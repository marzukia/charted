"""Tests for color utility functions."""

import pytest
from charted.utils.colors import (
    hex_to_rgb,
    rgb_to_hex,
    complementary_color,
)


class TestColorUtilitiesHappyPath:
    """Test happy path scenarios for color utilities."""

    def test_parse_valid_hex(self):
        """Test parsing valid hex color."""
        rgb = hex_to_rgb("#FF5733")
        assert rgb == (255, 87, 51)

    def test_parse_valid_rgb(self):
        """Test converting RGB to hex."""
        hex_color = rgb_to_hex((255, 87, 51))
        assert hex_color == "#ff5733"

    def test_complementary_color_valid(self):
        """Test computing complementary color."""
        comp = complementary_color("#FF0000")
        assert comp.startswith("#")
        assert len(comp) == 7


class TestColorUtilitiesSadPath:
    """Test edge cases for color utilities."""

    def test_invalid_hex_characters(self):
        """Test invalid hex characters raises ValueError."""
        with pytest.raises(ValueError):
            hex_to_rgb("#GGG")

    def test_hex_too_short(self):
        """Test hex too short raises ValueError."""
        with pytest.raises(ValueError):
            hex_to_rgb("#FF")

    def test_rgb_value_out_of_range(self):
        """Test RGB values out of range."""
        hex_color = rgb_to_hex((256, 0, 0))
        assert "#" in hex_color

    def test_hex_too_long(self):
        """Test hex too long - extra characters are ignored."""
        rgb = hex_to_rgb("#FF5733FF")
        assert rgb == (255, 87, 51)

    def test_rgb_negative_value(self):
        """Test RGB negative value."""
        hex_color = rgb_to_hex((-1, 0, 0))
        assert "#" in hex_color
