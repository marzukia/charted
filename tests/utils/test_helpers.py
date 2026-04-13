import math
from collections import defaultdict

import pytest

from charted.utils.helpers import (
    calculate_rotation_angle,
    calculate_text_dimensions,
    common_denominators,
    get_coefficient_and_exponent,
    nested_defaultdict,
    rotate_coordinate,
    round_to_clean_number,
)


def test_nested_defaultdict():
    nested = nested_defaultdict()
    nested[1][1] = "a"
    assert type(nested) is defaultdict
    assert type(nested[1]) is defaultdict


def test_nested_defaultdict_nested_access():
    nested = nested_defaultdict()
    nested[1][2][3] = "value"
    assert nested[1][2][3] == "value"


def test_nested_defaultdict_autovivification():
    nested = nested_defaultdict()
    result = nested[1][2]
    assert type(result) is defaultdict


def test_nested_defaultdict_is_defaultdict():
    nested = nested_defaultdict()
    assert isinstance(nested, defaultdict)


class TestCalculateRotationAngle:
    def test_calculate_rotation_angle_returns_zero_when_label_fits(self):
        result = calculate_rotation_angle(100, 150)
        assert result == 0

    def test_calculate_rotation_angle_with_small_permissible_width(self):
        result = calculate_rotation_angle(100, 50)
        expected = math.degrees(math.acos(0.5))
        assert result == expected

    def test_calculate_rotation_angle_with_equal_widths(self):
        result = calculate_rotation_angle(100, 100)
        assert result == 0

    def test_calculate_rotation_angle_with_invalid_ratio_negative(self):
        with pytest.raises(ValueError, match="Invalid ratio"):
            calculate_rotation_angle(100, -50)

    def test_calculate_rotation_angle_with_zero_permissible(self):
        result = calculate_rotation_angle(100, 0)
        assert result == 90.0

    def test_calculate_rotation_angle_with_permissible_greater_than_label(self):
        result = calculate_rotation_angle(100, 200)
        assert result == 0


class TestRotateCoordinate:
    def test_rotate_coordinate_0_degrees(self):
        x, y = rotate_coordinate(10, 0, 0)
        assert x == 10
        assert y == 0

    def test_rotate_coordinate_90_degrees(self):
        x, y = rotate_coordinate(1, 0, 90)
        assert abs(x - 0) < 1e-10
        assert abs(y - 1) < 1e-10

    def test_rotate_coordinate_180_degrees(self):
        x, y = rotate_coordinate(1, 0, 180)
        assert abs(x - (-1)) < 1e-10
        assert abs(y - 0) < 1e-10

    def test_rotate_coordinate_360_degrees(self):
        x, y = rotate_coordinate(5, 3, 360)
        assert abs(x - 5) < 1e-10
        assert abs(y - 3) < 1e-10

    def test_rotate_coordinate_negative_angle(self):
        x, y = rotate_coordinate(1, 0, -90)
        assert abs(x - 0) < 1e-10
        assert abs(y - (-1)) < 1e-10

    def test_rotate_coordinate_arbitrary_point(self):
        x, y = rotate_coordinate(2, 3, 90)
        assert abs(x - (-3)) < 1e-10
        assert abs(y - 2) < 1e-10


