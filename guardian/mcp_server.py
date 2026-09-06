import json
import logging
import traceback

from mcp.server.mcpserver import MCPServer

from guardian.guardian_tool import review_trade
from guardian.config import load_guardian_policy
from guardian.audit import create_audit_record
from binance.account import build_portfolio_snapshot_from_agent_os, get_requested_asset_value_usdt

logger = logging.getLogger(__name__)


server = MCPServer("Binance Guardian")


DEFAULT_USER_POLICY = (
    "Never let me risk more than 15% on one asset, "
    "always keep at least 30% in USDT, "
    "and don't let me use more than 2x leverage."
)


def guardian_review_trade(
    user_request: str,
    total_value_usdt: float = None,
    usdt_balance: float = None,
    current_asset_value_usdt: float = None,
    daily_pnl_pct: float = 0.0,
    user_policy: str = DEFAULT_USER_POLICY,
    portfolio_snapshot: dict = None,
    market_prices: dict = None,
):
    """
    Review a natural-language trading request against
    Guardian's deterministic risk policies.

    READ-ONLY SAFETY GATE.

    This tool NEVER places, cancels, or modifies orders.
    """

    try:
        # Load and compile the user's policy
        policy = load_guardian_policy(user_policy)

        # Allow optional live Binance Agent OS portfolio snapshots to populate the
        # portfolio fields used by Guardian without altering the existing policy engine.
        if portfolio_snapshot is not None:
            live_portfolio = build_portfolio_snapshot_from_agent_os(
                portfolio_snapshot,
                market_prices or {},
            )
            total_value_usdt = live_portfolio["total_value_usdt"]
            usdt_balance = live_portfolio["usdt_balance"]

            # Parse the requested asset symbol from the user request to derive the
            # current value dynamically from the portfolio snapshot.
            asset_symbol = user_request.split()[-1].replace('?', '').replace('.', '').upper()
            if asset_symbol in {"SOL", "BTC", "ETH", "BNB", "ADA", "DOGE", "XRP"}:
                current_asset_value_usdt = get_requested_asset_value_usdt(asset_symbol, live_portfolio)
            else:
                current_asset_value_usdt = 0.0

        if total_value_usdt is None:
            total_value_usdt = 0.0
        if usdt_balance is None:
            usdt_balance = 0.0
        if current_asset_value_usdt is None:
            current_asset_value_usdt = 0.0

        # Run deterministic Guardian policy engine
        result = review_trade(
            user_request=user_request,
            total_value_usdt=total_value_usdt,
            usdt_balance=usdt_balance,
            current_asset_value_usdt=current_asset_value_usdt,
            daily_pnl_pct=daily_pnl_pct,
            policy=policy,
        )

        # Portfolio snapshot used for the decision
        portfolio = {
            "total_value_usdt": total_value_usdt,
            "usdt_balance": usdt_balance,
            "current_asset_value_usdt": current_asset_value_usdt,
            "daily_pnl_pct": daily_pnl_pct,
        }

        if portfolio_snapshot is not None:
            live_snapshot = build_portfolio_snapshot_from_agent_os(
                portfolio_snapshot,
                market_prices or {},
            )
            portfolio["total_value_usdt"] = live_snapshot["total_value_usdt"]
            portfolio["usdt_balance"] = live_snapshot["usdt_balance"]
            portfolio["asset_values"] = live_snapshot["asset_values"]

        # Create audit evidence
        audit_record = create_audit_record(
            user_request=user_request,
            result=result,
            policy=policy,
            portfolio=portfolio,
        )

        # Complete Guardian response
        response = {
            "guardian": "Binance Guardian",
            "mode": "READ_ONLY",
            "decision": result["status"],
            "trade": {
                "symbol": result["symbol"],
                "side": result["side"],
                "requested_amount_usdt": result["requested_amount"],
                "approved_amount_usdt": result["approved_amount"],
                "leverage": result["leverage"],
            },
            "policy": policy,
            "reasons": result["reasons"],
            "risk_checks": result.get("risk_checks", []),
            "execution": {
                "order_placed": False,
                "execution_authorized": False,
            },
            "audit_record": audit_record,
        }

        return response

    except Exception as exc:
        logger.exception("guardian_review_trade execution failed")
        return {
            "guardian": "Binance Guardian",
            "mode": "READ_ONLY",
            "decision": "ERROR",
            "error": {
                "type": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc(),
            },
            "execution": {
                "order_placed": False,
                "execution_authorized": False,
            },
        }


# Register Guardian as an MCP tool
server.add_tool(
    guardian_review_trade,
    name="guardian_review_trade",
    description=(
        "Review a natural-language trading request against "
        "Guardian risk policies and return ALLOW, RESIZE, or BLOCK. "
        "This tool is a read-only safety gate and never places, "
        "cancels, or modifies orders."
    ),
)


if __name__ == "__main__":
    server.run("stdio")