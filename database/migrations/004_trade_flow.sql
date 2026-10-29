-- S06: eventos empresariales (operaciones ejecutadas) agregados por minuto en Spark.
CREATE TABLE IF NOT EXISTS trade_flow(
 symbol text NOT NULL, window_start timestamptz NOT NULL, window_end timestamptz NOT NULL,
 trades bigint NOT NULL, buy_usdt double precision NOT NULL, sell_usdt double precision NOT NULL,
 max_trade_usdt double precision NOT NULL, large_trades integer NOT NULL,
 updated_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(symbol,window_start));
GRANT SELECT ON trade_flow TO grafana_reader;
