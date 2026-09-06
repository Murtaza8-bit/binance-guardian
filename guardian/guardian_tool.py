from guardian.policy import (
    PortfolioState,
    evaluate_trade
)

from guardian.intent import parse_trade_intent


def review_trade(
    user_request: str,
    total_value_usdt: float,
    usdt_balance: float,
    current_asset_value_usdt: float,
    daily_pnl_pct: float,
    policy: dict
):
    """
    Guardian safety gate.

    Reviews a natural-language trading request against the
    user's portfolio and configured risk policies.

    This function NEVER places an order.
    """

    # Convert natural language into structured intent
    trade = parse_trade_intent(user_request)
    confirmation_required = bool(policy.get("require_confirmation", False))

    if policy.get("max_daily_loss_pct") is not None and daily_pnl_pct is None:
        return {
            "status": "BLOCK",
            "symbol": trade.symbol,
            "side": trade.side,
            "requested_amount": trade.amount_usdt,
            "approved_amount": 0,
            "leverage": trade.leverage,
            "confirmation_required": confirmation_required,
            "reasons": [
                "Daily P&L data unavailable; unable to safely evaluate the daily loss limit."
            ],
            "risk_checks": [{
                "check": "Daily loss limit",
                "status": "FAIL",
                "limit": f"Daily P&L data required; loss limit is {policy['max_daily_loss_pct']:.2f}%",
                "actual": "Unavailable",
                "message": (
                    "Daily P&L data unavailable; unable to safely evaluate "
                    "the daily loss limit."
                ),
            }],
        }

    # --------------------------------------------------
    # Basic balance check
    # --------------------------------------------------

    if trade.side.upper() == "BUY" and trade.amount_usdt > usdt_balance:
        return {
            "status": "BLOCK",
            "symbol": trade.symbol,
            "side": trade.side,
            "requested_amount": trade.amount_usdt,
            "approved_amount": 0,
            "leverage": trade.leverage,
            "confirmation_required": confirmation_required,
            "reasons": [
                (
                    f"Insufficient USDT balance. "
                    f"Available: ${usdt_balance:.2f}; "
                    f"requested: ${trade.amount_usdt:.2f}."
                )
            ],
            "risk_checks": [{
                "check": "USDT balance",
                "status": "FAIL",
                "limit": f"Available USDT >= ${trade.amount_usdt:.2f}",
                "actual": f"${usdt_balance:.2f}",
                "message": (
                    f"Insufficient USDT balance. Available: "
                    f"${usdt_balance:.2f}; requested: "
                    f"${trade.amount_usdt:.2f}."
                )
            }]
        }

    # --------------------------------------------------
    # Build portfolio state
    # --------------------------------------------------

    if trade.side.upper() == "SELL" and trade.amount_usdt > current_asset_value_usdt:
        return {
            "status": "BLOCK",
            "symbol": trade.symbol,
            "side": trade.side,
            "requested_amount": trade.amount_usdt,
            "approved_amount": 0,
            "leverage": trade.leverage,
            "confirmation_required": confirmation_required,
            "reasons": [
                (
                    f"Insufficient asset balance. "
                    f"Available: ${current_asset_value_usdt:.2f}; "
                    f"requested: ${trade.amount_usdt:.2f}."
                )
            ],
            "risk_checks": [{
                "check": "Asset balance",
                "status": "FAIL",
                "limit": f"Available asset value >= ${trade.amount_usdt:.2f}",
                "actual": f"${current_asset_value_usdt:.2f}",
                "message": (
                    f"Insufficient asset balance. Available: "
                    f"${current_asset_value_usdt:.2f}; requested: "
                    f"${trade.amount_usdt:.2f}."
                )
            }]
        }
    portfolio = PortfolioState(
        total_value_usdt=total_value_usdt,
        usdt_balance=usdt_balance,
        current_asset_value_usdt=current_asset_value_usdt,
        daily_pnl_pct=daily_pnl_pct
    )

    # --------------------------------------------------
    # Run deterministic Guardian policy engine
    # --------------------------------------------------

    decision = evaluate_trade(
        trade,
        portfolio,
        policy
    )

    return {
        "status": decision.status,
        "symbol": trade.symbol,
        "side": trade.side,
        "requested_amount": decision.requested_amount,
        "approved_amount": decision.approved_amount,
        "leverage": trade.leverage,
        "confirmation_required": confirmation_required,
        "reasons": decision.reasons,
        "risk_checks": decision.risk_checks
    }