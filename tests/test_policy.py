import unittest

from guardian.policy import PortfolioState, TradeIntent, evaluate_trade


class PolicyRoundingTests(unittest.TestCase):
    POLICY = {
        "max_trade_usdt": 100,
        "max_asset_exposure_pct": 15,
        "max_daily_loss_pct": 3,
        "max_leverage": 2,
        "minimum_usdt_reserve_pct": 30,
    }

    def test_tiny_positive_capacity_rounding_blocks(self):
        decision = evaluate_trade(
            TradeIntent("SOLUSDT", "BUY", 50),
            PortfolioState(
                total_value_usdt=1000,
                usdt_balance=1000,
                current_asset_value_usdt=149.996,
            ),
            self.POLICY,
        )

        self.assertEqual(decision.status, "BLOCK")
        self.assertEqual(decision.approved_amount, 0.00)

    def test_ordinary_sol_resize_remains_positive(self):
        decision = evaluate_trade(
            TradeIntent("SOLUSDT", "BUY", 300),
            PortfolioState(
                total_value_usdt=500,
                usdt_balance=350,
                current_asset_value_usdt=50,
            ),
            self.POLICY,
        )

        self.assertEqual(decision.status, "RESIZE")
        self.assertEqual(decision.approved_amount, 25.00)


if __name__ == "__main__":
    unittest.main()
