# Configuration

Charted supports project-level configuration via a `.chartedrc` file in your project root.

## File Formats

Supported filenames (in order of search):
- `.chartedrc.toml` — TOML format (recommended)
- `.chartedrc` — TOML format
- `charted.toml` — TOML format

Charted searches upward from your current directory to find a config file.

## Configuration Options

### Basic Settings

```toml
# Font settings
font = "Helvetica"        # Default font family
font_size = 12            # Default font size in points
title_font_size = 16      # Title font size in points

# Chart dimensions
width = 600               # Default chart width in pixels
height = 400              # Default chart height in pixels

# Color palette (SVG/CSS color values)
colors = [
    "#5fab9e",
    "#f58b51",
    "#f7dd72",
    "#db504a",
    "#2e4756"
]
```

### Pie Chart Defaults

```toml
[pie]
explode = 0.1           # Distance to separate slices (0.0-1.0)
start_angle = 0         # Starting angle in degrees
```

## Usage

Config values are automatically applied when creating charts:

```python
from charted import PieChart

# Uses values from .chartedrc if present
chart = PieChart(data=[10, 20, 30], labels=["A", "B", "C"])
```

You can also override config values programmatically:

```python
chart = PieChart(
    data=[10, 20, 30],
    labels=["A", "B", "C"],
    width=800,  # Overrides .chartedrc
    height=600
)
```

## Theme Support

Theme definitions can be referenced in your config:

```toml
theme = "dark"
```

Themes are loaded from the `charted/utils/themes.py` module.
