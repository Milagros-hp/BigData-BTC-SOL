"""S06: eventos empresariales. Cada operacion ejecutada en Binance (aggTrade) se publica en Kafka.

Las velas (producer.py) son la telemetria por minuto del mercado; las operaciones son
transacciones de negocio individuales: quien compro o vendio, cuanto y a que precio.
"""
import json
import os
import signal
import time
import traceback
from decimal import Decimal, InvalidOperation
import requests
import websocket
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
from .contract import SYMBOLS
from .core import STATE, save_json

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "kafka:9092")
TOPICS = {s: "market.trades." + s.lower() for s in SYMBOLS}
WS = "wss://data-stream.binance.vision/stream?streams=btcusdt@aggTrade/solusdt@aggTrade"
REST = "https://data-api.binance.vision"
MAX_BACKFILL_PAGES = 120
EVENT_TYPE = "market.trade.executed"
running = True

def validate_trade(event):
    if not isinstance(event, dict):
        raise ValueError("event_must_be_object")
    if event.get("schema_version") != 1 or event.get("event_type") != EVENT_TYPE:
        raise ValueError("unsupported_contract")
    if event.get("symbol") not in SYMBOLS or event.get("side") not in ("buy", "sell"):
        raise ValueError("symbol_or_side")
    if event.get("source") != "binance_spot" or event.get("synthetic") is not False:
        raise ValueError("untrusted_source")
    trade_id, trade_ms = event.get("trade_id"), event.get("trade_ms")
    if type(trade_id) is not int or trade_id < 0 or type(trade_ms) is not int or trade_ms <= 0:
        raise ValueError("invalid_trade_id_or_time")
    if trade_ms > int(time.time() * 1000) + 10000:
        raise ValueError("future_trade")
    try:
        price, quantity, quote = (Decimal(str(event[k])) for k in ("price", "quantity", "quote_usdt"))
    except (InvalidOperation, KeyError, TypeError) as error:
        raise ValueError("invalid_decimal") from error
    if not (price > 0 and quantity > 0 and quote > 0):
        raise ValueError("non_positive_trade")
    if event.get("event_id") != f"{event['symbol']}:trade:{trade_id}":
        raise ValueError("invalid_event_id")
    return event

def from_aggtrade(message, published_ms=None, transport="websocket"):
    payload = message.get("data", message)
    if payload.get("e") != "aggTrade":
        return None
    price, quantity = Decimal(payload["p"]), Decimal(payload["q"])
    # m=True: el comprador fue el creador de la orden, la operacion la inicio un vendedor.
    event = {"schema_version": 1, "event_type": EVENT_TYPE, "event_id": f"{payload['s']}:trade:{int(payload['a'])}",
        "symbol": payload["s"], "trade_id": int(payload["a"]), "trade_ms": int(payload["T"]),
        "price": str(price), "quantity": str(quantity), "quote_usdt": str((price * quantity).quantize(Decimal("0.00000001"))),
        "side": "sell" if payload["m"] else "buy", "source": "binance_spot", "transport": transport,
        "published_ms": published_ms or int(time.time() * 1000), "synthetic": False}
    return validate_trade(event)

def from_rest(symbol, row, published_ms=None):
    """Una fila de /api/v3/aggTrades lleva los mismos campos que el mensaje WebSocket."""
    return from_aggtrade({"e": "aggTrade", "s": symbol, "a": row["a"], "p": row["p"], "q": row["q"],
        "T": row["T"], "m": row["m"]}, published_ms, transport="rest")

def missing_trades(session, last_ids):
    """Operaciones ausentes tras una caida, en orden de tiempo.

    Se ordenan entre activos porque el watermark de Spark es global: publicar primero un
    activo completo convertiria en tardias las operaciones del otro.
    """
    events = []
    for symbol, last_id in last_ids.items():
        for _ in range(MAX_BACKFILL_PAGES):
            response = session.get(REST + "/api/v3/aggTrades",
                params={"symbol": symbol, "fromId": last_id + 1, "limit": 1000}, timeout=20)
            response.raise_for_status()
            rows = response.json()
            events.extend(from_rest(symbol, row) for row in rows)
            if len(rows) < 1000:
                break
            last_id = rows[-1]["a"]
    return sorted(events, key=lambda event: event["trade_ms"])

def stop(*_):
    global running
    running = False

def read_status():
    try:
        return json.loads((STATE / "trades_status.json").read_text())
    except (OSError, ValueError):
        return {}

def ensure_topics():
    admin = KafkaAdminClient(bootstrap_servers=BOOTSTRAP, client_id="cryptopulse-trades-admin")
    present = set(admin.list_topics())
    missing = [NewTopic(name, num_partitions=3, replication_factor=1) for name in TOPICS.values() if name not in present]
    if missing:
        try:
            admin.create_topics(missing)
        except TopicAlreadyExistsError:
            pass
    admin.close()

def run():
    signal.signal(signal.SIGTERM, stop)
    ensure_topics()
    producer = KafkaProducer(bootstrap_servers=BOOTSTRAP, acks="all", retries=10, linger_ms=50,
        key_serializer=lambda s: s.encode(), value_serializer=lambda value: json.dumps(value).encode(),
        client_id="cryptopulse-trades", enable_idempotence=True)
    previous = read_status()
    info = {"connected": False, "published": previous.get("published", 0), "rejected": 0, "recovered": previous.get("recovered", 0),
        "last_trade_ms": previous.get("last_trade_ms"), "heartbeat_ms": None, "last_ids": previous.get("last_ids", {})}
    def publish(event):
        producer.send(TOPICS[event["symbol"]], key=event["symbol"], value=event)
        info["published"] += 1
        info["last_trade_ms"] = event["trade_ms"]
        info["last_ids"][event["symbol"]] = event["trade_id"]
    session = requests.Session()
    backoff = 1
    while running:
        connection = None
        try:
            connection = websocket.create_connection(WS, timeout=5)
            # El socket ya acumula lo nuevo: se recupera el hueco y luego se ignora lo repetido.
            recovered = missing_trades(session, info["last_ids"])
            for event in recovered:
                publish(event)
            producer.flush(30)
            info["recovered"] += len(recovered)
            info["connected"] = True
            backoff = 1
            next_heartbeat = 0
            while running:
                try:
                    event = from_aggtrade(json.loads(connection.recv()))
                    if event is not None and event["trade_id"] > info["last_ids"].get(event["symbol"], -1):
                        publish(event)
                except websocket.WebSocketTimeoutException:
                    pass
                except (ValueError, KeyError, TypeError, ArithmeticError) as error:
                    info["rejected"] += 1
                    print("Operacion rechazada:", repr(error), flush=True)
                if time.monotonic() >= next_heartbeat:
                    info["heartbeat_ms"] = int(time.time() * 1000)
                    save_json(STATE / "trades_status.json", info)
                    next_heartbeat = time.monotonic() + 10
        except Exception:
            info["connected"] = False
            save_json(STATE / "trades_status.json", info)
            traceback.print_exc()
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)
        finally:
            if connection:
                connection.close()
    producer.flush(10)
    info["connected"] = False
    save_json(STATE / "trades_status.json", info)
    producer.close()

if __name__ == "__main__":
    run()
