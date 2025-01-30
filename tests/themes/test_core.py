"""Tests for charted.themes.core module."""

import pytest

from charted.themes.core import ColorPalette, Theme


class TestThemePreset:
    """Test Theme.from_preset() method."""

    def test_light_preset(self):
        """Test light theme preset has expected colors."""
        theme = Theme.from_preset("light")
        assert theme.title_color == "#1f2937"
        assert theme.background_color == "#f9fafb"
        assert theme.grid_color == "#6b7280"
        assert len(theme.colors) == 5

    def test_dark_preset(self):
        """Test dark theme preset has expected colors."""
        theme = Theme.from_preset("dark")
        assert theme.grid_color == "#9ca3af"
        assert theme.title_color == "#ffffff"
        assert theme.background_color == "#1a1a1a"
        assert len(theme.colors) == 5

    def test_high_contrast_preset(self):
        """Test high-contrast theme preset."""
        theme = Theme.from_preset("high-contrast")
        assert theme.title_color == "#000000"
        assert theme.grid_color == "#000000"
        assert theme.background_color == "#FFFFFF"
        assert len(theme.colors) == 5


class TestThemeCompose:
    """Test Theme.compose() method."""

    def test_compose_with_colors_override(self):
        """Test composing theme with custom colors."""
        base = Theme.from_preset("light")
        custom = base.compose(Theme(colors=["#ff0000", "#00ff00"]))
        assert custom.colors == ["#ff0000", "#00ff00"]
        assert (
            custom.title_color == "#1f2937"
        )  # inherited from light preset, NOT class default

    def test_compose_with_background_color(self):
        """Test composing theme with background color."""
        theme = Theme.from_preset("light").compose(Theme(background_color="#f0f0f0"))
        assert theme.background_color == "#f0f0f0"

    def test_compose_multiple_properties(self):
        """Test composing theme with multiple property overrides."""
        base = Theme.from_preset("dark")
        custom = base.compose(
            Theme(
                colors=["#a00", "#0a0"],
                title_color="#fff",
                legend_position="top-right",
            )
        )
        assert custom.colors == ["#a00", "#0a0"]
        assert custom.title_color == "#fff"
        assert custom.legend_position == "top-right"


class TestThemeCycleColor:
    """Test Theme.cycle_color() method."""

    def test_cycle_through_palette(self):
        """Test cycling through color palette."""
        theme = Theme(colors=["#f00", "#0f0", "#00f"])
        assert theme.cycle_color(0) == "#f00"
        assert theme.cycle_color(1) == "#0f0"
        assert theme.cycle_color(2) == "#00f"

    def test_cycle_wraps_around(self):
        """Test cycling wraps around palette."""
        theme = Theme(colors=["#f00", "#0f0"])
        assert theme.cycle_color(2) == "#f00"  # wraps
        assert theme.cycle_color(3) == "#0f0"
        assert theme.cycle_color(4) == "#f00"

    def test_cycle_with_large_index(self):
        """Test cycling with large index."""
        theme = Theme(colors=["#111", "#222"])
        assert theme.cycle_color(100) == "#111"  # 100 % 2 = 0
        assert theme.cycle_color(101) == "#222"


class TestColorPalette:
    """Test ColorPalette class."""

    def test_from_list(self):
        """Test creating ColorPalette from list."""
        palette = ColorPalette(colors=["#f00", "#0f0", "#00f"])
        assert len(palette.colors) == 3
        assert palette.colors[0] == "#f00"

    def test_get_color(self):
        """Test getting color by index."""
        palette = ColorPalette(colors=["#a", "#b", "#c"])
        assert palette.get_color(0) == "#a"
        assert palette.get_color(2) == "#c"

    def test_get_color_wraps(self):
        """Test get_color wraps around."""
        palette = ColorPalette(colors=["#a", "#b"])
        assert palette.get_color(5) == "#b"  # 5 % 2 = 1

    def test_expand_expands_palette(self):
        """Test expand expands palette if needed."""
        palette = ColorPalette(colors=["#a", "#b"])
        expanded = palette.expand(5)
        assert len(expanded.colors) == 5
        # First two should be original colors
        assert expanded.colors[0] == "#a"
        assert expanded.colors[1] == "#b"

    def test_expand_already_sufficient(self):
        """Test expand returns self if size sufficient."""
        palette = ColorPalette(colors=["#a", "#b", "#c", "#d", "#e"])
        result = palette.expand(3)
        assert result is palette  # Same object

    def test_expand_generates_hsl_colors(self):
        """Test expand generates HSL colors for large palettes."""
        palette = ColorPalette(colors=["#f00"])
        expanded = palette.expand(10)
        assert len(expanded.colors) == 10
        # First should be original, rest should be HSL-generated
        assert expanded.colors[0] == "#f00"
        # Check that generated colors are valid hsl format
        for color in expanded.colors[1:]:
            assert color.startswith("hsl(")


class TestThemeImmutability:
    """Test Theme immutability (frozen dataclass)."""

    def test_cannot_modify_frozen(self):
        """Test that frozen theme cannot be modified."""
        theme = Theme.from_preset("light")
        with pytest.raises(Exception):
            theme.title_color = "#fff"

    def test_compose_returns_new(self):
        """Test compose returns new instance, doesn't modify original."""
        base = Theme.from_preset("light")
        original_title = base.title_color
        custom = base.compose(Theme(title_color="#fff"))
        assert base.title_color == original_title  # unchanged
        assert custom.title_color == "#fff"  # different


class TestHSLSupport:
    """Test HSL color support in Theme."""

    def test_hsl_colors_roundtrip(self):
        """Test that HSL colors roundtrip through to_dict/from_dict."""
        # Create theme with HSL palette entries (using dark colors for contrast)
        theme = Theme(
            colors=["#ff0000", "hsl(120, 70%, 30%)", "hsla(240, 60%, 20%, 0.8)"],
            legend_font_color="hsl(30, 80%, 30%)",
        )

        # Convert to dict and back
        theme_dict = vars(theme)
        restored_theme = Theme(**theme_dict)

        # Verify HSL colors are preserved
        assert restored_theme.colors[0] == "#ff0000"
        assert restored_theme.colors[1] == "hsl(120, 70%, 30%)"
        assert restored_theme.colors[2] == "hsla(240, 60%, 20%, 0.8)"
        assert restored_theme.legend_font_color == "hsl(30, 80%, 30%)"


class TestLegendContrastValidation:
    """Test legend contrast validation."""

    def test_low_contrast_legend_raises(self):
        """Test that low contrast between legend and background raises error."""
        # Same color for legend and background = zero contrast
        with pytest.raises(ValueError) as exc_info:
            Theme(
                colors=["#ff0000"],
                legend_font_color="#FFFFFF",
                background_color="#FFFFFF",  # Same as legend = no contrast
            )

        assert "contrast" in str(exc_info.value).lower()

    def test_adequate_contrast_passes(self):
        """Test that adequate contrast passes validation."""
        # Black legend on white background = high contrast
        theme = Theme(
            colors=["#ff0000"],
            legend_font_color="#000000",
            background_color="#FFFFFF",
        )
        assert theme.legend_font_color == "#000000"
        assert theme.background_color == "#FFFFFF"
