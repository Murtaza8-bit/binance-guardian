import unittest

from app import DEFAULT_USER_POLICY
from guardian.config import load_guardian_policy
from guardian.policy_compiler import PolicyCompilationError, compile_policy


class PolicyCompilerTests(unittest.TestCase):
    def test_supported_policy_compiles_as_before(self):
        policy = compile_policy(
            "Never let me risk more than 15% on one asset, "
            "always keep at least 30% in USDT, "
            "and don't let me use more than 2x leverage."
        )

        self.assertEqual(
            policy,
            {
                "max_asset_exposure_pct": 15.0,
                "minimum_usdt_reserve_pct": 30.0,
                "max_leverage": 2.0,
            },
        )

    def test_supported_trade_and_daily_loss_policy_compiles(self):
        policy = compile_policy(
            "Limit each trade to $200 and set a daily loss limit of 5%."
        )

        self.assertEqual(policy["max_trade_usdt"], 200.0)
        self.assertEqual(policy["max_daily_loss_pct"], 5.0)

    def test_unsupported_policy_wording_raises(self):
        with self.assertRaisesRegex(PolicyCompilationError, "minimum USDT reserve"):
            compile_policy("Keep at least 80 percent in USDT")

    def test_non_policy_text_remains_uncompiled(self):
        self.assertEqual(compile_policy("I prefer conservative decisions."), {})

    def test_config_preserves_defaults_when_supported_policy_compiles(self):
        policy = load_guardian_policy("maximum trade to $200")

        self.assertEqual(policy["max_trade_usdt"], 200.0)
        self.assertEqual(policy["max_asset_exposure_pct"], 15)
        self.assertEqual(policy["max_daily_loss_pct"], 3)
        self.assertEqual(policy["max_leverage"], 2)
        self.assertEqual(policy["minimum_usdt_reserve_pct"], 30)
        self.assertTrue(policy["require_confirmation"])

    def test_config_defaults_match_effective_guardian_defaults(self):
        configured = load_guardian_policy()
        effective = load_guardian_policy(DEFAULT_USER_POLICY)

        for key in (
            "max_asset_exposure_pct",
            "max_leverage",
            "minimum_usdt_reserve_pct",
        ):
            self.assertEqual(configured[key], effective[key])

    def test_unsupported_policy_does_not_fall_back_silently(self):
        with self.assertRaises(PolicyCompilationError):
            load_guardian_policy("Keep at least 80 percent in USDT")


if __name__ == "__main__":
    unittest.main()