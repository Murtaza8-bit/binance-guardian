from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class BinancePortfolio:
    total_value_usdt: float
    usdt_balance: float
    asset_values: dict


def build_portfolio_from_balances(balances: list[dict], prices: Optional[dict[str, float]] = None) -> BinancePortfolio:
    """
    Convert read-only Binance spot balance data into the portfolio structure
    expected by Guardian.

    The account balance payload is expected to look like:
    [{"asset": "USDT", "free": "350.00", "locked": "0.00"}, ...]

    The optional prices map is keyed by asset symbol, for example:
    {"SOL": 105.9, "BTC": 79948.77, "ETH": 2501.53}
    """

    usdt_balance = 0.0
    asset_values = {}
    total_value_usdt = 0.0

    for balance in balances or []:
        asset = str(balance.get("asset", "")).upper()
        free = float(balance.get("free", 0) or 0)
        locked = float(balance.get("locked", 0) or 0)
        total = free + locked

        if total <= 0:
            continue

        if asset == "USDT":
            usdt_balance = total
            total_value_usdt += total
        else:
            price = float(prices.get(asset, 0.0) or 0.0) if prices else 0.0
            asset_values[asset] = total * price
            total_value_usdt += asset_values[asset]

    if usdt_balance > 0:
        total_value_usdt += 0.0

    # The portfolio owner may also hold USDT as a separate balance that is not in
    # the account data; in that case it is already included in the USDT total above.
    return BinancePortfolio(
        total_value_usdt=round(total_value_usdt, 2),
        usdt_balance=round(usdt_balance, 2),
        asset_values={k: round(v, 8) for k, v in asset_values.items()},
    )


def get_requested_asset_value_usdt(asset_symbol: str, portfolio: Any) -> float:
    """Return the current value of the requested asset in USDT from a live portfolio snapshot."""
    asset = str(asset_symbol or "").upper()
    if not asset:
        return 0.0

    if hasattr(portfolio, "asset_values"):
        qty = getattr(portfolio, "asset_values").get(asset, 0.0)
    else:
        qty = (portfolio or {}).get("asset_values", {}).get(asset, 0.0)

    if qty <= 0:
        return 0.0

    return round(float(qty), 8)


def build_portfolio_snapshot_from_agent_os(account_data: Dict[str, Any], market_prices: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """Mirror the live Binance Agent OS account response into Guardian's expected portfolio structure."""
    balances = account_data.get("balances", []) if isinstance(account_data, dict) else []
    portfolio = build_portfolio_from_balances(balances, prices=market_prices or {})

    return {
        "total_value_usdt": portfolio.total_value_usdt,
        "usdt_balance": portfolio.usdt_balance,
        "asset_values": portfolio.asset_values,
    }