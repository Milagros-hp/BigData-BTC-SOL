import copy
import time
import unittest
from .trades import from_aggtrade, validate_trade

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

if __name__ == "__main__":
    unittest.main()
