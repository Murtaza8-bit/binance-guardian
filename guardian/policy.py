from dataclasses import dataclass
from typing import List


@dataclass
class TradeIntent:
    symbol: str
    side: str
    amount_usdt: float
    leverage: int = 1


@dataclass
class PortfolioState:
    total_value_usdt: float
    usdt_balance: float
    current_asset_value_usdt: float
    daily_pnl_pct: float = 0.0


@dataclass
class PolicyDecision:
    status: str
    requested_amount: float
    approved_amount: float
    reasons: List[str]
    risk_checks: List[dict]


def evaluate_trade(intent, portfolio, policy):
    reasons = []
    risk_checks = []

    approved_amount = intent.amount_usdt

    # ---------------------------------------------------------
    # 1. Maximum trade size
    # ---------------------------------------------------------

    max_trade = policy["max_trade_usdt"]

    if intent.amount_usdt > max_trade:
        approved_amount = min(
            approved_amount,
            max_trade
        )

        risk_checks.append({
            "check": "Maximum trade size",
            "status": "FAIL",
            "limit": f"${max_trade:.2f}",
            "actual": f"${intent.amount_usdt:.2f}",
            "message": (
                f"Requested ${intent.amount_usdt:.2f} "
                f"exceeds the ${max_trade:.2f} maximum trade size."
            )
        })

        reasons.append(
            f"Requested trade exceeds the "
            f"${max_trade} maximum trade size."
        )

    else:
        risk_checks.append({
            "check": "Maximum trade size",
            "status": "PASS",
            "limit": f"${max_trade:.2f}",
            "actual": f"${intent.amount_usdt:.2f}",
            "message": "Trade size is within the configured limit."
        })

    # ---------------------------------------------------------
    # 2. Leverage
    # ---------------------------------------------------------

    max_leverage = policy["max_leverage"]

    if intent.leverage > max_leverage:

        risk_checks.append({
            "check": "Maximum leverage",
            "status": "FAIL",
            "limit": f"{max_leverage}x",
            "actual": f"{intent.leverage}x",
            "message": (
                f"{intent.leverage}x leverage exceeds "
                f"the {max_leverage}x policy limit."
            )
        })

        return PolicyDecision(
            status="BLOCK",
            requested_amount=intent.amount_usdt,
            approved_amount=0,
            reasons=[
                f"{intent.leverage}x leverage exceeds the "
                f"{max_leverage}x policy limit."
            ],
            risk_checks=risk_checks
        )

    else:
        risk_checks.append({
            "check": "Maximum leverage",
            "status": "PASS",
            "limit": f"{max_leverage}x",
            "actual": f"{intent.leverage}x",
            "message": "Leverage is within the configured limit."
        })

    # ---------------------------------------------------------
    # 3. Daily loss
    # ---------------------------------------------------------

    max_daily_loss = policy["max_daily_loss_pct"]

    if portfolio.daily_pnl_pct <= -max_daily_loss:

        risk_checks.append({
            "check": "Daily loss limit",
            "status": "FAIL",
            "limit": f"-{max_daily_loss:.2f}%",
            "actual": f"{portfolio.daily_pnl_pct:.2f}%",
            "message": (
                f"Daily loss limit of {max_daily_loss}% "
                f"has been reached."
            )
        })

        return PolicyDecision(
            status="BLOCK",
            requested_amount=intent.amount_usdt,
            approved_amount=0,
            reasons=[
                f"Daily loss limit of "
                f"{max_daily_loss}% has been reached."
            ],
            risk_checks=risk_checks
        )

    else:
        risk_checks.append({
            "check": "Daily loss limit",
            "status": "PASS",
            "limit": f"-{max_daily_loss:.2f}%",
            "actual": f"{portfolio.daily_pnl_pct:.2f}%",
            "message": "Daily loss remains within the configured limit."
        })

    # ---------------------------------------------------------
    # 4. Single-asset exposure
    # ---------------------------------------------------------

    max_exposure_pct = policy["max_asset_exposure_pct"]

    if intent.side.upper() == "BUY" and portfolio.total_value_usdt > 0:

        max_asset_value = (
            portfolio.total_value_usdt
            * max_exposure_pct
            / 100
        )

        remaining_asset_capacity = max(
            0,
            max_asset_value
            - portfolio.current_asset_value_usdt
        )

        if approved_amount > remaining_asset_capacity:

            approved_amount = remaining_asset_capacity

            risk_checks.append({
                "check": "Single-asset exposure",
                "status": "FAIL",
                "limit": (
                    f"{max_exposure_pct:.2f}% "
                    f"(${max_asset_value:.2f})"
                ),
                "actual": (
                    f"${portfolio.current_asset_value_usdt:.2f} "
                    f"existing + "
                    f"${intent.amount_usdt:.2f} requested"
                ),
                "remaining_capacity": round(
                    remaining_asset_capacity,
                    2
                ),
                "message": (
                    f"Only ${remaining_asset_capacity:.2f} "
                    f"of asset exposure remains available."
                )
            })

            reasons.append(
                f"Trade would exceed the "
                f"{max_exposure_pct}% "
                f"single-asset exposure limit."
            )

        else:

            risk_checks.append({
                "check": "Single-asset exposure",
                "status": "PASS",
                "limit": (
                    f"{max_exposure_pct:.2f}% "
                    f"(${max_asset_value:.2f})"
                ),
                "actual": (
                    f"${portfolio.current_asset_value_usdt:.2f} "
                    f"existing + "
                    f"${intent.amount_usdt:.2f} requested"
                ),
                "message": (
                    "Trade remains within the asset exposure limit."
                )
            })

    # ---------------------------------------------------------
    # 5. USDT reserve
    # ---------------------------------------------------------

    reserve_pct = policy["minimum_usdt_reserve_pct"]

    minimum_reserve = (
        portfolio.total_value_usdt
        * reserve_pct
        / 100
    )

    spendable_usdt = max(
        0,
        portfolio.usdt_balance
        - minimum_reserve
    )

    if intent.side.upper() == "BUY":

        if approved_amount > spendable_usdt:

            approved_amount = spendable_usdt

            risk_checks.append({
                "check": "USDT reserve",
                "status": "FAIL",
                "limit": (
                    f"{reserve_pct:.2f}% "
                    f"(${minimum_reserve:.2f})"
                ),
                "actual": f"${portfolio.usdt_balance:.2f}",
                "spendable": round(spendable_usdt, 2),
                "message": (
                    f"Trade reduced to preserve the "
                    f"{reserve_pct}% USDT reserve."
                )
            })

            reasons.append(
                f"Order reduced to preserve the "
                f"{reserve_pct}% USDT reserve."
            )

        else:

            risk_checks.append({
                "check": "USDT reserve",
                "status": "PASS",
                "limit": (
                    f"{reserve_pct:.2f}% "
                    f"(${minimum_reserve:.2f})"
                ),
                "actual": f"${portfolio.usdt_balance:.2f}",
                "spendable": round(spendable_usdt, 2),
                "message": (
                    "USDT reserve requirement is satisfied."
                )
            })

    # ---------------------------------------------------------
    # Final decision
    # ---------------------------------------------------------

    approved_amount = round(approved_amount, 2)

    if approved_amount <= 0:

        status = "BLOCK"

    elif approved_amount < intent.amount_usdt:

        status = "RESIZE"

    else:

        status = "ALLOW"

        reasons.append(
            "All configured Guardian policies passed."
        )

    return PolicyDecision(
        status=status,
        requested_amount=intent.amount_usdt,
        approved_amount=approved_amount,
        reasons=reasons,
        risk_checks=risk_checks
    )