class TestCommonDenominators:
    def test_common_denominators_small_difference_close_values(self):
        # When b_abs - a_abs <= 2, return default list
        result = common_denominators(1, 2)
        assert result == [0.2, 0.25, 0.5, 1]

    def test_common_denominators_equal_small_numbers(self):
        result = common_denominators(1, 3)
        assert result == [0.2, 0.25, 0.5, 1]

    def test_common_denominators_equal_numbers_large_diff(self):
        result = common_denominators(6, 6)
        # diff = 0 <= 2, so return default
        assert result == [0.2, 0.25, 0.5, 1]

    def test_common_denominators_coprime_numbers_large_diff(self):
        result = common_denominators(5, 10)
        # diff = 5 > 2, so compute actual divisors
        assert result == [1, 5]

    def test_common_denominators_gcd_is_included(self):
        result = common_denominators(12, 18)
        assert 6 in result

    def test_common_denominators_zero_and_nonzero_large_diff(self):
        result = common_denominators(0, 6)
        # diff = 6 > 2, a_abs == 0 so return divisors of b
        assert result == [1, 2, 3, 6]

    def test_common_denominators_both_zero(self):
        result = common_denominators(0, 0)
        # diff = 0 <= 2, so return default
        assert result == [0.2, 0.25, 0.5, 1]

    def test_common_denominators_negative_permissible(self):
        result = common_denominators(-12, 18)
        # a_abs=12, b_abs=18, diff=6 > 2, compute divisors
        assert result == [1, 2, 3, 6]

    def test_common_denominators_negative_label(self):
        result = common_denominators(12, -18)
        # a_abs=12, b_abs=18, diff=6 > 2, compute divisors
        assert result == [1, 2, 3, 6]


class TestGetCoefficientAndExponent:
    def test_get_coefficient_and_exponent_basic(self):
        coef, exp = get_coefficient_and_exponent(10)
        assert coef == 1
        assert exp == 1

    def test_get_coefficient_and_exponent_large_number(self):
        coef, exp = get_coefficient_and_exponent(1500)
        assert abs(coef - 1.5) < 1e-10
        assert exp == 3

    def test_get_coefficient_and_exponent_small_number(self):
        coef, exp = get_coefficient_and_exponent(0.05)
        assert abs(coef - 5) < 1e-10
        assert exp == -2

    def test_get_coefficient_and_exponent_zero(self):
        coef, exp = get_coefficient_and_exponent(0)
        assert coef == 0
        assert exp == 0

    def test_get_coefficient_and_exponent_negative_number(self):
        coef, exp = get_coefficient_and_exponent(-100)
        assert abs(coef - (-1)) < 1e-10
        assert exp == 2

    def test_get_coefficient_and_exponent_exact_power_of_10(self):
        coef, exp = get_coefficient_and_exponent(1000)
        assert coef == 1
        assert exp == 3

    def test_get_coefficient_and_exponent_fractional(self):
        coef, exp = get_coefficient_and_exponent(0.1)
        assert abs(coef - 1) < 1e-10
        assert exp == -1


class TestRoundToCleanNumber:
    def test_round_to_clean_number_basic(self):
        result = round_to_clean_number(23)
        assert result == 25

    def test_round_to_clean_number_round_down(self):
        result = round_to_clean_number(23, round_down=True)
        assert result == 20

    def test_round_to_clean_number_small_value(self):
        result = round_to_clean_number(0.23)
        assert result == 0.25

    def test_round_to_clean_number_negative(self):
        result = round_to_clean_number(-23)
        assert result == -25

    def test_round_to_clean_number_already_clean(self):
        result = round_to_clean_number(25)
        assert result == 25

    def test_round_to_clean_number_large_value(self):
        result = round_to_clean_number(1500)
        assert result == 1500


class TestCalculateTextDimensions:
    def test_calculate_text_dimensions_basic(self):
        result = calculate_text_dimensions("Hello", "Arial", 12)
        assert result.text == "Hello"
        assert result.width > 0
        assert result.height > 0

    def test_calculate_text_dimensions_empty_string(self):
        result = calculate_text_dimensions("", "Arial", 12)
        assert result.text == ""
        assert result.width == 0
        assert result.height == 0

    def test_calculate_text_dimensions_single_char(self):
        result = calculate_text_dimensions("A", "Arial", 12)
        assert result.text == "A"
        assert result.width > 0
        assert result.height > 0

    def test_calculate_text_dimensions_wide_characters(self):
        text = "WWW"
        result = calculate_text_dimensions(text, "Arial", 12)
        single_char_result = calculate_text_dimensions("W", "Arial", 12)
        assert abs(result.width - 3 * single_char_result.width) < 0.01
