import re


class PolicyCompilationError(ValueError):
    """Raised when a recognizable safety policy cannot be compiled safely."""


def _unsupported_policy_categories(text: str, policy: dict) -> list[str]:
    categories = []

    if re.search(r"\b(?:trade|order)\b", text) and re.search(
        r"\b(?:maximum|max|limit|cap|at most|no more)\b", text
    ) and "max_trade_usdt" not in policy:
        categories.append("maximum trade size")

    if re.search(r"\b(?:asset|exposure|risk)\b", text) and re.search(
        r"\b(?:\d+(?:\.\d+)?)\s*(?:%|percent)\b", text
    ) and "max_asset_exposure_pct" not in policy:
        categories.append("single-asset exposure")

    if re.search(r"\busdt\b", text) and re.search(
        r"\b(?:keep|maintain|reserve|minimum|at least|hold)\b", text
    ) and "minimum_usdt_reserve_pct" not in policy:
        categories.append("minimum USDT reserve")

    if re.search(r"\bleverage\b|\b\d+(?:\.\d+)?\s*x\b", text) and "max_leverage" not in policy:
        categories.append("maximum leverage")

    if re.search(r"\b(?:daily|per day|in a day)\b", text) and re.search(
        r"\b(?:loss|lose|drawdown)\b", text
    ) and "max_daily_loss_pct" not in policy:
        categories.append("daily loss limit")

    if re.search(r"\bconfirm(?:ation|ed)?\b", text):
        categories.append("confirmation requirement")

    return categories


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

    unsupported_categories = _unsupported_policy_categories(text, policy)
    if unsupported_categories:
        categories = ", ".join(unsupported_categories)
        raise PolicyCompilationError(
            f"Could not compile safety policy requirement: {categories}."
        )

    return policy