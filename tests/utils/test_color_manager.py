"""Tests for charted.utils.color_manager module."""

from charted.utils.color_manager import ColorManager


class TestColorManagerGetColor:
    """Test ColorManager.get_color() method."""

    def test_get_first_color(self):
        """Test getting first color."""
        manager = ColorManager(colors=["#f00", "#0f0", "#00f"])
        assert manager.get_color(0) == "#f00"

    def test_get_color_cycling(self):
        """Test color cycling."""
        manager = ColorManager(colors=["#a", "#b"])
        assert manager.get_color(0) == "#a"
        assert manager.get_color(1) == "#b"
        assert manager.get_color(2) == "#a"  # cycles
        assert manager.get_color(3) == "#b"

    def test_default_fallback(self):
        """Test default fallback when no colors provided."""
        manager = ColorManager()
        assert manager.get_color(0) == "#5fab9e"


class TestColorManagerEnsurePaletteSize:
    """Test ColorManager.ensure_palette_size() method."""

    def test_expands_small_palette(self):
        """Test expanding small palette."""
        manager = ColorManager(colors=["#f00"])
        expanded = manager.ensure_palette_size(5)
        assert len(expanded) == 5
        assert expanded[0] == "#f00"
        # Should have generated 4 more HSL colors
        for color in expanded[1:]:
            assert color.startswith("hsl(")

    def test_returns_copy_when_sufficient(self):
        """Test returns copy when size sufficient."""
        manager = ColorManager(colors=["#a", "#b", "#c"])
        result = manager.ensure_palette_size(2)
        assert result == ["#a", "#b", "#c"]  # Same content
        assert result is not manager._colors  # Different object


class TestColorManagerHSLGeneration:
    """Test HSL color generation."""

    def test_generates_distinct_colors(self):
        """Test generates distinct colors for large palette."""
        manager = ColorManager()
        colors = manager.generate_hsl_colors(10)
        assert len(colors) == 10
        # All should be valid HSL format
        for color in colors:
            assert color.startswith("hsl(")

    def test_spread_colors_across_hue(self):
        """Test colors are spread across hue spectrum."""
        manager = ColorManager()
        colors = manager.generate_hsl_colors(6)
        # With 6 colors at 60 degree intervals
        assert "hsl(0, 70%, 50%)" in colors
        assert "hsl(60, 70%, 50%)" in colors


class TestColorManagerContrast:
    """Test contrast validation methods."""

    def test_calculate_contrast_ratio_black_white(self):
        """Test black on white has highest ratio."""
        manager = ColorManager()
        ratio = manager.validate_contrast("#000000", "#ffffff")
        assert ratio == 21.0  # Maximum possible is ~21:1

    def test_calculate_contrast_similar_colors(self):
        """Test similar colors have low ratio."""
        manager = ColorManager()
        ratio = manager.validate_contrast("#aaaaaa", "#bbbbbb")
        assert ratio < 2  # Very similar colors

    def test_validate_contrast_passes(self):
        """Test passing contrast validation - returns ratio."""
        manager = ColorManager()
        ratio = manager.validate_contrast("#000000", "#ffffff")
        assert ratio >= 4.5  # Passes minimum 4.5

    def test_validate_contrast_fails(self):
        """Test failing contrast validation."""
        manager = ColorManager()
        ratio = manager.validate_contrast("#eeeeee", "#ffffff")
        assert ratio < 4.5  # Fails minimum


class TestColorManagerValidateTheme:
    """Test ColorManager.validate_theme() method."""

    def test_valid_theme_no_warnings(self):
        """Test valid theme produces no warnings."""
        manager = ColorManager()
        from charted import Theme

        theme = Theme.from_preset("light")
        warnings = manager.validate_theme(theme)
        assert warnings == []

    def test_dark_title_on_dark_background_warns(self):
        """Test warning for dark title on dark background."""
        manager = ColorManager()
        from charted import Theme

        theme = Theme(
            title_color="#111111",
            background_color="#222222",
            legend_font_color="#ffffff",  # White for contrast with dark bg
            colors=["#f00"],
        )
        warnings = manager.validate_theme(theme)
        assert len(warnings) > 0
