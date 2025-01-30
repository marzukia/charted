"""Tests for charted.utils.config_schema."""

from charted.utils.config_schema import (
    validate_config,
    validate_theme_dict,
)


class TestThemeSchema:
    """Test theme schema validation."""

    def test_validate_valid_theme(self):
        """Test validation of valid theme."""
        theme = {
            "colors": ["#ff0000", "#00ff00"],
            "grid_color": "#CCCCCC",
        }
        is_valid, errors = validate_theme_dict(theme)
        assert is_valid
        assert len(errors) == 0

    def test_validate_invalid_colors(self):
        """Test validation with invalid colors."""
        theme = {"colors": ["red", "green"]}
        is_valid, errors = validate_theme_dict(theme)
        assert not is_valid
        assert any("hex" in e for e in errors)

    def test_validate_numeric_ranges(self):
        """Test validation of numeric ranges."""
        theme = {"h_padding": 0.6}
        is_valid, errors = validate_theme_dict(theme)
        assert not is_valid
        assert any("between" in e for e in errors)


class TestConfigValidation:
    """Test full config validation."""

    def test_validate_valid_config(self):
        """Test validation of valid config."""
        config = {
            "theme_section": {"colors": ["#ff0000"]},
        }
        is_valid, errors = validate_config(config)
        assert is_valid
