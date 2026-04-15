from collections import defaultdict
import json
import math
import os


from charted.utils.defaults import BASE_DEFINITIONS_DIR, DEFAULT_FONT, DEFAULT_FONT_SIZE
from charted.utils.types import MeasuredText, Vector


def calculate_text_dimensions(
    text: str,
    font: str = DEFAULT_FONT,
    font_size: int = DEFAULT_FONT_SIZE,
) -> MeasuredText:
    text = str(text)
    with open(os.path.join(BASE_DEFINITIONS_DIR, f"{font}.json"), "r") as src:
        lookup = json.loads(src.read())[str(font_size)]
        ord_arr = [ord(char) for char in text]
        width = sum([lookup[str(ord_char)]["width"] for ord_char in ord_arr])
        height = max([lookup[str(ord_char)]["height"] for ord_char in ord_arr])
        return MeasuredText(text, width, height)


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
    if (b - a) <= 2:
        return [0.2, 0.25, 0.5, 1]

    a, b = abs(int(a)), abs(int(b))
    if a == 0 and b == 0:
        return []
    elif a == 0:
        return _divisors(b)
    elif b == 0:
        return _divisors(a)

    smaller = int(min(a, b))
    common_divisors = [i for i in _divisors(smaller) if a % i == 0 and b % i == 0]

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


def nested_defaultdict() -> defaultdict:
    return defaultdict(nested_defaultdict)
