"""Property-based tests for color utilities using hypothesis.

These tests generate random inputs to find edge cases that manual tests miss.
Install hypothesis: uv pip install hypothesis
Run: pytest tests/properties/ --hypothesis-seed=0
"""

import re

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from charted.utils.colors import (
    calculate_contrast_ratio,
    complementary_color,
    get_contrast_color,
    hex_to_rgb,
    rgb_to_hex,
)

# ============================================================
# Hex Color Validation Properties
# ============================================================


@given(st.text(max_size=20))
@settings(max_examples=100)
def test_hex_color_rejects_empty_and_whitespace(text):
    """Hex color validator should reject empty strings and whitespace."""
    from charted.utils.colors import is_valid_hex_color

    if not text or text.isspace():
        assert not is_valid_hex_color(text)


@given(st.sampled_from(["#FFF", "#FFFFFF", "#FFFFFFFF", "#abc", "#aBcDeF"]))
@settings(max_examples=50)
def test_hex_color_accepts_valid_formats(hex_str):
    """Hex color validator should accept all valid hex formats."""
    from charted.utils.colors import is_valid_hex_color

    assert is_valid_hex_color(hex_str)


@given(st.text(min_size=1, max_size=20))
@settings(max_examples=200)
def test_hex_color_rejects_invalid_prefix(text):
    """Hex color validator should reject strings without # prefix."""
    from charted.utils.colors import is_valid_hex_color

    if not text.startswith("#"):
        assert not is_valid_hex_color(text)


@given(st.text(min_size=1, max_size=20))
@settings(max_examples=200)
def test_hex_color_rejects_invalid_characters(text):
    """Hex color validator should reject non-hex characters."""
    from charted.utils.colors import is_valid_hex_color

    if re.match(r"^[^#]*[^#A-Fa-f0-9].*$", text) or (
        text.startswith("#") and not re.match(r"^#[A-Fa-f0-9]{3,8}$", text)
    ):
        assert not is_valid_hex_color(text)


# ============================================================
# RGB Conversion Properties
# ============================================================


@given(
    r=st.integers(0, 255),
    g=st.integers(0, 255),
    b=st.integers(0, 255),
)
@settings(max_examples=100)
def test_rgb_to_hex_roundtrip(r, g, b):
    """RGB to hex conversion should be reversible."""
    hex_color = rgb_to_hex((r, g, b))
    result_r, result_g, result_b = hex_to_rgb(hex_color)

    assert result_r == r
    assert result_g == g
    assert result_b == b


@given(st.text(min_size=1, max_size=9))
@settings(max_examples=200)
def test_hex_to_rgb_rejects_invalid(hex_str):
    """hex_to_rgb should reject invalid hex strings."""
    # Valid formats: #RGB, #RRGGBB, #RRGGBBAA
    valid_pattern = r"^#[A-Fa-f0-9]{3,8}$"

    if not re.match(valid_pattern, hex_str):
        with pytest.raises(ValueError):
            hex_to_rgb(hex_str)


@given(st.sampled_from(["#FFF", "#FFFFFF", "#FFFFFFFF", "#abc", "#aBcDeF"]))
@settings(max_examples=50)
def test_hex_to_rgb_valid_formats(hex_str):
    """hex_to_rgb should accept all valid hex formats."""
    # Should not raise
    hex_to_rgb(hex_str)


# ============================================================
# Contrast Ratio Properties
# ============================================================


@given(
    fg=st.sampled_from(
        ["#000000", "#FFFFFF", "#808080", "#FF0000", "#00FF00", "#0000FF"]
    ),
    bg=st.sampled_from(
        ["#000000", "#FFFFFF", "#808080", "#FF0000", "#00FF00", "#0000FF"]
    ),
)
@settings(max_examples=50)
def test_contrast_ratio_is_symmetric(fg, bg):
    """Contrast ratio should be symmetric (A:B == B:A)."""
    ratio_ab = calculate_contrast_ratio(fg, bg)
    ratio_ba = calculate_contrast_ratio(bg, fg)

    assert abs(ratio_ab - ratio_ba) < 0.001


@given(
    color=st.sampled_from(["#000000", "#FFFFFF"]),
)
@settings(max_examples=20)
def test_contrast_ratio_same_color_is_one(color):
    """Contrast ratio of same color should be exactly 1.0."""
    ratio = calculate_contrast_ratio(color, color)
    assert ratio == 1.0


