"""Value-label formatting for on-element data annotations.

Turns a raw numeric value into a display string under one of three formats:

- ``"number"``  -> grouped decimal, e.g. ``1,234.5``
- ``"percent"`` -> value scaled to a percentage, e.g. ``0.25`` -> ``25%``
- ``"currency"`` -> prefixed grouped decimal, e.g. ``$1,234.50``

The formatter is intentionally dependency-free (no ``locale``/``babel``) so it
behaves identically across environments. Options are passed as plain keyword
arguments and every one has a sensible default, so ``format_value(12.5)`` works
on its own.
"""

from __future__ import annotations

import math

VALID_FORMATS = ("number", "percent", "currency")

# Magnitude thresholds for switching to scientific notation. Values at or above
# the large threshold (e.g. 1,000,000,000) or below the small threshold and
# non-zero (e.g. 0.0002) become unwieldy as grouped decimals: huge numbers
# collide on dense axes, tiny ones round to "0". Anything between the two
# thresholds keeps the historical grouped-decimal formatting byte-for-byte.
_SCI_LARGE = 1e6
_SCI_SMALL = 1e-3


def _to_scientific(value: float) -> str:
    """Render ``value`` in compact scientific notation, e.g. ``1.5e9``.

    The mantissa is rounded to two decimals and trailing zeros are trimmed, so
    round magnitudes collapse to a bare ``1e9`` / ``2e-4`` rather than
    ``1.00e9``. A mantissa that rounds up to 10 carries into the exponent so
    ``999999999`` formats as ``1e9`` rather than ``10e8``.
    """
    if value == 0:
        return "0"
    negative = value < 0
    magnitude = abs(value)
    exponent = math.floor(math.log10(magnitude))
    mantissa = round(magnitude / (10**exponent), 2)
    if mantissa >= 10:
        mantissa /= 10
        exponent += 1
    mantissa_str = f"{mantissa:.2f}".rstrip("0").rstrip(".")
    out = f"{mantissa_str}e{exponent}"
    return f"-{out}" if negative else out


def _is_extreme_magnitude(value: float) -> bool:
    """True when ``value`` is large or small enough to warrant sci-notation."""
    magnitude = abs(value)
    return magnitude != 0 and (magnitude >= _SCI_LARGE or magnitude < _SCI_SMALL)


def _group(int_part: str, sep: str) -> str:
    """Insert a thousands separator into a sign-stripped integer string."""
    if sep == "" or len(int_part) <= 3:
        return int_part
    digits = []
    for offset, ch in enumerate(reversed(int_part)):
        if offset and offset % 3 == 0:
            digits.append(sep)
        digits.append(ch)
    return "".join(reversed(digits))


def format_value(
    value: float,
    fmt: str = "number",
    *,
    decimals: int | None = None,
    prefix: str = "",
    suffix: str = "",
    currency_symbol: str = "$",
    thousands_sep: str = ",",
    percent_scale: bool = True,
) -> str:
    """Format a numeric value for display on a chart element.

    Args:
        value: The raw value to format.
        fmt: One of ``"number"``, ``"percent"``, ``"currency"``.
        decimals: Fixed number of decimal places. ``None`` picks a default per
            format (0 for number/percent/currency unless the value has a
            fractional part, in which case 1) and trims trailing zeros for the
            ``number`` format only.
        prefix: String prepended to the result (after any sign handling).
        suffix: String appended to the result.
        currency_symbol: Symbol used for ``"currency"`` format.
        thousands_sep: Grouping separator for the integer part. ``""`` disables.
        percent_scale: For ``"percent"``, multiply the value by 100 first. Set
            ``False`` when the value is already a percentage (e.g. ``25`` -> ``25%``).

    Returns:
        The formatted string.

    Raises:
        ValueError: If ``fmt`` is not a recognised format.
    """
    if fmt not in VALID_FORMATS:
        raise ValueError(
            f"Unknown value-label format {fmt!r}; expected one of {VALID_FORMATS}"
        )

    try:
        num = float(value)
    except (TypeError, ValueError):
        return str(value)

    # Switch extreme magnitudes to scientific notation for the plain number
    # format (axis ticks and on-element value labels). Currency and percent
    # keep their grouped formatting: a percentage is already a small,
    # human-scale number after scaling, and currency rarely wants an exponent.
    # Normal-range numbers fall through untouched so existing baselines stay
    # byte-identical.
    if fmt == "number" and _is_extreme_magnitude(num):
        return f"{prefix}{_to_scientific(num)}{suffix}"

    scaled = num * 100 if (fmt == "percent" and percent_scale) else num

    # Decide decimal places.
    if decimals is None:
        has_fraction = abs(scaled - round(scaled)) > 1e-9
        places = 1 if has_fraction else 0
        trim = fmt == "number"
    else:
        places = max(0, int(decimals))
        trim = False

    negative = scaled < 0
    body = f"{abs(scaled):.{places}f}"

    if "." in body:
        int_part, frac_part = body.split(".")
    else:
        int_part, frac_part = body, ""

    int_part = _group(int_part, thousands_sep)
    out = int_part if not frac_part else f"{int_part}.{frac_part}"

    if trim and "." in out:
        out = out.rstrip("0").rstrip(".")

    sign = "-" if negative else ""

    if fmt == "currency":
        out = f"{sign}{currency_symbol}{out}"
    elif fmt == "percent":
        out = f"{sign}{out}%"
    else:
        out = f"{sign}{out}"

    return f"{prefix}{out}{suffix}"
