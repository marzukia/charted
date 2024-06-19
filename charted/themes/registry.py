"""Theme registration and management for charted."""

from charted.themes.core import Theme

# Registered themes storage
_registered_themes: dict[str, Theme] = {}

# Default theme name
_default_theme_name: str = "light"


def register_theme(name: str, theme: Theme) -> None:
    """Register a custom theme by name.

    Registered themes can be used like presets:

    ```python
    from charted import register_theme, Theme

    register_theme("corporate", Theme(colors=["#1a365d", "#2b6cb0"]))
    chart = BarChart(data=[1, 2, 3], labels=["a", "b", "c"], theme="corporate")
    ```

    Args:
        name: Unique identifier for the theme.
        theme: Theme instance to register.
    """
    if not name or not name.strip():
        raise ValueError("Theme name cannot be empty")
    _registered_themes[name] = theme


def list_themes() -> list[str]:
    """List all available theme names.

    Returns:
        List of registered theme names (presets + custom).
    """
    return sorted(list(_registered_themes.keys()))


def get_theme(name: str) -> Theme:
    """Get a theme by name.

    Args:
        name: Theme name (preset or registered).

    Returns:
        Theme instance.

    Raises:
        ValueError: If theme is not found.
    """
    if name in _registered_themes:
        return _registered_themes[name].__copy__()
    raise ValueError(f"Theme not found: {name!r}")


def get_default_theme() -> str:
    """Get the current default theme name.

    Returns:
        Default theme name (e.g., "light").
    """
    return _default_theme_name


def set_default_theme(name: str) -> None:
    """Set the default theme for new charts.

    Args:
        name: Theme name to use as default.
    """
    if name not in _registered_themes:
        # Allow preset names even if not registered
        from charted.themes.core import Theme

        Theme.from_preset(name)  # Validate it exists
    global _default_theme_name
    _default_theme_name = name