@given(
    fg=st.sampled_from(["#000000"]),
    bg=st.sampled_from(["#FFFFFF"]),
)
@settings(max_examples=20)
def test_contrast_ratio_black_white_is_max(fg, bg):
    """Black on white should have maximum contrast ratio (~21:1)."""
    ratio = calculate_contrast_ratio(fg, bg)
    assert ratio == pytest.approx(21.0, abs=0.1)


# ============================================================
# Complementary Color Properties
# ============================================================


@given(
    st.sampled_from(["#FFF", "#000", "#F00", "#0F0", "#00F", "#FF0", "#0FF", "#F0F"])
)
@settings(max_examples=50)
def test_complementary_color_hex_format(color):
    """Complementary color should return valid hex format."""
    comp = complementary_color(color)

    # Should be valid hex
    assert re.match(r"^#[A-Fa-f0-9]{6}$", comp)


@given(
    st.sampled_from(["#FFF", "#000", "#F00", "#0F0", "#00F", "#FF0", "#0FF", "#F0F"])
)
@settings(max_examples=50)
def test_complementary_color_twice_returns_original(color):
    """Complementary of complementary should approximately return original color.

    Note: Due to floating-point precision in HSV conversion, exact equality
    may not hold. We allow small differences (±2 RGB values).
    """
    comp1 = complementary_color(color)
    comp2 = complementary_color(comp1)

    # Convert to RGB for comparison (handles #FFF vs #FFFFFF)
    r1, g1, b1 = hex_to_rgb(color)
    r2, g2, b2 = hex_to_rgb(comp2)

    # Allow small floating-point precision errors
    assert abs(r1 - r2) <= 2
    assert abs(g1 - g2) <= 2
    assert abs(b1 - b2) <= 2


# ============================================================
# Contrast Color Selection Properties
# ============================================================


@given(
    bg=st.sampled_from(["#000000", "#FFFFFF", "#808080"]),
)
@settings(max_examples=30)
def test_contrast_color_returns_valid_hex(bg):
    """get_contrast_color should always return valid hex color."""
    result = get_contrast_color(bg)

    # Should be valid 6-digit hex
    assert re.match(r"^#[A-Fa-f0-9]{6}$", result)


@given(
    bg=st.sampled_from(["#000000"]),  # Black background
)
@settings(max_examples=20)
def test_contrast_color_light_on_dark(bg):
    """Light color should be selected for dark backgrounds."""
    result = get_contrast_color(bg)
    r, g, b = hex_to_rgb(result)

    # Should be light (high values)
    assert r > 128 or g > 128 or b > 128


@given(
    bg=st.sampled_from(["#FFFFFF"]),  # White background
)
@settings(max_examples=20)
def test_contrast_color_dark_on_light(bg):
    """Dark color should be selected for light backgrounds."""
    result = get_contrast_color(bg)
    r, g, b = hex_to_rgb(result)

    # Should be dark (low values)
    assert r < 128 or g < 128 or b < 128


# ============================================================
# Edge Cases and Stress Tests
# ============================================================


@given(
    r=st.integers(-100, 355),  # Out of range values
    g=st.integers(-100, 355),
    b=st.integers(-100, 355),
)
@settings(max_examples=100)
def test_rgb_to_hex_handles_edge_cases(r, g, b):
    """rgb_to_hex should handle out-of-range values gracefully."""
    try:
        hex_color = rgb_to_hex(r, g, b)
        # If it succeeds, result should be valid hex
        assert re.match(r"^#[A-Fa-f0-9]{6}$", hex_color)
    except (ValueError, TypeError):
        # Or it may raise an error - both are acceptable
        pass


@given(
    fg=st.text(min_size=1, max_size=20),
    bg=st.text(min_size=1, max_size=20),
)
@settings(max_examples=200)
def test_contrast_ratio_rejects_invalid(fg, bg):
    """calculate_contrast_ratio should reject invalid hex colors."""
    from charted.utils.colors import is_valid_hex_color

    if not is_valid_hex_color(fg) or not is_valid_hex_color(bg):
        with pytest.raises((ValueError, TypeError)):
            calculate_contrast_ratio(fg, bg)
