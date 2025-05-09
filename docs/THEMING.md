# Theming System

Charted provides a modern, type-safe theming system that replaces the legacy TypedDict-based approach with frozen dataclasses for immutability and better IDE support.

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
    colors=["#1a365d", "#2b6cb0"],
    background_color="#f7fafc"
))
```

## Built-in Presets

Charted includes three built-in theme presets:

### Light Theme (default)
- Colors: Green, blue, red, orange, purple
- Background: White (#FFFFFF)
- Title color: Dark gray (#444444)

### Dark Theme
- Colors: Teal, orange, yellow, red, dark gray
- Background: Dark gray (#1a1a1a)
- Grid color: Dark gray (#444444)
- Title color: White (#ffffff)

### High-Contrast Theme
- Colors: Black, yellow, cyan, magenta, lime
- Background: White (#FFFFFF)
- Grid color: Black (#000000)
- Title color: Black (#000000)

## Custom Themes

Create custom themes by constructing a `Theme` object:

```python
from charted import Theme

# Minimal theme (only override what you need)
theme = Theme(colors=["#ff0000", "#00ff00"])

# Full theme with all options
theme = Theme(
    colors=["#1a365d", "#2b6cb0", "#3182ce"],
    grid_color="#999999",
    grid_dasharray="2,2",
    legend_position="topleft",
    legend_font_size=12,
    title_color="#2d3748",
    title_font_size=18,
    title_font_family="Helvetica",
    background_color="#f7fafc",
    h_padding=0.05,
    v_padding=0.05,
    marker_size=4,
)
```

## Theme Composition

Compose themes by layering overrides:

```python
base = Theme.from_preset("light")
custom = base.compose(Theme(colors=["#ff0000"]))
# custom inherits all light theme properties except colors
```

## Color Cycling

The `ColorManager` class provides automatic color cycling for charts with many series:

```python
from charted import ColorManager

manager = ColorManager(colors=["#ff0000", "#00ff00"])
print(manager.get_color(0))  # "#ff0000"
print(manager.get_color(10))  # "#ff0000" (cycles)
```

## Validation

Validate themes for WCAG contrast compliance:

```python
from charted import Theme, validate_theme

theme = Theme(title_color="#aaaaaa", background_color="#ffffff")
warnings = validate_theme(theme)
if warnings:
    print("Contrast issues:", warnings)
```

## Configuration File

Create a `.chartedrc.toml` file in your project root:

```toml
[theme]
colors = ["#1a365d", "#2b6cb0"]
background_color = "#f7fafc"

[charts.bar]
theme = { colors = ["#e53e3e", "#dd6b20"] }
```

Available properties:
- `colors`: Array of hex color strings
- `grid_color`: Hex color for grid lines
- `grid_dasharray`: Dash pattern (e.g., "2,2")
- `grid_visible`: Boolean
- `legend_position`: "topright", "topleft", "bottomright", "bottomleft"
- `legend_font_size`: Integer (8-72)
- `title_color`: Hex color
- `title_font_size`: Integer (8-72)
- `title_font_family`: String
- `background_color`: Hex color
- `h_padding`: Float (0.0-0.5)
- `v_padding`: Float (0.0-0.5)
- `marker_size`: Float (1.0-20.0)

## Migration from TypedDict

Old code using dict-based themes:

```python
# Old (deprecated)
theme = {
    "colors": ["#ff0000"],
    "grid_color": "#999999"
}
```

New code with dataclass themes:

```python
# New (recommended)
from charted import Theme

theme = Theme(colors=["#ff0000"], grid_color="#999999")
```
