"""Number/label formatting helpers shared by all modules.

Every function returns an em dash ("—") for missing or invalid values,
so modules never have to handle None themselves.
"""

# Terminal palette (kept in sync with app.py CSS)
UP = "#00E676"      # gains
DOWN = "#FF5252"    # losses
ACCENT = "#FF9900"  # amber labels / rules
TEXT = "#E6EDF3"


def fmt_num(x, decimals: int = 2, suffix: str = "") -> str:
    """Plain number with thousands separators: 1,234.56"""
    if x is None:
        return "—"
    try:
        return f"{float(x):,.{decimals}f}{suffix}"
    except (TypeError, ValueError):
        return "—"


def fmt_big(x) -> str:
    """Human-readable large numbers: 1.53T, 234.50B, 12.30M, 8.4K"""
    if x is None:
        return "—"
    try:
        x = float(x)
    except (TypeError, ValueError):
        return "—"
    for threshold, label in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(x) >= threshold:
            return f"{x / threshold:,.2f}{label}"
    return f"{x:,.0f}"


def fmt_pct(x, is_fraction: bool = True) -> str:
    """Percentage formatting.

    is_fraction=True  -> source value 0.153 means 15.3%
    is_fraction=False -> source value is already in percent (15.3)
    """
    if x is None:
        return "—"
    try:
        x = float(x)
    except (TypeError, ValueError):
        return "—"
    return f"{x * 100:.2f}%" if is_fraction else f"{x:.2f}%"


def chg_color(x) -> str:
    """Green for gains, red for losses, neutral when unknown."""
    try:
        return UP if float(x) >= 0 else DOWN
    except (TypeError, ValueError):
        return TEXT
