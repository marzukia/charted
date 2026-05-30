# Configuration Guide

Configure Charted globally or per-chart.

## Configuration Methods

Charted supports configuration via:

1. **TOML config files** (`.chartedrc.toml`)
2. **Environment variables**
3. **Per-chart overrides**

## TOML Configuration

Create a `.chartedrc.toml` file in your project root:

```toml
# .chartedrc.toml

[defaults]
font = "Roboto"
font_size = 12
title_font_size = 16
width = 600
height = 400

[bar]
bar_gap = 0.2
group_gap = 0.3

[theme]
colors = ["#FF6B6B", "#4ECDC4", "#45B7D1"]
background_color = "#ffffff"
```

## Environment Variables

```bash
export CHARTED_FONT="Roboto"
export CHARTED_FONT_SIZE="14"
export CHARTED_WIDTH="800"
export CHARTED_HEIGHT="600"
```

## Per-Chart Overrides

Override defaults for individual charts:

```python
from charted import BarChart

# Uses global defaults from .chartedrc.toml
chart1 = BarChart(data=[120, 180, 210], labels=["Q1", "Q2", "Q3"])

# Override for this chart only
chart2 = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    font_family="Monoton",  # Override font
    width=1000,             # Override width
    height=800              # Override height
)
```

## Available Options

### General Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `font` | str | "Arial" | Font family |
| `font_size` | int | 12 | Body text size (pt) |
| `title_font_size` | int | 16 | Title size (pt) |
| `width` | int | 600 | Chart width (px) |
| `height` | int | 400 | Chart height (px) |

### Chart-Specific Options

See individual chart documentation for chart-specific options.
