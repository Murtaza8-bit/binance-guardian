from __future__ import annotations

from flask import Flask, render_template, request

from guardian.config import load_guardian_policy
from guardian.mcp_server import guardian_review_trade

app = Flask(__name__)

DEFAULT_USER_POLICY = (
    "Never let me risk more than 15% on one asset, "
    "always keep at least 30% in USDT, "
    "and don't let me use more than 2x leverage."
)

DEMO_SCENARIOS = {
    "ALLOW": {
        "request_text": "Buy $50 of BTC",
        "mode_label": "DEMO / TEST DATA",
        "source": "Controlled demo data",
        "portfolio": {
            "total_value_usdt": 500.0,
            "usdt_balance": 350.0,
            "current_asset_value_usdt": 0.0,
            "daily_pnl_pct": -1.0,
            "asset_values": {"BTC": 0.0},
        },
        "market_prices": {"BTC": 50000.0},
        "portfolio_snapshot": None,
        "scenario": "ALLOW",
    },
    "RESIZE": {
        "request_text": "Buy $300 of SOL",
        "mode_label": "DEMO / TEST DATA",
        "source": "Controlled demo data",
        "portfolio": {
            "total_value_usdt": 500.0,
            "usdt_balance": 350.0,
            "current_asset_value_usdt": 50.0,
            "daily_pnl_pct": -1.0,
            "asset_values": {"SOL": 50.0},
        },
        "market_prices": {"SOL": 106.30},
        "portfolio_snapshot": None,
        "scenario": "RESIZE",
    },
    "BLOCK": {
        "request_text": "Buy $50 of BTC using 10x leverage",
        "mode_label": "DEMO / TEST DATA",
        "source": "Controlled demo data",
        "portfolio": {
            "total_value_usdt": 500.0,
            "usdt_balance": 350.0,
            "current_asset_value_usdt": 50.0,
            "daily_pnl_pct": -1.0,
            "asset_values": {"BTC": 50.0},
        },
        "market_prices": {"BTC": 50000.0},
        "portfolio_snapshot": None,
        "scenario": "BLOCK",
    },
}


def get_agent_os_dashboard_snapshot():
    """Return the non-live dashboard placeholder for Agent OS orchestration."""
    return {
        "mode_label": "AGENT OS ORCHESTRATION / NO LIVE DATA",
        "source": "Dashboard demo path; Binance Agent OS MCP data is external",
        "portfolio": {
            "total_value_usdt": 0.0,
            "usdt_balance": 0.0,
            "current_asset_value_usdt": 0.0,
            "daily_pnl_pct": 0.0,
            "asset_values": {},
        },
        "market_prices": {},
        "portfolio_snapshot": None,
        "scenario": "AGENT_OS_DEMO",
    }


def get_demo_snapshot(scenario_name: str = "ALLOW"):
    """Return a clearly labeled demo portfolio for controlled testing."""
    return DEMO_SCENARIOS.get(scenario_name.upper(), DEMO_SCENARIOS["ALLOW"]).copy()


def run_guardian_review(request_text: str, mode: str, scenario_name: str = "ALLOW"):
    """Run Guardian via the existing safety layer without permitting execution."""
    policy = load_guardian_policy(DEFAULT_USER_POLICY)
    snapshot = (
        get_agent_os_dashboard_snapshot()
        if mode in {"live", "agent_os_demo"}
        else get_demo_snapshot(scenario_name)
    )

    if mode in {"live", "agent_os_demo"}:
        total_value_usdt = snapshot["portfolio"]["total_value_usdt"]
        usdt_balance = snapshot["portfolio"]["usdt_balance"]
        current_asset_value_usdt = snapshot["portfolio"]["current_asset_value_usdt"]
        portfolio_snapshot = snapshot["portfolio_snapshot"]
        market_prices = snapshot["market_prices"]
        daily_pnl_pct = snapshot["portfolio"]["daily_pnl_pct"]
    else:
        total_value_usdt = snapshot["portfolio"]["total_value_usdt"]
        usdt_balance = snapshot["portfolio"]["usdt_balance"]
        current_asset_value_usdt = snapshot["portfolio"]["current_asset_value_usdt"]
        portfolio_snapshot = None
        market_prices = snapshot["market_prices"]
        daily_pnl_pct = snapshot["portfolio"]["daily_pnl_pct"]

    result = guardian_review_trade(
        user_request=request_text,
        total_value_usdt=total_value_usdt,
        usdt_balance=usdt_balance,
        current_asset_value_usdt=current_asset_value_usdt,
        daily_pnl_pct=daily_pnl_pct,
        user_policy=DEFAULT_USER_POLICY,
        portfolio_snapshot=portfolio_snapshot,
        market_prices=market_prices,
    )

    result["source_label"] = snapshot["mode_label"]
    result["data_source"] = snapshot["source"]
    result["portfolio_snapshot"] = snapshot["portfolio"]
    result["market_price_usdt"] = snapshot["market_prices"].get("SOL", snapshot["market_prices"].get("BTC", 0.0))
    result["policy"] = policy
    result["scenario"] = snapshot.get("scenario", scenario_name.upper())
    return result


@app.route("/", methods=["GET", "POST"])
def dashboard():
    request_text = "Buy $300 of SOL"
    mode = "live"
    scenario_name = "AGENT_OS_DEMO"

    if request.method == "POST":
        request_text = request.form.get("request", request_text)
        scenario_name = request.form.get("scenario", scenario_name).upper()
        mode = "agent_os_demo" if scenario_name in {"LIVE", "AGENT_OS_DEMO"} else "demo"

    if mode == "demo":
        demo_snapshot = get_demo_snapshot(scenario_name)
        request_text = demo_snapshot["request_text"]

    result = run_guardian_review(request_text, mode, scenario_name)
    return render_template(
        "index.html",
        request_text=request_text,
        mode=mode,
        scenario_name=result.get("scenario", scenario_name.upper()),
        result=result,
        risk_checks=result.get("risk_checks", []),
        mode_label=result["source_label"],
        data_source=result["data_source"],
        portfolio=result["portfolio_snapshot"],
        current_price=result["market_price_usdt"],
        policy_summary=(
            "Bound by max_trade_usdt=$100, max_asset_exposure_pct=15%, "
            "max_daily_loss_pct=3%, max_leverage=2x, minimum_usdt_reserve_pct=30%."
        ),
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)