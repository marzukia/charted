"""Tests for theme loading and utilities."""

from charted.utils.themes import (
    Theme,
    DEFAULT_THEME,
    PRESET_THEMES,
    DARK_THEME,
    LIGHT_THEME,
    HIGH_CONTRAST_THEME,
)


class TestThemeLoadingHappyPath:
    """Test happy path scenarios for theme loading."""

    def test_load_default_theme(self):
        """Test loading the default theme."""
        theme = Theme.load(None)
        assert "colors" in theme
        assert "legend" in theme
        assert "title" in theme

    def test_load_custom_theme_dict(self):
        """Test loading a custom theme dict."""
        custom = {"colors": ["#FF0000", "#00FF00"]}
        theme = Theme.load(custom)
        assert theme["colors"] == ["#FF0000", "#00FF00"]

    def test_merge_themes(self):
        """Test merging two themes."""
        custom = {"colors": ["#FF0000"], "title": {"font_size": 20}}
        theme = Theme.load(custom)
        assert theme["colors"] == ["#FF0000"]
        assert theme["title"]["font_size"] == 20
        assert "font_family" in theme["title"]

    def test_get_required_colors(self):
        """Test that required colors are present."""
        theme = Theme.load(None)
        assert "colors" in theme
        assert len(theme["colors"]) > 0


class TestPresetThemes:
    """Test preset theme loading."""

    def test_load_dark_theme(self):
        """Test loading dark preset theme."""
        theme = Theme.load("dark")
        assert theme["title"]["font_color"] == "#E0E0E0"
        assert theme["v_grid"]["stroke"] == "#444444"
        assert "#5fab9e" in theme["colors"]

    def test_load_light_theme(self):
        """Test loading light preset theme."""
        theme = Theme.load("light")
        assert theme["title"]["font_color"] == "#333333"
        assert theme["v_grid"]["stroke"] == "#E0E0E0"
        assert "#2e7d32" in theme["colors"]

    def test_load_high_contrast_theme(self):
        """Test loading high-contrast preset theme."""
        theme = Theme.load("high-contrast")
        assert theme["title"]["font_color"] == "#000000"
        assert theme["v_grid"]["stroke"] == "#000000"
        assert "#000000" in theme["colors"]

    def test_preset_themes_dict(self):
        """Test PRESET_THEMES dictionary contains all presets."""
        assert "dark" in PRESET_THEMES
        assert "light" in PRESET_THEMES
        assert "high-contrast" in PRESET_THEMES
        assert PRESET_THEMES["dark"] == DARK_THEME
        assert PRESET_THEMES["light"] == LIGHT_THEME
        assert PRESET_THEMES["high-contrast"] == HIGH_CONTRAST_THEME


class TestThemeLoadingSadPath:
    """Test edge cases for theme loading."""

    def test_empty_theme_dict(self):
        """Test loading empty theme dict returns defaults."""
        theme = Theme.load({})
        assert "colors" in theme
        assert "legend" in theme

    def test_partial_theme_merges_with_defaults(self):
        """Test partial theme merges with defaults."""
        partial = {"colors": ["#000000"]}
        theme = Theme.load(partial)
        assert theme["colors"] == ["#000000"]
        assert "legend" in theme

    def test_load_with_none(self):
        """Test loading with None returns default theme."""
        theme = Theme.load(None)
        assert theme == DEFAULT_THEME
        assert "colors" in theme
        assert "legend" in theme
