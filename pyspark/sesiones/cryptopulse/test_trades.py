import copy
import time
import unittest
from .trades import from_aggtrade, from_rest, missing_trades, validate_trade

def message(maker=False, **overrides):
    payload = {"e": "aggTrade", "s": "BTCUSDT", "a": 123456, "p": "81596.12000000", "q": "0.01500000",
               "T": int(time.time() * 1000) - 1000, "m": maker}
    payload.update(overrides)
    return {"stream": "btcusdt@aggTrade", "data": payload}

class TradeContractTest(unittest.TestCase):
    def test_buyer_initiated_trade(self):
        event = from_aggtrade(message(maker=False), published_ms=1)
        self.assertEqual(event["side"], "buy")
        self.assertEqual(event["event_id"], "BTCUSDT:trade:123456")
        self.assertEqual(event["quote_usdt"], "1223.94180000")

    def test_maker_buyer_means_seller_initiated(self):
        self.assertEqual(from_aggtrade(message(maker=True))["side"], "sell")

    def test_other_streams_are_ignored(self):
        self.assertIsNone(from_aggtrade({"data": {"e": "kline"}}))

    def test_rejects_invalid_events(self):
        event = from_aggtrade(message())
        for key, value in [("symbol", "ETHUSDT"), ("side", "hold"), ("price", "0"), ("synthetic", True),
                           ("event_id", "BTCUSDT:trade:1"), ("trade_ms", int(time.time() * 1000) + 60000)]:
            broken = copy.deepcopy(event)
            broken[key] = value
            with self.assertRaises(ValueError, msg=key):
                validate_trade(broken)

class FakeResponse:
    def __init__(self, rows):
        self.rows = rows
    def raise_for_status(self):
        pass
    def json(self):
        return self.rows

class FakeSession:
    def __init__(self, pages):
        self.pages = pages
        self.requested = []
    def get(self, url, params, timeout):
        self.requested.append((params["symbol"], params["fromId"]))
        return FakeResponse(self.pages[params["symbol"]].pop(0))

def row(trade_id, trade_ms):
    return {"a": trade_id, "p": "10.00000000", "q": "2.00000000", "T": trade_ms, "m": False}

class TradeRecoveryTest(unittest.TestCase):
    def test_rest_row_uses_same_contract(self):
        event = from_rest("SOLUSDT", row(7, int(time.time() * 1000) - 1000))
        self.assertEqual((event["transport"], event["event_id"], event["quote_usdt"]), ("rest", "SOLUSDT:trade:7", "20.00000000"))

    def test_gap_is_merged_by_event_time_between_assets(self):
        now = int(time.time() * 1000)
        session = FakeSession({"BTCUSDT": [[row(11, now - 1000)]], "SOLUSDT": [[row(21, now - 5000)]]})
        events = missing_trades(session, {"BTCUSDT": 10, "SOLUSDT": 20})
        self.assertEqual([e["symbol"] for e in events], ["SOLUSDT", "BTCUSDT"])
        self.assertEqual(session.requested, [("BTCUSDT", 11), ("SOLUSDT", 21)])

    def test_full_pages_continue_from_last_id(self):
        now = int(time.time() * 1000)
        session = FakeSession({"BTCUSDT": [[row(i, now - 2000) for i in range(11, 1011)], [row(1011, now - 1000)]]})
        self.assertEqual(len(missing_trades(session, {"BTCUSDT": 10})), 1001)
        self.assertEqual(session.requested[1], ("BTCUSDT", 1011))

    def test_nothing_to_recover_on_first_start(self):
        self.assertEqual(missing_trades(FakeSession({}), {}), [])

if __name__ == "__main__":
    unittest.main()
