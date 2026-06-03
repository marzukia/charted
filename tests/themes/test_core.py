"""Tests for charted.themes.core module."""

import pytest

from charted.themes.core import NAMED_PALETTES, ColorPalette, Theme, resolve_palette


class TestThemePreset:
    """Test Theme.from_preset() method."""

    def test_light_preset(self):
        """Light theme preset has expected colors."""
        theme = Theme.from_preset("light")
        assert theme.title_color == "#1f2937"
        assert theme.background_color == "#f9fafb"
        assert theme.grid_color == "#6b7280"
        assert len(theme.colors) == 5

    def test_dark_preset(self):
        """Dark theme preset has expected colors."""
        theme = Theme.from_preset("dark")
        assert theme.grid_color == "#9ca3af"
        assert theme.title_color == "#ffffff"
        assert theme.background_color == "#1a1a1a"
        assert len(theme.colors) == 5

    def test_high_contrast_preset(self):
        """High-contrast theme preset."""
        theme = Theme.from_preset("high-contrast")
        assert theme.title_color == "#000000"
        assert theme.grid_color == "#000000"
        assert theme.background_color == "#FFFFFF"
        # High-contrast now uses the Okabe-Ito colourblind-safe palette.
        assert len(theme.colors) == 8

    def test_unknown_preset_raises(self):
        """Unknown preset raises ValueError."""
        with pytest.raises(ValueError, match="Unknown theme"):
            Theme.from_preset("nonexistent")


class TestThemeCompose:
    """Test Theme.compose() method."""

    def test_compose_with_colors_override(self):
        """Composing theme with custom colors."""
        base = Theme.from_preset("light")
        custom = base.compose(Theme(colors=["#ff0000", "#00ff00"]))
        assert custom.colors == ["#ff0000", "#00ff00"]
        assert custom.title_color == "#1f2937"  # inherited from light preset

    def test_compose_with_background_color(self):
        """Composing theme with background color."""
        theme = Theme.from_preset("light").compose(Theme(background_color="#f0f0f0"))
        assert theme.background_color == "#f0f0f0"

    def test_compose_multiple_properties(self):
        """Composing theme with multiple overrides."""
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

    def test_compose_none_returns_copy(self):
        """compose(None) returns a copy."""
        base = Theme.from_preset("light")
        result = base.compose(None)
        assert result is not base
        assert result.title_color == base.title_color

    def test_compose_empty_colors_list(self):
        """Compose with empty colors list keeps base colors."""
        base = Theme.from_preset("light")
        custom = base.compose(Theme(colors=[]))
        # Empty list should not override
        assert custom.colors == base.colors

    def test_compose_with_default_values_skipped(self):
        """Values matching class defaults are skipped during compose."""
        base = Theme.from_preset("light")
        # Compose with a theme that has default values for all fields
        default_theme = Theme()
        custom = base.compose(default_theme)
        # Should return a copy of base unchanged
        assert custom.title_color == base.title_color

    def test_compose_no_new_values_returns_copy(self):
        """When no new values, returns copy of base."""
        base = Theme.from_preset("light")
        same = Theme(colors=["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899"])
        custom = base.compose(same)
        assert custom is not base

    def test_compose_immutability(self):
        """Original theme is not modified by compose."""
        base = Theme.from_preset("light")
        original_colors = base.colors.copy()
        base.compose(Theme(title_color="#fff"))
        assert base.colors == original_colors


class TestThemeCycleColor:
    """Test Theme.cycle_color() method."""

    def test_cycle_through_palette(self):
        """Cycling through color palette."""
        theme = Theme(colors=["#f00", "#0f0", "#00f"])
        assert theme.cycle_color(0) == "#f00"
        assert theme.cycle_color(1) == "#0f0"
        assert theme.cycle_color(2) == "#00f"

    def test_cycle_wraps_around(self):
        """Cycling wraps around palette."""
        theme = Theme(colors=["#f00", "#0f0"])
        assert theme.cycle_color(2) == "#f00"
        assert theme.cycle_color(3) == "#0f0"
        assert theme.cycle_color(4) == "#f00"

    def test_cycle_with_large_index(self):
        """Cycling with large index."""
        theme = Theme(colors=["#111", "#222"])
        assert theme.cycle_color(100) == "#111"
        assert theme.cycle_color(101) == "#222"


class TestColorPalette:
    """Test ColorPalette class."""

    def test_from_list(self):
        """Creating ColorPalette from list."""
        palette = ColorPalette(colors=["#f00", "#0f0", "#00f"])
        assert len(palette.colors) == 3
        assert palette.colors[0] == "#f00"

    def test_get_color(self):
        """Getting color by index."""
        palette = ColorPalette(colors=["#a", "#b", "#c"])
        assert palette.get_color(0) == "#a"
        assert palette.get_color(2) == "#c"

    def test_get_color_wraps(self):
        """get_color wraps around."""
        palette = ColorPalette(colors=["#a", "#b"])
        assert palette.get_color(5) == "#b"

    def test_expand_expands_palette(self):
        """Expand expands palette if needed."""
        palette = ColorPalette(colors=["#a", "#b"])
        expanded = palette.expand(5)
        assert len(expanded.colors) == 5
        assert expanded.colors[0] == "#a"
        assert expanded.colors[1] == "#b"

    def test_expand_already_sufficient(self):
        """Expand returns self if size sufficient."""
        palette = ColorPalette(colors=["#a", "#b", "#c", "#d", "#e"])
        result = palette.expand(3)
        assert result is palette

    def test_expand_generates_hsl_colors(self):
        """Expand generates HSL colors for large palettes."""
        palette = ColorPalette(colors=["#f00"])
        expanded = palette.expand(10)
        assert len(expanded.colors) == 10
        assert expanded.colors[0] == "#f00"
        for color in expanded.colors[1:]:
            assert color.startswith("hsl(")


