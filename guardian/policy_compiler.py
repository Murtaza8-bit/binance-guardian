import re


def compile_policy(text: str) -> dict:
    """
    Convert a natural-language risk policy into Guardian's
    structured policy format.
    """

    policy = {}

    text = text.lower()

    # --------------------------------------------------
    # Maximum trade size
    # Examples:
    # "maximum trade of $100"
    # "limit each trade to $200"
    # --------------------------------------------------

    match = re.search(
        r"(?:maximum|max|limit)\s+(?:each\s+)?(?:trade|order)"
        r"(?:\s+to|\s+of)?\s*\$?(\d+(?:\.\d+)?)",
        text
    )

    if match:
        policy["max_trade_usdt"] = float(match.group(1))

    # --------------------------------------------------
    # Single asset exposure
    # Examples:
    # "15% on one asset"
    # "15% in a single asset"
    # "single asset exposure of 15%"
    # --------------------------------------------------

    match = re.search(
        r"(?:more than|maximum|max|limit)?\s*"
        r"(\d+(?:\.\d+)?)\s*%\s*"
        r"(?:on|in)\s+(?:a\s+)?(?:single\s+|one\s+)?asset",
        text
    )

    if not match:
        match = re.search(
            r"(?:single\s+asset|asset\s+exposure)"
            r".{0,30}?(\d+(?:\.\d+)?)\s*%",
            text
        )

    if match:
        policy["max_asset_exposure_pct"] = float(match.group(1))

    # --------------------------------------------------
    # USDT reserve
    # Examples:
    # "keep at least 30% in USDT"
    # "maintain 20% USDT reserve"
    # --------------------------------------------------

    match = re.search(
        r"(?:keep|maintain|reserve)"
        r".{0,20}?(\d+(?:\.\d+)?)\s*%\s*(?:in\s+)?usdt",
        text
    )

    if match:
        policy["minimum_usdt_reserve_pct"] = float(match.group(1))

    # --------------------------------------------------
    # Leverage
    # Examples:
    # "more than 2x leverage"
    # "maximum 3x"
    # --------------------------------------------------

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*x\s*(?:leverage)?",
        text
    )

    if match:
        policy["max_leverage"] = float(match.group(1))

    # --------------------------------------------------
    # Daily loss
    # Examples:
    # "daily loss limit of 3%"
    # "don't lose more than 5% in a day"
    # --------------------------------------------------

    match = re.search(
        r"(?:daily\s+loss|loss)"
        r".{0,30}?(\d+(?:\.\d+)?)\s*%",
        text
    )

    if match:
        policy["max_daily_loss_pct"] = float(match.group(1))

    return policy