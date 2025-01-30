"""Tests for charted.utils.theme_manager module."""

import pytest

from charted.themes.core import Theme
from charted.utils.theme_manager import ThemeManager, _dict_to_theme


class TestThemeManagerLoadTheme:
    """Test ThemeManager.load_theme() method."""

    def test_load_theme_none_returns_default(self):
        """Test loading theme with None returns default Theme."""
        theme = ThemeManager.load_theme(None)

        assert isinstance(theme, Theme)
        assert theme.colors == ["#5fab9e", "#f58b51", "#f7dd72", "#db504a", "#2e4756"]

    def test_load_theme_with_preset_name(self):
        """Test loading theme with preset name string."""
        theme = ThemeManager.load_theme("light")

        assert isinstance(theme, Theme)
        assert theme.background_color == "#f9fafb"

    def test_load_theme_with_dark_preset(self):
        """Test loading dark preset."""
        theme = ThemeManager.load_theme("dark")

        assert isinstance(theme, Theme)
        assert theme.background_color == "#1a1a1a"
        assert theme.title_color == "#ffffff"

    def test_load_theme_with_theme_object(self):
        """Test loading theme with Theme object returns same object."""
        custom_theme = Theme(
            colors=["#FF0000"], background_color="#000000", legend_font_color="#ffffff"
        )
        theme = ThemeManager.load_theme(custom_theme)

        assert theme is custom_theme
        assert theme.colors == ["#FF0000"]

    def test_load_theme_with_dict_backward_compatibility(self):
        """Test loading theme with dict for backward compatibility."""
        theme_dict = {"colors": ["#F00", "#0F0"], "background_color": "#FFF"}
        theme = ThemeManager.load_theme(theme_dict)

        assert isinstance(theme, Theme)
        assert theme.colors == ["#F00", "#0F0"]
        assert theme.background_color == "#FFF"

    def test_load_theme_with_chart_type_overrides(self):
        """Test loading theme applies chart-type overrides when config has overrides."""
        from unittest.mock import patch

        # Mock the config loading to return a config with bar chart overrides
        mock_config = {"bar": {"colors": ["#00F"], "title_color": "#F00"}}

        with patch("charted.config.load_config", return_value=mock_config):
            with patch("charted.config.get_chart_theme") as mock_get:
                mock_get.return_value = {"colors": ["#00F"], "title_color": "#F00"}

                theme = ThemeManager.load_theme(None, "bar")

                assert theme.colors == ["#00F"]
                assert theme.title_color == "#F00"

    def test_load_theme_invalid_preset_raises(self):
        """Test loading theme with invalid preset name raises ValueError."""
        with pytest.raises(ValueError, match="Theme not found"):
            ThemeManager.load_theme("invalid_preset_name")


class TestDictToTheme:
    """Test _dict_to_theme() helper function."""

    def test_dict_to_theme_valid_fields(self):
        """Test converting valid dict to Theme."""
        data = {
            "colors": ["#F00", "#0F0", "#00F"],
            "background_color": "#FFFFFF",
            "title_color": "#000000",
            "grid_color": "#CCCCCC",
        }

        theme = _dict_to_theme(data)

        assert isinstance(theme, Theme)
        assert theme.colors == ["#F00", "#0F0", "#00F"]
        assert theme.background_color == "#FFFFFF"
        assert theme.title_color == "#000000"
        assert theme.grid_color == "#CCCCCC"

    def test_dict_to_theme_partial_fields(self):
        """Test converting dict with only some fields."""
        data = {"colors": ["#F00"]}

        theme = _dict_to_theme(data)

        assert isinstance(theme, Theme)
        assert theme.colors == ["#F00"]
        # Other fields should have defaults
        assert theme.background_color == "#FFFFFF"

    def test_dict_to_theme_invalid_field_raises(self):
        """Test converting dict with invalid field raises ValueError."""
        data = {"invalid_field": "value", "colors": ["#F00"]}

        with pytest.raises(ValueError, match="Unknown theme field"):
            _dict_to_theme(data)

    def test_dict_to_theme_empty_dict(self):
        """Test converting empty dict returns Theme with defaults."""
        theme = _dict_to_theme({})

        assert isinstance(theme, Theme)
        # Should have all default values
        assert theme.colors == ["#5fab9e", "#f58b51", "#f7dd72", "#db504a", "#2e4756"]

    def test_dict_to_theme_with_all_valid_fields(self):
        """Test converting dict with all valid Theme fields."""
        data = {
            "colors": ["#F00"],
            "grid_color": "#CCC",
            "grid_dasharray": "2,2",
            "grid_visible": False,
            "legend_position": "bottom",
            "legend_font_size": 12,
            "legend_font_family": "Helvetica",
            "title_color": "#333",
            "title_font_size": 18,
            "title_font_family": "Verdana",
            "background_color": "#EEE",
            "h_padding": 0.1,
            "v_padding": 0.1,
            "marker_size": 5.0,
        }

        theme = _dict_to_theme(data)

        assert theme.grid_dasharray == "2,2"
        assert theme.grid_visible is False
        assert theme.legend_position == "bottom"
        assert theme.title_font_size == 18

    def test_dict_to_theme_ignores_extra_keys(self):
        """Test that dict_to_theme only uses valid Theme fields."""
        # This should raise because invalid_field is not valid
        data = {"colors": ["#F00"], "unknown_key": "value"}

        with pytest.raises(ValueError):
            _dict_to_theme(data)


class TestThemeManagerEdgeCases:
    """Test edge cases for ThemeManager."""

    def test_load_theme_with_high_contrast_preset(self):
        """Test loading high-contrast preset."""
        theme = ThemeManager.load_theme("high-contrast")

        assert theme.background_color == "#FFFFFF"
        assert theme.title_color == "#000000"
        assert theme.grid_color == "#000000"

    def test_load_theme_dict_with_nested_keys_ignored(self):
        """Test that nested dict keys are handled correctly."""
        # Nested structures should be rejected or ignored
        data = {"colors": ["#F00"], "nested": {"key": "value"}}

        with pytest.raises(ValueError):
            _dict_to_theme(data)

    def test_load_theme_preserves_theme_immutability(self):
        """Test that loading a Theme doesn't modify the original."""
        original = Theme(colors=["#F00"])
        original_colors = original.colors.copy()

        theme = ThemeManager.load_theme(original)

        assert original.colors == original_colors  # Unchanged
        assert theme is original  # Returns same reference
