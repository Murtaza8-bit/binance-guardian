import re

from guardian.policy import TradeIntent


def parse_trade_intent(message: str) -> TradeIntent:
    """
    Convert a natural-language trading request into a structured
    TradeIntent that Guardian's deterministic policy engine can evaluate.
    """

    text = message.lower().strip()

    # Find trading side
    if re.search(r"\b(buy|purchase)\b", text):
        side = "BUY"
    elif re.search(r"\b(sell|dump)\b", text):
        side = "SELL"
    else:
        raise ValueError("Could not determine whether this is a BUY or SELL request.")

    # Find an explicitly monetary trade amount, not numbers from leverage text.
    amount_patterns = (
        r"\$\s*(\d+(?:\.\d+)?)",
        r"\b(?:usd|usdt)\s*(\d+(?:\.\d+)?)\b",
        r"\b(\d+(?:\.\d+)?)\s*(?:usd|usdt)\b",
    )
    amount_match = None
    for pattern in amount_patterns:
        amount_match = re.search(pattern, text)
        if amount_match:
            break

    if not amount_match:
        raise ValueError("Could not determine the trade amount.")

    amount_usdt = float(amount_match.group(1))

    # Find common crypto symbols
    symbol_match = re.search(
        r"\b(btc|bitcoin|eth|ethereum|bnb|sol|solana|xrp|ada|doge|avax|dot|link)\b",
        text
    )

    if not symbol_match:
        raise ValueError("Could not determine the cryptocurrency.")

    symbol_map = {
        "btc": "BTCUSDT",
        "bitcoin": "BTCUSDT",
        "eth": "ETHUSDT",
        "ethereum": "ETHUSDT",
        "bnb": "BNBUSDT",
        "sol": "SOLUSDT",
        "solana": "SOLUSDT",
        "xrp": "XRPUSDT",
        "ada": "ADAUSDT",
        "doge": "DOGEUSDT",
        "avax": "AVAXUSDT",
        "dot": "DOTUSDT",
        "link": "LINKUSDT",
    }

    symbol = symbol_map[symbol_match.group(1)]

    # Find leverage if mentioned
    leverage_match = re.search(r"(\d+)\s*x", text)
    leverage = int(leverage_match.group(1)) if leverage_match else 1

    return TradeIntent(
        symbol=symbol,
        side=side,
        amount_usdt=amount_usdt,
        leverage=leverage
    )