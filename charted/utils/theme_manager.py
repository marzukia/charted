"""Theme management for charted charts.

Extracted from Chart class to reduce coupling and improve testability.
This module encapsulates all theme loading and merging logic.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from charted.themes.core import Theme


class ThemeManager:
    """Handles theme loading, merging, and chart-type overrides.

    Replaces theme loading logic scattered in Chart.__init__ with a
    focused component that manages theme configuration.

    Attributes:
        None (stateless utility class)

    Example:
        >>> from charted.utils.theme_manager import ThemeManager
        >>> theme = ThemeManager.load_theme(None, "bar")
    """

    @staticmethod
    def load_theme(
        theme: "Theme | str | dict[str, object] | None",
        chart_type: str | None = None,
    ) -> "Theme":
        """Load base theme and apply chart-type overrides.

        Args:
            theme: Base theme to start with (Theme object, preset name string,
                   dict of properties, or None).
            chart_type: Chart type for applying overrides (e.g., 'bar', 'line').

        Returns:
            Merged theme configuration with chart-type overrides applied.

        Example:
            >>> from charted.utils.theme_manager import ThemeManager
            >>> # Load default theme
            >>> theme = ThemeManager.load_theme(None)
            >>> # Load theme with bar chart overrides
            >>> theme = ThemeManager.load_theme(None, "bar")
            >>> # Load preset by name
            >>> theme = ThemeManager.load_theme("dark")
        """
        from charted.config import get_chart_theme, load_config
        from charted.themes.core import Theme

        # Resolve theme to Theme object
        if isinstance(theme, str):
            # Treat as preset name or registered theme name
            try:
                base_theme = Theme.from_preset(theme)
            except ValueError:
                from charted.themes.registry import get_theme

                base_theme = get_theme(theme)
        elif theme is None:
            base_theme = Theme()
        elif isinstance(theme, dict):
            # Backward compatibility: convert dict to Theme
            base_theme = _dict_to_theme(theme)
        else:
            base_theme = theme

        # Apply chart-type overrides if available
        if chart_type:
            config = load_config()
            chart_override = get_chart_theme(config, chart_type)
            if chart_override:
                override_theme = _dict_to_theme(chart_override)
                # Merge: chart override takes precedence over base theme
                base_theme = base_theme.compose(override_theme)

        return base_theme


def _dict_to_theme(data: dict[str, object]) -> "Theme":
    """Convert a dict to Theme object (backward compatibility).

    Args:
        data: Dictionary with theme properties.

    Returns:
        Theme instance with values from dict.

    Raises:
        ValueError: If dict contains keys that don't match Theme fields.
    """
    from dataclasses import fields

    from charted.themes.core import Theme

    # Map dict keys to Theme fields - only allow known fields
    theme_data: dict[str, Any] = {}
    theme_fields = {f.name for f in fields(Theme)}

    for key, value in data.items():
        if key in theme_fields:
            theme_data[key] = value
        else:
            raise ValueError(
                f"Unknown theme field '{key}'. Valid fields: {sorted(theme_fields)}"
            )

    return Theme(**theme_data)