class TestThemeImmutability:
    """Test Theme immutability (frozen dataclass)."""

    def test_cannot_modify_frozen(self):
        """Frozen theme cannot be modified."""
        theme = Theme.from_preset("light")
        with pytest.raises(Exception):
            theme.title_color = "#fff"

    def test_compose_returns_new(self):
        """Compose returns new instance, doesn't modify original."""
        base = Theme.from_preset("light")
        original_title = base.title_color
        custom = base.compose(Theme(title_color="#fff"))
        assert base.title_color == original_title
        assert custom.title_color == "#fff"


class TestHSLSupport:
    """Test HSL color support in Theme."""

    def test_hsl_colors_roundtrip(self):
        """HSL colors roundtrip through to_dict/from_dict."""
        theme = Theme(
            colors=["#ff0000", "hsl(120, 70%, 30%)", "hsla(240, 60%, 20%, 0.8)"],
            legend_font_color="hsl(30, 80%, 30%)",
        )
        theme_dict = vars(theme)
        restored_theme = Theme(**theme_dict)
        assert restored_theme.colors[0] == "#ff0000"
        assert restored_theme.colors[1] == "hsl(120, 70%, 30%)"
        assert restored_theme.colors[2] == "hsla(240, 60%, 20%, 0.8)"
        assert restored_theme.legend_font_color == "hsl(30, 80%, 30%)"


class TestLegendContrastValidation:
    """Test legend contrast validation."""

    def test_low_contrast_legend_raises(self):
        """Low contrast between legend and background raises error."""
        with pytest.raises(ValueError) as exc_info:
            Theme(
                colors=["#ff0000"],
                legend_font_color="#FFFFFF",
                background_color="#FFFFFF",
            )
        assert "contrast" in str(exc_info.value).lower()

    def test_adequate_contrast_passes(self):
        """Adequate contrast passes validation."""
        theme = Theme(
            colors=["#ff0000"],
            legend_font_color="#000000",
            background_color="#FFFFFF",
        )
        assert theme.legend_font_color == "#000000"
        assert theme.background_color == "#FFFFFF"


class TestNamedPalettes:
    """Test NAMED_PALETTES constant."""

    def test_default_palette(self):
        """Default palette exists."""
        assert "default" in NAMED_PALETTES
        assert len(NAMED_PALETTES["default"]) == 5

    def test_all_palettes_have_colors(self):
        """All palettes have non-empty color lists."""
        for name, colors in NAMED_PALETTES.items():
            assert len(colors) >= 1, f"{name} palette is empty"

    def test_viridis_palette(self):
        """Viridis palette exists and has expected colors."""
        assert "viridis" in NAMED_PALETTES
        assert len(NAMED_PALETTES["viridis"]) == 5

    def test_categorical_palette(self):
        """Categorical palette has 10 colors."""
        assert "categorical" in NAMED_PALETTES
        assert len(NAMED_PALETTES["categorical"]) == 10

    def test_known_palettes(self):
        """All expected palettes are present."""
        expected = {
            "default",
            "viridis",
            "ocean",
            "categorical",
            "rainbow",
            "monochrome",
            "pastel",
            "sunset",
            "forest",
            "inferno",
        }
        assert expected.issubset(set(NAMED_PALETTES.keys()))


class TestResolvePalette:
    """Test resolve_palette() function."""

    def test_none_returns_default(self):
        """None returns default palette copy."""
        colors = resolve_palette(None)
        assert colors == NAMED_PALETTES["default"]

    def test_none_returns_copy(self):
        """None returns a copy, not the original list."""
        colors = resolve_palette(None)
        colors.append("#000")
        # Should not modify the original
        assert len(NAMED_PALETTES["default"]) == 5

    def test_list_passthrough(self):
        """List is passed through as-is."""
        colors = resolve_palette(["#a", "#b"])
        assert colors == ["#a", "#b"]

    def test_list_returns_copy(self):
        """List returns a copy."""
        original = ["#a", "#b"]
        result = resolve_palette(original)
        result.append("#c")
        assert len(original) == 2

    def test_named_palette(self):
        """Named palette returns a copy of its colors."""
        colors = resolve_palette("viridis")
        assert colors == NAMED_PALETTES["viridis"]

    def test_named_palette_returns_copy(self):
        """Named palette returns a copy."""
        colors = resolve_palette("viridis")
        colors.append("#000")
        assert len(NAMED_PALETTES["viridis"]) == 5

    def test_unknown_palette_raises(self):
        """Unknown palette name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown palette"):
            resolve_palette("nonexistent")
