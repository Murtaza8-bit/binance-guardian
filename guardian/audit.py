import json
from datetime import datetime, timezone


def create_audit_record(
    user_request: str,
    result: dict,
    policy: dict,
    portfolio: dict,
) -> dict:
    """
    Create a structured audit record for a Guardian decision.

    Guardian is a read-only safety layer.
    It never executes trades.
    """

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "guardian": "Binance Guardian",
        "mode": "READ_ONLY",

        "request": {
            "text": user_request,
            "symbol": result["symbol"],
            "side": result["side"],
            "requested_amount_usdt": result["requested_amount"],
            "leverage": result["leverage"],
        },

        "portfolio_snapshot": {
            "total_value_usdt": portfolio["total_value_usdt"],
            "usdt_balance": portfolio["usdt_balance"],
            "current_asset_value_usdt": portfolio[
                "current_asset_value_usdt"
            ],
            "daily_pnl_pct": portfolio["daily_pnl_pct"],
        },

        "policy": policy,

        "decision": {
            "status": result["status"],
            "approved_amount_usdt": result["approved_amount"],
            "reasons": result["reasons"],
            "risk_checks": result.get("risk_checks", []),
        },

        "execution": {
            "order_placed": False,
            "execution_authorized": False,
        },
    }


def audit_record_to_json(record: dict) -> str:
    """Convert an audit record to formatted JSON."""
    return json.dumps(record, indent=2)