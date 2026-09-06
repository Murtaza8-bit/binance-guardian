import unittest

from binance.account import (
    build_portfolio_from_balances,
    get_requested_asset_value_usdt,
)
from guardian.mcp_server import guardian_review_trade as mcp_guardian_review_trade


def guardian_review_trade(*args, **kwargs):
    kwargs.setdefault("daily_pnl_pct", 0.0)
    return mcp_guardian_review_trade(*args, **kwargs)


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

        self.assertEqual(portfolio.usdt_balance, 350.00)
        self.assertEqual(portfolio.total_value_usdt, 375.00)

    def test_locked_usdt_is_not_spendable_for_buy(self):
        result = guardian_review_trade(
            user_request="Buy $50 BTC",
            portfolio_snapshot={
                "balances": [
                    {"asset": "USDT", "free": "0", "locked": "10000"},
                ]
            },
            market_prices={"BTC": 50000.00},
        )

        self.assertEqual(result["decision"], "BLOCK")
        self.assertIn("Insufficient USDT balance", result["reasons"][0])

    def test_locked_usdt_does_not_increase_buy_funding(self):
        result = guardian_review_trade(
            user_request="Buy $50 BTC",
            portfolio_snapshot={
                "balances": [
                    {"asset": "USDT", "free": "100", "locked": "10000"},
                ]
            },
            market_prices={"BTC": 50000.00},
        )

        self.assertEqual(result["decision"], "BLOCK")
        self.assertEqual(result["audit_record"]["portfolio_snapshot"]["usdt_balance"], 100.00)

    def test_locked_asset_is_not_sellable(self):
        result = guardian_review_trade(
            user_request="Sell $50 BTC",
            portfolio_snapshot={
                "balances": [
                    {"asset": "USDT", "free": "10000", "locked": "0"},
                    {"asset": "BTC", "free": "0", "locked": "1"},
                ]
            },
            market_prices={"BTC": 100.00},
        )

        self.assertEqual(result["decision"], "BLOCK")
        self.assertIn("Insufficient asset balance", result["reasons"][0])

    def test_sell_uses_free_asset_value_only(self):
        result = guardian_review_trade(
            user_request="Sell $50 BTC",
            portfolio_snapshot={
                "balances": [
                    {"asset": "USDT", "free": "10000", "locked": "0"},
                    {"asset": "BTC", "free": "1", "locked": "1"},
                ]
            },
            market_prices={"BTC": 100.00},
        )

        self.assertEqual(result["decision"], "ALLOW")
        snapshot = result["audit_record"]["portfolio_snapshot"]
        self.assertEqual(snapshot["asset_values"]["BTC"], 200.00)
        self.assertEqual(snapshot["available_asset_values"]["BTC"], 100.00)

    def test_missing_price_does_not_crash(self):
        portfolio = build_portfolio_from_balances(
            [{"asset": "SOL", "free": "10", "locked": "0"}],
            {},
        )

        self.assertEqual(portfolio.asset_values["SOL"], 0.00)
        self.assertEqual(portfolio.total_value_usdt, 0.00)
        self.assertFalse(portfolio.valuation_complete)
        self.assertEqual(portfolio.missing_market_prices, ["SOL"])

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

    def test_missing_market_price_blocks_asset_exposure_evaluation(self):
        result = guardian_review_trade(
            user_request="Buy $50 SOL",
            portfolio_snapshot={
                "balances": [
                    {"asset": "USDT", "free": "10000", "locked": "0"},
                    {"asset": "SOL", "free": "10", "locked": "0"},
                ]
            },
            market_prices={},
        )

        self.assertEqual(result["decision"], "BLOCK")
        self.assertIn("Missing market price for SOL", result["reasons"][0])
        self.assertFalse(result["audit_record"]["portfolio_snapshot"]["valuation_complete"])
        self.assertEqual(
            result["audit_record"]["portfolio_snapshot"]["missing_market_prices"],
            ["SOL"],
        )

    def test_valid_market_price_preserves_asset_evaluation(self):
        result = guardian_review_trade(
            user_request="Buy $50 SOL",
            portfolio_snapshot={
                "balances": [
                    {"asset": "USDT", "free": "10000", "locked": "0"},
                    {"asset": "SOL", "free": "10", "locked": "0"},
                ]
            },
            market_prices={"SOL": 106.30},
        )

        self.assertEqual(result["decision"], "ALLOW")
        self.assertEqual(
            result["audit_record"]["portfolio_snapshot"]["current_asset_value_usdt"],
            1063.00,
        )

    def test_usdt_only_portfolio_does_not_require_market_price(self):
        result = guardian_review_trade(
            user_request="Buy $50 BTC",
            portfolio_snapshot={
                "balances": [
                    {"asset": "USDT", "free": "10000", "locked": "0"},
                ]
            },
            market_prices={},
        )

        self.assertEqual(result["decision"], "ALLOW")
        self.assertTrue(result["audit_record"]["portfolio_snapshot"]["valuation_complete"])
        self.assertEqual(
            result["audit_record"]["portfolio_snapshot"]["missing_market_prices"],
            [],
        )

    def test_missing_daily_pnl_blocks_live_snapshot_review(self):
        result = mcp_guardian_review_trade(
            user_request="Buy $50 BTC",
            portfolio_snapshot={
                "balances": [
                    {"asset": "USDT", "free": "10000", "locked": "0"},
                ]
            },
            market_prices={"BTC": 50000.00},
        )

        self.assertEqual(result["decision"], "BLOCK")
        self.assertIn("Daily P&L data unavailable", result["reasons"][0])

    def test_explicit_zero_daily_pnl_continues_evaluation(self):
        result = guardian_review_trade(
            user_request="Buy $50 BTC",
            portfolio_snapshot={
                "balances": [
                    {"asset": "USDT", "free": "10000", "locked": "0"},
                ]
            },
            market_prices={"BTC": 50000.00},
            daily_pnl_pct=0.0,
        )

        self.assertEqual(result["decision"], "ALLOW")

    def test_daily_pnl_within_limit_preserves_evaluation(self):
        result = guardian_review_trade(
            user_request="Buy $50 BTC",
            portfolio_snapshot={
                "balances": [
                    {"asset": "USDT", "free": "10000", "locked": "0"},
                ]
            },
            market_prices={"BTC": 50000.00},
            daily_pnl_pct=-1.0,
        )

        self.assertEqual(result["decision"], "ALLOW")

    def test_daily_pnl_beyond_limit_preserves_block(self):
        result = guardian_review_trade(
            user_request="Buy $50 BTC",
            portfolio_snapshot={
                "balances": [
                    {"asset": "USDT", "free": "10000", "locked": "0"},
                ]
            },
            market_prices={"BTC": 50000.00},
            daily_pnl_pct=-4.0,
        )

        self.assertEqual(result["decision"], "BLOCK")
        self.assertIn("Daily loss limit", result["reasons"][0])

    def test_guardian_detects_asset_before_leverage_suffix(self):
        result = guardian_review_trade(
            user_request="Buy $300 of SOL using 10x leverage",
            portfolio_snapshot={
                "balances": [
                    {"asset": "USDT", "free": "10000", "locked": "0"},
                    {"asset": "SOL", "free": "10", "locked": "0"},
                ]
            },
            market_prices={"SOL": 106.30},
        )

        self.assertEqual(result["decision"], "BLOCK")
        self.assertEqual(result["trade"]["symbol"], "SOLUSDT")
        self.assertEqual(
            result["audit_record"]["portfolio_snapshot"]["current_asset_value_usdt"],
            1063.00,
        )

    def test_guardian_detects_assets_with_trailing_request_words(self):
        cases = [
            ("Buy $300 of SOL using 10x leverage", "SOL", 106.30, "BLOCK"),
            ("Buy $300 BTC with 2x leverage", "BTC", 50000.00, "BLOCK"),
            ("Buy $300 of ETH using 2x leverage", "ETH", 2500.00, "BLOCK"),
        ]

        for request, asset, price, expected_decision in cases:
            with self.subTest(asset=asset):
                result = guardian_review_trade(
                    user_request=request,
                    portfolio_snapshot={
                        "balances": [
                            {"asset": "USDT", "free": "10000", "locked": "0"},
                            {"asset": asset, "free": "10", "locked": "0"},
                        ]
                    },
                    market_prices={asset: price},
                )

                self.assertEqual(result["decision"], expected_decision)
                self.assertEqual(result["trade"]["symbol"], f"{asset}USDT")
                self.assertEqual(
                    result["audit_record"]["portfolio_snapshot"]["current_asset_value_usdt"],
                    10 * price,
                )

    def test_sell_blocks_when_asset_holdings_are_insufficient(self):
        result = guardian_review_trade(
            user_request="Sell $50 BTC",
            portfolio_snapshot={
                "balances": [
                    {"asset": "USDT", "free": "10000", "locked": "0"},
                ]
            },
            market_prices={"BTC": 100.00},
        )

        self.assertEqual(result["decision"], "BLOCK")
        self.assertIn("Insufficient asset balance", result["reasons"][0])
        self.assertEqual(result["trade"]["approved_amount_usdt"], 0)

    def test_sell_within_asset_holdings_continues_policy_evaluation(self):
        result = guardian_review_trade(
            user_request="Sell $50 BTC",
            portfolio_snapshot={
                "balances": [
                    {"asset": "USDT", "free": "10000", "locked": "0"},
                    {"asset": "BTC", "free": "1", "locked": "0"},
                ]
            },
            market_prices={"BTC": 100.00},
        )

        self.assertEqual(result["decision"], "ALLOW")
        self.assertEqual(result["trade"]["approved_amount_usdt"], 50)

    def test_sell_full_asset_holdings_is_allowed_by_holdings_check(self):
        result = guardian_review_trade(
            user_request="Sell $100 BTC",
            portfolio_snapshot={
                "balances": [
                    {"asset": "USDT", "free": "10000", "locked": "0"},
                    {"asset": "BTC", "free": "1", "locked": "0"},
                ]
            },
            market_prices={"BTC": 100.00},
        )

        self.assertEqual(result["decision"], "ALLOW")
        self.assertEqual(result["trade"]["approved_amount_usdt"], 100)

    def test_confirmation_requirement_is_exposed_without_execution(self):
        result = guardian_review_trade(
            user_request="Buy $50 BTC",
            portfolio_snapshot={
                "balances": [
                    {"asset": "USDT", "free": "10000", "locked": "0"},
                ]
            },
            market_prices={"BTC": 50000.00},
        )

        self.assertEqual(result["decision"], "ALLOW")
        self.assertTrue(result["confirmation_required"])
        self.assertTrue(result["audit_record"]["decision"]["confirmation_required"])
        self.assertFalse(result["execution"]["order_placed"])
        self.assertFalse(result["execution"]["execution_authorized"])


if __name__ == "__main__":
    unittest.main()
