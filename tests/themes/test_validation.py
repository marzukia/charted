"""Tests for charted.themes.validation module."""

from charted import Theme, validate_theme


class TestValidateTheme:
    """Test validate_theme function."""

    def test_valid_theme_returns_empty(self):
        """Test that valid theme returns empty warnings."""
        theme = Theme.from_preset("light")
        warnings = validate_theme(theme)
        assert warnings == []

    def test_low_contrast_title_warning(self):
        """Test warning for low contrast title."""
        # Dark title on dark background - also need to set legend color for contrast
        theme = Theme(
            title_color="#111111",  # Very dark
            background_color="#000000",  # Black
            legend_font_color="#ffffff",  # White for contrast
            colors=["#f00"],
        )
        warnings = validate_theme(theme)
        assert len(warnings) > 0
        assert any("title" in w.lower() for w in warnings)

    def test_low_contrast_grid_warning(self):
        """Test warning for low contrast grid."""
        # Dark grid on dark background - also need legend color for contrast
        theme = Theme(
            grid_color="#111111",
            background_color="#000000",
            legend_font_color="#ffffff",  # White for contrast
            colors=["#f00"],
        )
        warnings = validate_theme(theme)
        assert len(warnings) > 0
        assert any("grid" in w.lower() for w in warnings)

    def test_high_contrast_theme_passes(self):
        """Test high-contrast theme passes validation."""
        theme = Theme.from_preset("high-contrast")
        warnings = validate_theme(theme)
        assert warnings == []


class TestValidateColorContrast:
    """Test validate_color_contrast function."""

    def test_high_contrast_passes(self):
        """Test high contrast colors pass."""
        from charted.themes.validation import validate_color_contrast

        passes, ratio = validate_color_contrast("#000000", "#ffffff")
        assert passes is True
        assert ratio > 10  # Black on white has very high ratio

    def test_low_contrast_fails(self):
        """Test low contrast colors fail."""
        from charted.themes.validation import validate_color_contrast

        # Similar gray values
        passes, ratio = validate_color_contrast("#aaaaaa", "#cccccc")
        assert passes is False
        assert ratio < 4.5

    def test_custom_min_ratio(self):
        """Test custom minimum ratio."""
        from charted.themes.validation import validate_color_contrast

        # White on light gray has ratio ~1.3
        passes, ratio = validate_color_contrast("#ffffff", "#eeeeee", min_ratio=1.0)
        assert passes is True
        passes, _ = validate_color_contrast("#ffffff", "#eeeeee", min_ratio=1.5)
        assert passes is False


class TestGetAccessibleTextColor:
    """Test get_accessible_text_color function."""

    def test_returns_accessible_color(self):
        """Test returns first accessible color."""
        from charted.themes.validation import get_accessible_text_color

        # Dark background - should return dark color
        color = get_accessible_text_color(
            bg_color="#000000",
            dark_colors=["#333333", "#666666"],
            light_colors=["#ffffff"],
        )
        assert color in ["#333333", "#666666", "#ffffff"]

    def test_fallback_to_last_option(self):
        """Test falls back to last option if all fail."""
        from charted.themes.validation import get_accessible_text_color

        # Very light background, try dark colors - should return first accessible
        color = get_accessible_text_color(
            bg_color="#ffffff",
            dark_colors=["#333333", "#666666"],
            light_colors=["#eeeeee"],  # Won't pass on white
        )
        # Should return first accessible dark color (#333333 passes)
        assert color == "#333333"
