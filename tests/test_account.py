import unittest

from binance.account import (
    build_portfolio_from_balances,
    get_requested_asset_value_usdt,
)
from guardian.mcp_server import guardian_review_trade


class BinanceAccountTests(unittest.TestCase):
    def test_asset_balance_is_stored_as_usdt_value(self):
        portfolio = build_portfolio_from_balances(
            [{"asset": "SOL", "free": "10", "locked": "0"}],
            {"SOL": 106.30},
        )

        self.assertEqual(portfolio.asset_values["SOL"], 1063.00)
        self.assertEqual(portfolio.total_value_usdt, 1063.00)
        self.assertEqual(get_requested_asset_value_usdt("SOL", portfolio), 1063.00)

    def test_free_and_locked_balances_are_combined(self):
        portfolio = build_portfolio_from_balances(
            [{"asset": "SOL", "free": "4", "locked": "6"}],
            {"SOL": 106.30},
        )

        self.assertEqual(portfolio.asset_values["SOL"], 1063.00)
        self.assertEqual(portfolio.total_value_usdt, 1063.00)

    def test_usdt_balance_remains_correct(self):
        portfolio = build_portfolio_from_balances(
            [{"asset": "USDT", "free": "350.00", "locked": "25.00"}],
            {"USDT": 1.0},
        )

        self.assertEqual(portfolio.usdt_balance, 375.00)
        self.assertEqual(portfolio.total_value_usdt, 375.00)

    def test_missing_price_does_not_crash(self):
        portfolio = build_portfolio_from_balances(
            [{"asset": "SOL", "free": "10", "locked": "0"}],
            {},
        )

        self.assertEqual(portfolio.asset_values["SOL"], 0.00)
        self.assertEqual(portfolio.total_value_usdt, 0.00)

    def test_guardian_exposure_uses_usdt_asset_value(self):
        result = guardian_review_trade(
            user_request="Buy $50 of SOL",
            portfolio_snapshot={
                "balances": [
                    {"asset": "USDT", "free": "10000", "locked": "0"},
                    {"asset": "SOL", "free": "10", "locked": "0"},
                ]
            },
            market_prices={"SOL": 106.30},
            user_policy=(
                "maximum trade to $2000, maximum 10% on a single asset, "
                "keep at least 0% in USDT, maximum 3x leverage"
            ),
        )

        self.assertEqual(result["decision"], "RESIZE")
        self.assertEqual(result["trade"]["approved_amount_usdt"], 43.3)
        exposure_check = next(
            check for check in result["risk_checks"]
            if check["check"] == "Single-asset exposure"
        )
        self.assertEqual(exposure_check["status"], "FAIL")
        self.assertIn("$1063.00 existing", exposure_check["actual"])


if __name__ == "__main__":
    unittest.main()
