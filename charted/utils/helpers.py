import functools
import math
from collections import defaultdict
from typing import cast

from charted.fonts.wrapper import Font
from charted.utils.defaults import DEFAULT_FONT, DEFAULT_FONT_SIZE
from charted.utils.types import MeasuredText, Vector


@functools.lru_cache(maxsize=512)
def calculate_text_dimensions(
    text: str,
    font: str = DEFAULT_FONT,
    font_size: int = DEFAULT_FONT_SIZE,
) -> MeasuredText:
    text = str(text)
    font_instance = Font(family=font, size=font_size)
    width, height = font_instance.measure(text)
    return MeasuredText(text, width, height)


def wrap_text_to_width(
    text: str,
    max_width: float,
    font: str = DEFAULT_FONT,
    font_size: int = DEFAULT_FONT_SIZE,
) -> MeasuredText:
    """Wrap a label across multiple lines so it fits within ``max_width``.

    Splits on whitespace and greedily packs words onto each line. A single
    word longer than ``max_width`` is kept whole on its own line rather than
    being truncated, so the full text is always preserved. Returns a
    MeasuredText whose width is the widest resulting line, whose height is the
    total stacked height of all lines, and whose ``lines`` holds the per-line
    strings (``None`` when no wrapping was needed).

    A non-positive ``max_width`` disables wrapping and returns the label
    measured as a single line.
    """
    text = str(text)
    single = calculate_text_dimensions(text, font=font, font_size=font_size)
    if max_width <= 0 or single.width <= max_width:
        return single

    words = text.split()
    if not words:
        return single

    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if (
            current
            and calculate_text_dimensions(
                candidate, font=font, font_size=font_size
            ).width
            > max_width
        ):
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)

    if len(lines) <= 1:
        return single

    measured_lines = [
        calculate_text_dimensions(line, font=font, font_size=font_size)
        for line in lines
    ]
    width = max(m.width for m in measured_lines)
    height = sum(m.height for m in measured_lines)
    return MeasuredText(text, width, height, lines=lines)


def calculate_rotation_angle(
    total_label_width: float,
    total_permissible_width: float,
) -> float | None:
    if total_label_width <= total_permissible_width:
        return 0

    ratio = total_permissible_width / total_label_width
    if ratio > 1.0 or ratio < 0.0:
        raise ValueError("Invalid ratio: it should be between 0 and 1.")

    rotation_angle_radians = math.acos(ratio)
    rotation_angle_degrees = math.degrees(rotation_angle_radians)

    return rotation_angle_degrees


def rotate_coordinate(x: float, y: float, angle_degrees: float) -> tuple[float, float]:
    angle_radians = math.radians(angle_degrees)
    x_new = x * math.cos(angle_radians) - y * math.sin(angle_radians)
    y_new = x * math.sin(angle_radians) + y * math.cos(angle_radians)
    return x_new, y_new


def _divisors(n: int) -> list[int]:
    """Return sorted list of divisors of n using an O(sqrt(n)) algorithm."""
    if n <= 0:
        return []
    divisors = []
    i = 1
    sqrt_n = int(n**0.5)
    while i <= sqrt_n:
        if n % i == 0:
            divisors.append(i)
            if i != n // i:
                divisors.append(n // i)
        i += 1
    return sorted(divisors)


def common_denominators(a: float, b: float) -> Vector:
    a_int, b_int = abs(int(a)), abs(int(b))

    # Small ranges get a fixed fine-grained denominator set. This must come
    # before the integer-zero check: int(0.5) == 0, so a range like (0, 0.5)
    # would otherwise be mistaken for "both zero" and return [].
    if (b - a) <= 2:
        return [0.2, 0.25, 0.5, 1]

    if a_int == 0 and b_int == 0:
        return []

    a, b = a_int, b_int
    if a == 0:
        return cast("Vector", _divisors(b))
    elif b == 0:
        return cast("Vector", _divisors(a))

    smaller = int(min(a, b))
    common_divisors: Vector = [
        i for i in _divisors(smaller) if a % i == 0 and b % i == 0
    ]

    return common_divisors


def get_coefficient_and_exponent(value: float) -> tuple[float, float]:
    if value == 10:
        return 1, 1

    if value == 0:
        return 0, 0

    exponent = int(math.floor(math.log10(abs(value))))
    coefficient = value / (10**exponent)
    return coefficient, exponent


def round_to_clean_number(value: float, round_down: bool = False) -> float:
    is_negative = value < 0
    coefficient, exponent = get_coefficient_and_exponent(abs(value))
    nearest_half = math.ceil(coefficient * 2) / 2
    if round_down:
        nearest_half = math.floor(coefficient * 2) / 2
    rounded_value = nearest_half * (10**exponent)
    if is_negative:
        rounded_value = -rounded_value
    return rounded_value


def nested_defaultdict() -> "defaultdict[object, object]":
    return defaultdict(nested_defaultdict)


def round_coordinate(value: float, decimals: int = 1) -> float:
    """Round a coordinate value to specified decimal places.

    Args:
        value: The coordinate value to round.
        decimals: Number of decimal places (default: 1).

    Returns:
        Rounded coordinate value.
    """
    return round(value, decimals)
