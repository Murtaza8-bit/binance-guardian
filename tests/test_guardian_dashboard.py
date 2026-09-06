import unittest
import unittest

from app import app, run_guardian_review


class GuardianDashboardTests(unittest.TestCase):
    def test_live_empty_account_blocks(self):
        result = run_guardian_review("Buy $300 of SOL", "live")
        self.assertEqual(result["decision"], "BLOCK")
        self.assertEqual(result["trade"]["approved_amount_usdt"], 0)
        self.assertIn("Insufficient USDT balance", result["reasons"][0])
        self.assertFalse(result["execution"]["order_placed"])
        self.assertFalse(result["execution"]["execution_authorized"])
        self.assertIn("risk_checks", result)
        self.assertIn("audit_record", result)

    def test_demo_allow_scenario(self):
        result = run_guardian_review("Buy $50 of BTC", "demo", "ALLOW")
        self.assertEqual(result["decision"], "ALLOW")
        self.assertEqual(result["trade"]["approved_amount_usdt"], 50)
        self.assertTrue(result["risk_checks"])
        self.assertIn("audit_record", result)
        self.assertFalse(result["execution"]["order_placed"])
        self.assertFalse(result["execution"]["execution_authorized"])

    def test_demo_resize_scenario(self):
        result = run_guardian_review("Buy $300 of SOL", "demo", "RESIZE")
        self.assertEqual(result["decision"], "RESIZE")
        self.assertEqual(result["trade"]["approved_amount_usdt"], 25)
        self.assertTrue(result["risk_checks"])
        self.assertIn("audit_record", result)
        self.assertFalse(result["execution"]["order_placed"])
        self.assertFalse(result["execution"]["execution_authorized"])

    def test_demo_block_scenario(self):
        result = run_guardian_review("Buy $50 of BTC using 10x leverage", "demo", "BLOCK")
        self.assertEqual(result["decision"], "BLOCK")
        self.assertEqual(result["trade"]["approved_amount_usdt"], 0)
        self.assertTrue(result["risk_checks"])
        self.assertIn("audit_record", result)
        self.assertFalse(result["execution"]["order_placed"])
        self.assertFalse(result["execution"]["execution_authorized"])

    def test_dashboard_live_mode_uses_guardian_decision(self):
        client = app.test_client()
        response = client.post("/", data={"scenario": "LIVE", "request": "Buy $300 of SOL"})
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("BINANCE GUARDIAN", html)
        self.assertIn("READ-ONLY", html)
        self.assertIn("BLOCK", html)
        self.assertIn("$0.00", html)
        self.assertIn("BINANCE AGENT OS", html)

    def test_scenario_selector_contains_all_options(self):
        client = app.test_client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        # Ensure the UI separates Agent OS orchestration from dashboard demo data.
        self.assertIn('🔵 AGENT OS ORCHESTRATION — NO LIVE DATA', html)
        self.assertIn('🟢 DEMO — ALLOW', html)
        self.assertIn('🟡 DEMO — RESIZE', html)
        self.assertIn('🔴 DEMO — BLOCK', html)

    def test_dashboard_scenarios_render_expected_results(self):
        client = app.test_client()
        scenarios = [
            ("ALLOW", "Buy $50 of BTC", "ALLOW", "$50.00"),
            ("RESIZE", "Buy $300 of SOL", "RESIZE", "$25.00"),
            ("BLOCK", "Buy $50 of BTC using 10x leverage", "BLOCK", "$0.00"),
        ]
        for scenario, request_text, expected_decision, expected_amount in scenarios:
            with self.subTest(scenario=scenario):
                response = client.post("/", data={"scenario": scenario, "request": request_text})
                self.assertEqual(response.status_code, 200)
                html = response.get_data(as_text=True)
                self.assertIn(expected_decision, html)
                self.assertIn(expected_amount, html)
                self.assertIn("DEMO / TEST DATA", html)


if __name__ == "__main__":
    unittest.main()

