import unittest

from guardian.intent import parse_trade_intent


class ParseTradeIntentTests(unittest.TestCase):
    def test_buy_dollar_amount_of_sol(self):
        trade = parse_trade_intent("Buy $300 of SOL")
        self.assertEqual(trade.symbol, "SOLUSDT")
        self.assertEqual(trade.side, "BUY")
        self.assertEqual(trade.amount_usdt, 300.0)
        self.assertEqual(trade.leverage, 1)


if __name__ == "__main__":
    unittest.main()
