import unittest

from guardian.intent import parse_trade_intent


class ParseTradeIntentTests(unittest.TestCase):
    def test_buy_dollar_amount_of_sol(self):
        trade = parse_trade_intent("Buy $300 of SOL")
        self.assertEqual(trade.symbol, "SOLUSDT")
        self.assertEqual(trade.side, "BUY")
        self.assertEqual(trade.amount_usdt, 300.0)
        self.assertEqual(trade.leverage, 1)

    def test_leverage_number_is_not_used_as_trade_amount(self):
        with self.assertRaisesRegex(ValueError, "Could not determine the trade amount"):
            parse_trade_intent("Buy BTC using 10x leverage")

    def test_dollar_amount_with_leverage(self):
        trade = parse_trade_intent("Buy $300 BTC using 10x leverage")
        self.assertEqual(trade.amount_usdt, 300.0)
        self.assertEqual(trade.symbol, "BTCUSDT")
        self.assertEqual(trade.leverage, 10)

    def test_usdt_amount_of_asset(self):
        trade = parse_trade_intent("Buy 300 USDT of BTC")
        self.assertEqual(trade.amount_usdt, 300.0)
        self.assertEqual(trade.symbol, "BTCUSDT")

    def test_asset_for_dollar_amount(self):
        trade = parse_trade_intent("Buy BTC for $300")
        self.assertEqual(trade.amount_usdt, 300.0)
        self.assertEqual(trade.symbol, "BTCUSDT")


if __name__ == "__main__":
    unittest.main()
