# Theming Guide

Customize the appearance of your charts with Charted's powerful theming system.

## Built-in Themes

Charted includes 3 built-in themes:

- **light** — Clean white background with dark text (default)
- **dark** — Dark background with light text
- **high-contrast** — Maximum contrast for accessibility

```python
from charted import BarChart

# Use a built-in theme
chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    theme="dark"
)
```

## Custom Themes

Override any theme property with a dictionary:

```python
chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    theme={
        "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1"],
        "background_color": "#1a1a2e",
        "grid_color": "#ffffff20",
        "font_family": "Roboto",
        "font_size": 14
    }
)
```

## Theme Structure

Complete theme dictionary structure:

```python
theme = {
    # Colors
    "colors": ["#1f77b4", "#ff7f0e", "#2ca02c"],  # Series colors
    "background_color": "#ffffff",
    "grid_color": "#e0e0e0",
    "text_color": "#333333",
    
    # Typography
    "font_family": "Arial",
    "font_size": 12,
    "title_font_size": 16,
    
    # Spacing
    "padding": 60,
    "title_padding": 10,
    
    # Grid
    "grid_lines": True,
    "grid_width": 1,
    
    # Legend
    "legend_position": "top",
    "legend_font_size": 12,
}
```

## Per-Chart Theme Overrides

You can also pass theme overrides directly to chart constructors:

```python
from charted import ColumnChart

chart = ColumnChart(
    data=[[120, 180], [150, 200]],
    labels=["Q1", "Q2"],
    theme={
        "colors": ["#FF6B6B", "#4ECDC4"],  # Override default palette
        "title_font_size": 20  # Larger title
    }
)
```

See the full [API Reference](https://github.com/marzukia/charted/tree/main/charted) for complete theme documentation.
