"""Theme system for charted charts.

This module provides a modern, type-safe theme system that replaces the
legacy TypedDict-based approach with frozen dataclasses for immutability
and better IDE support.

## Quick Start

```python
from charted import BarChart, Theme

# Use built-in presets
chart = BarChart(data=[1, 2, 3], labels=["a", "b", "c"], theme="dark")

# Compose custom themes
custom_theme = Theme.from_preset("light").compose(Theme(colors=["#ff0000"]))
chart = BarChart(data=[1, 2, 3], labels=["a", "b", "c"], theme=custom_theme)

# Register custom themes
from charted import register_theme

register_theme("corporate", Theme(
    colors=["#1a365d", "#2b6cb0", "#3182ce", "#4299e1", "#63b3ed"],
    background_color="#f7fafc"
))
```

## API Reference
"""

from charted.themes.core import ColorPalette, Theme
from charted.themes.registry import (
    get_default_theme,
    get_theme,
    list_themes,
    register_theme,
)
from charted.themes.validation import validate_theme

__all__ = [
    "ColorPalette",
    "Theme",
    "register_theme",
    "list_themes",
    "get_theme",
    "get_default_theme",
    "validate_theme",
]
