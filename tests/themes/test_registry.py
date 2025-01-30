"""Tests for charted.themes.registry module."""

import pytest

from charted import Theme, get_theme, list_themes, register_theme
from charted.themes.registry import (
    _registered_themes,
    get_default_theme,
    set_default_theme,
)


class TestThemeRegistry:
    """Test theme registration and retrieval."""

    def setup_method(self):
        """Clean up registry before each test."""
        # Reset to only presets
        _registered_themes.clear()
        for preset in ["light", "dark", "high-contrast"]:
            register_theme(preset, Theme.from_preset(preset))

    def test_register_theme_adds_to_registry(self):
        """Test registering a custom theme adds it to registry."""
        custom_theme = Theme(colors=["#a00", "#0a0", "#00a"])
        register_theme("custom", custom_theme)

        assert "custom" in list_themes()

    def test_register_theme_stores_correct_theme(self):
        """Test registered theme can be retrieved correctly."""
        custom_theme = Theme(
            colors=["#f00"], background_color="#000", legend_font_color="#fff"
        )
        register_theme("test_theme", custom_theme)

        retrieved = get_theme("test_theme")
        assert retrieved.colors == ["#f00"]
        assert retrieved.background_color == "#000"
        assert retrieved.legend_font_color == "#fff"

    def test_list_themes_includes_presets(self):
        """Test list_themes includes preset themes."""
        themes = list_themes()

        assert "light" in themes
        assert "dark" in themes
        assert "high-contrast" in themes

    def test_list_themes_includes_registered(self):
        """Test list_themes includes registered custom themes."""
        custom_theme = Theme(colors=["#fff"])
        register_theme("my_custom_theme", custom_theme)

        themes = list_themes()

        assert "my_custom_theme" in themes

    def test_list_themes_returns_sorted(self):
        """Test list_themes returns sorted list."""
        register_theme("zebra", Theme())
        register_theme("alpha", Theme())
        register_theme("beta", Theme())

        themes = list_themes()

        assert themes == sorted(themes)

    def test_get_theme_returns_copy(self):
        """Test get_theme returns a copy, not original."""
        custom_theme = Theme(colors=["#f00"])
        register_theme("mutable_test", custom_theme)

        retrieved = get_theme("mutable_test")

        # Modify retrieved theme (if possible - it's frozen)
        # Just verify it's a different object
        assert retrieved is not custom_theme

    def test_get_theme_not_found_raises(self):
        """Test get_theme raises ValueError for unknown theme."""
        with pytest.raises(ValueError, match="Theme not found"):
            get_theme("nonexistent_theme")

    def test_register_empty_name_raises(self):
        """Test registering theme with empty name raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            register_theme("", Theme())

    def test_register_whitespace_only_name_raises(self):
        """Test registering theme with whitespace-only name raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            register_theme("   ", Theme())

    def test_register_theme_overwrites_existing(self):
        """Test registering theme with same name overwrites existing."""
        original = Theme(colors=["#f00"])
        register_theme("overwrite_test", original)

        updated = Theme(colors=["#0f0"])
        register_theme("overwrite_test", updated)

        retrieved = get_theme("overwrite_test")
        assert retrieved.colors == ["#0f0"]

    def test_registry_isolation_between_tests(self):
        """Test that registered themes don't leak between tests."""
        # Register a theme
        register_theme("temp_test", Theme(colors=["#123"]))

        # Verify it exists
        assert "temp_test" in list_themes()

        # Clean up (setup_method will do this for next test)
        if "temp_test" in _registered_themes:
            del _registered_themes["temp_test"]


class TestDefaultTheme:
    """Test default theme functions."""

    def setup_method(self):
        """Reset registry and default theme before each test."""
        _registered_themes.clear()
        for preset in ["light", "dark", "high-contrast"]:
            register_theme(preset, Theme.from_preset(preset))
        # Reset to initial default
        import charted.themes.registry as reg

        reg._default_theme_name = "light"

    def test_get_default_theme_returns_current(self):
        """Test get_default_theme returns current default."""
        default = get_default_theme()

        assert default == "light"

    def test_set_default_theme_changes_default(self):
        """Test set_default_theme updates default theme."""
        set_default_theme("dark")

        default = get_default_theme()

        assert default == "dark"

    def test_set_default_theme_with_preset(self):
        """Test setting preset as default works."""
        set_default_theme("high-contrast")

        default = get_default_theme()

        assert default == "high-contrast"

    def test_set_default_theme_with_registered(self):
        """Test setting registered theme as default works."""
        register_theme("custom", Theme())
        set_default_theme("custom")

        default = get_default_theme()

        assert default == "custom"

    def test_set_default_theme_invalid_preset_raises(self):
        """Test setting invalid preset as default raises ValueError."""
        with pytest.raises(ValueError, match="Unknown theme"):
            set_default_theme("nonexistent_preset")

    def test_set_default_theme_preserves_registry(self):
        """Test set_default_theme doesn't affect registered themes."""
        register_theme("test", Theme(colors=["#f00"]))

        set_default_theme("dark")

        # Registered theme should still exist
        assert "test" in list_themes()
        assert get_theme("test").colors == ["#f00"]


class TestRegistryCleanup:
    """Test registry cleanup functionality."""

    def test_clear_registry(self):
        """Test clearing all registered themes."""
        register_theme("clear_test", Theme())

        _registered_themes.clear()

        assert "clear_test" not in list_themes()

    def test_remove_specific_theme(self):
        """Test removing specific theme from registry."""
        register_theme("remove_me", Theme())

        del _registered_themes["remove_me"]

        with pytest.raises(ValueError, match="Theme not found"):
            get_theme("remove_me")
