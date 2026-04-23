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
                        # Bundled fonts: Helvetica, Arial, Roboto, JetBrains Mono, Fira Code, Inter, Lato
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

### Bar Chart Defaults

```toml
[bar]
bar_gap = 0.50          # Gap between bars as fraction of bar width (0.0-1.0)
```

### Column Chart Defaults

```toml
[column]
column_gap = 0.50       # Gap between columns as fraction of column width (0.0-1.0)
```

### Pie Chart Defaults

```toml
[pie]
explode = 0.1           # Distance to separate slices (0.0-1.0)
start_angle = 0         # Starting angle in degrees (0-360)
label_font_size = 14    # Font size for slice labels in points
```

### Chart-Specific Configuration

Chart-specific parameters (like `inner_radius` for pie charts) are set as constructor arguments, not in the config file.

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

## CLI Usage

Config files are automatically used by the CLI:

```sh
# Uses .chartedrc.toml from project root
charted create bar output.svg --data data.csv

# Override config with explicit config path
charted create column chart.svg -d sales.csv -c /path/to/config.toml
```

## Advanced Configuration

### Environment Variables

Override config values via environment variables:

```bash
export CHARTED_WIDTH=800
export CHARTED_HEIGHT=500
export CHARTED_THEME=dark
export CHARTED_FONT=Roboto
```

### Programmatic Configuration

Load and modify config in Python:

```python
from charted.config import load_config, save_config

config = load_config()
config["width"] = 800
config["theme"] = "dark"
save_config(config, path="/path/to/custom/.chartedrc.toml")
```

### Chart-Specific Defaults

Configure defaults per chart type:

```toml
[bar]
bar_gap = 0.3

[column]
column_gap = 0.6

[pie]
explode = 0.15
start_angle = 90
label_font_size = 12
```

### Complete Example

Full `.chartedrc.toml` example:

```toml
font = "Roboto"
font_size = 12
title_font_size = 16

# Theme configuration
theme = "dark"  # or "light", "high-contrast", or custom dict

# Grid configuration
v_grid = { stroke = "#E0E0E0", stroke_dasharray = "5,5" }
h_grid = { stroke = "#E0E0E0", stroke_dasharray = "5,5" }

# Legend configuration  
legend = { position = "topright", font_size = 11, font_color = "#666666", legend_padding = 0.25 }

# Title configuration
title = { font_size = "16pt", font_family = "Helvetica", font_weight = "bold", font_color = "#333333" }

# Marker configuration
marker = { marker_size = 3.0 }

# Padding configuration
padding = { h_padding = 0.05, v_padding = 0.05 }
```

Chart-specific parameters (explode, inner_radius, start_angle, etc.) are constructor arguments, not config options.

## Troubleshooting

### Config Not Loading

```python
from charted.config import find_config
config_path = find_config()
print(f"Config found at: {config_path}")
```

### Overriding Config Programmatically

```python
from charted import BarChart

chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    width=1000,
    height=700,
    theme="dark"
)
```
