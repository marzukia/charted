"""Property-based tests for color utilities using hypothesis."""

import re
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from charted.utils.colors import (
    calculate_contrast_ratio,
    complementary_color,
    get_contrast_color,
    hex_to_rgb,
    is_valid_hex_color,
    rgb_to_hex,
)

hex_digits = "0123456789ABCDEFabcdef"

hex3 = st.tuples(
    st.sampled_from(hex_digits), st.sampled_from(hex_digits), st.sampled_from(hex_digits)
).map(lambda t: f"#{t[0]}{t[1]}{t[2]}")

hex6 = st.tuples(*[st.sampled_from(hex_digits)] * 6).map(
    lambda t: f"#{''.join(t)}"
)

valid_hex = st.one_of(hex3, hex6)


@given(st.text(max_size=30))
@settings(max_examples=150)
def test_is_valid_hex_color_accepts_only_valid(text):
    result = is_valid_hex_color(text)
    if result:
        assert re.match(r"^#[A-Fa-f0-9]{3,8}$", text)


@given(valid_hex)
@settings(max_examples=100)
def test_hex_to_rgb_roundtrip(hex_color):
    r, g, b = hex_to_rgb(hex_color)
    assert 0 <= r <= 255
    assert 0 <= g <= 255
    assert 0 <= b <= 255
    regenerated = rgb_to_hex((r, g, b))
    assert re.match(r"^#[A-Fa-f0-9]{6}$", regenerated)


@given(
    r=st.integers(0, 255),
    g=st.integers(0, 255),
    b=st.integers(0, 255),
)
@settings(max_examples=100)
def test_rgb_to_hex_roundtrip_from_rgb(r, g, b):
    hex_color = rgb_to_hex((r, g, b))
    rr, rg, rb = hex_to_rgb(hex_color)
    assert rr == r
    assert rg == g
    assert rb == b


@given(
    r=st.integers(-100, 355),
    g=st.integers(-100, 355),
    b=st.integers(-100, 355),
)
@settings(max_examples=100)
def test_rgb_to_hex_clamps_or_rejects(r, g, b):
    in_range = 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255
    try:
        result = rgb_to_hex((r, g, b))
        assert re.match(r"^#[A-Fa-f0-9]{6}$", result)
        if not in_range:
            pytest.fail(f"rgb_to_hex({r},{g},{b}) should have raised ValueError for out-of-range input")
    except (ValueError, TypeError):
        if in_range:
            pytest.fail(f"rgb_to_hex({r},{g},{b}) should not have raised for in-range input")


@given(st.text(min_size=1, max_size=20))
@settings(max_examples=200)
def test_hex_to_rgb_rejects_invalid(hex_str):
    if not re.match(r"^#[A-Fa-f0-9]{3,8}$", hex_str):
        with pytest.raises(ValueError):
            hex_to_rgb(hex_str)


@given(valid_hex, valid_hex)
@settings(max_examples=100)
def test_contrast_ratio_symmetric(fg, bg):
    ratio_ab = calculate_contrast_ratio(fg, bg)
    ratio_ba = calculate_contrast_ratio(bg, fg)
    assert abs(ratio_ab - ratio_ba) < 0.001


@given(valid_hex)
@settings(max_examples=50)
def test_contrast_ratio_same_color_is_one(color):
    ratio = calculate_contrast_ratio(color, color)
    assert ratio == pytest.approx(1.0)


@given(valid_hex)
@settings(max_examples=50)
def test_contrast_ratio_against_white_minimum_one(fg):
    ratio = calculate_contrast_ratio(fg, "#FFFFFF")
    assert ratio >= 1.0


@given(valid_hex)
@settings(max_examples=50)
def test_contrast_ratio_against_black_minimum_one(fg):
    ratio = calculate_contrast_ratio(fg, "#000000")
    assert ratio >= 1.0


@given(valid_hex)
@settings(max_examples=150)
def test_complementary_color_returns_valid_hex(color):
    comp = complementary_color(color)
    assert re.match(r"^#[A-Fa-f0-9]{6}$", comp)


@given(valid_hex)
@settings(max_examples=80)
def test_complementary_twice_is_original(color):
    comp1 = complementary_color(color)
    comp2 = complementary_color(comp1)
    r1, g1, b1 = hex_to_rgb(color)
    r2, g2, b2 = hex_to_rgb(comp2)
    assert abs(r1 - r2) <= 2
    assert abs(g1 - g2) <= 2
    assert abs(b1 - b2) <= 2


@given(valid_hex)
@settings(max_examples=100)
def test_get_contrast_color_returns_valid_hex(bg):
    result = get_contrast_color(bg)
    assert re.match(r"^#[A-Fa-f0-9]{6}$", result)


@given(valid_hex)
@settings(max_examples=80)
def test_contrast_color_is_readable_on_background(bg):
    fg = get_contrast_color(bg)
    ratio = calculate_contrast_ratio(fg, bg)
    assert ratio >= 2.5


@given(
    fg=st.text(min_size=1, max_size=20),
    bg=st.text(min_size=1, max_size=20),
)
@settings(max_examples=200)
def test_contrast_ratio_rejects_invalid_input(fg, bg):
    if not is_valid_hex_color(fg) or not is_valid_hex_color(bg):
        with pytest.raises((ValueError, TypeError)):
            calculate_contrast_ratio(fg, bg)
