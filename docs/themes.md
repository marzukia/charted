# Themes Guide

Charted provides a powerful theming system that lets you customize every visual aspect of your charts. This guide covers everything from quick preset usage to advanced custom theme creation.

## Quick Start

### Using Preset Themes

Charted ships with 3 built-in themes:

```python
from charted import BarChart

# Dark theme - great for presentations on dark backgrounds
chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    theme="dark"
)
chart.save("dark_chart.svg")

# Light theme - clean, professional look
chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    theme="light"
)
chart.save("light_chart.svg")

# High-contrast theme - accessibility focused
chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    theme="high-contrast"
)
chart.save("accessible_chart.svg")
```

### Using Theme.load()

Load themes by name string:

```python
from charted import BarChart
from charted.utils.themes import Theme

chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    theme=Theme.load("dark")  # Alternative: "light", "high-contrast"
)
```
## Theme Structure

A theme is a dictionary with the following structure:

```python
{
    # Color palette (5 colors, cycles for additional series)
    "colors": ["#2e7d32", "#1565c0", "#c62828", "#f57c00", "#6a1b9a"],
    
    # Vertical grid lines (x-axis grid)
    "v_grid": {
        "stroke": "#E0E0E0",           # Grid line color
        "stroke_dasharray": "2,2",     # Dashed pattern (None = solid)
    },
    
    # Horizontal grid lines (y-axis grid)
    "h_grid": {
        "stroke": "#E0E0E0",
        "stroke_dasharray": "2,2",
    },
    
    # Default styling for all data series
    "series_style": {
        "stroke_width": 2.0,           # Line thickness
        "stroke_opacity": 1.0,         # 0.0-1.0
        "fill": None,                  # Bar/column fill color
        "marker_shape": "circle",      # "circle"|"square"|"diamond"|"none"
        "marker_size": 3.0,            # Marker size in pixels
    },
    
    # Legend configuration
    "legend": {
        "font_size": 11,
        "legend_padding": 0.25,
        "position": "topright",        # "topright"|"topleft"|"bottomright"|etc.
    },
    
    # Title configuration
    "title": {
        "font_size": 14,
        "font_family": "Arial",
        "font_weight": "bold",
        "font_color": "#333333",
    },
    
    # Chart padding
    "padding": {
        "h_padding": 0.05,             # Horizontal padding (0.0-1.0)
        "v_padding": 0.05,             # Vertical padding (0.0-1.0)
    },
}
```

## Creating Custom Themes

### Basic Custom Theme

Create a theme by providing a dictionary with any overrides:

```python
from charted import BarChart

corporate_theme = {
    "colors": ["#003366", "#0066cc", "#6699cc", "#99c2ff", "#cce5ff"],
    "title": {
        "font_color": "#003366",
        "font_weight": "bold",
    },
    "v_grid": {
        "stroke": "#cccccc",
        "stroke_dasharray": "4,4",
    },
}

chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    theme=corporate_theme
)
chart.save("corporate_chart.svg")
```

### Theme Merging

Themes use deep merging - unspecified values inherit from defaults:

```python
from charted import BarChart

# This only changes colors, everything else uses defaults
custom_colors = {
    "colors": ["#ff6b6b", "#4ecdc4", "#45b7d1", "#f7b731", "#5f27cd"],
}

chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    theme=custom_colors
)
```

## Advanced Customization

### Per-Series Styling

Override styles for individual data series:

```python
from charted import BarChart

# Highlight the second series with custom styling
series_styles = [
    None,  # Use theme default for first series
    {
        "fill": "#ff0000",           # Red bars
        "stroke_width": 3.0,         # Thicker border
    },
    {
        "fill": "#00ff00",           # Green bars
        "stroke_width": 3.0,
    },
]

chart = BarChart(
    data=[[120, 180, 210], [130, 190, 220], [140, 200, 230]],
    labels=["Q1", "Q2", "Q3"],
    series_names=["2022", "2023", "2024"],
    series_styles=series_styles
)
chart.save("highlighted_series.svg")
```

### Pie Chart Slice Styling

Apply different colors/styling to individual pie slices:

```python
from charted import PieChart

# Style each slice independently
slice_styles = [
    {"fill": "#ff6384", "opacity": 1.0},
    {"fill": "#36a2eb", "opacity": 0.9},
    {"fill": "#ffce56", "opacity": 0.8},
    {"fill": "#4bc0c0", "opacity": 0.7},
]

chart = PieChart(
    data=[30, 45, 25, 50],
    labels=["Category A", "Category B", "Category C", "Category D"],
    series_styles=slice_styles
)
chart.save("styled_pie.svg")
```

### Line/Scatter Marker Customization

Control marker appearance for line and scatter charts:

```python
from charted import LineChart

# Square markers with custom stroke
series_styles = [
    {
        "marker_shape": "square",
        "marker_size": 5.0,
        "stroke_opacity": 0.8,       # Semi-transparent line
        "stroke_width": 2.5,
    },
]

chart = LineChart(
    data=[120, 180, 210, 150],
    labels=["Q1", "Q2", "Q3", "Q4"],
    series_styles=series_styles
)
chart.save("square_markers.svg")
```

## Theme Presets Explained

### Dark Theme

- **Use case:** Presentations, dark mode interfaces, dashboards
- **Colors:** Muted teal/orange/yellow palette
- **Grid:** Subtle dark gray lines
- **Title:** Light gray (#E0E0E0)
- **Best for:** Reducing eye strain in low-light environments

```python
dark_theme = {
    "colors": ["#5fab9e", "#f58b51", "#f7dd72", "#db504a", "#2e4756"],
    "title": {"font_color": "#E0E0E0"},
    "v_grid": {"stroke": "#444444"},
    "h_grid": {"stroke": "#444444"},
}
```

### Light Theme

- **Use case:** Professional reports, print, light backgrounds
- **Colors:** Traditional green/blue/red palette
- **Grid:** Light gray dashed lines
- **Title:** Dark gray (#333333)
- **Best for:** Corporate documents, accessibility

```python
light_theme = {

## Complete Theme Reference

### Full Theme Dictionary Structure

Every theme is a dictionary with these keys:

```python
complete_theme = {
    # Primary color palette (5 colors, cycles for additional series)
    "colors": ["#2e7d32", "#1565c0", "#c62828", "#f57c00", "#6a1b9a"],
    
    # Vertical grid (x-axis grid lines)
    "v_grid": {
        "stroke": "#E0E0E0",           # Grid line color
        "stroke_dasharray": "2,2",     # Dashed pattern (None = solid)
        "stroke_width": 0.5,           # Line thickness
    },
    
    # Horizontal grid (y-axis grid lines)
    "h_grid": {
        "stroke": "#E0E0E0",
        "stroke_dasharray": "2,2",
        "stroke_width": 0.5,
    },
    
    # Default series styling (applied to all data series)
    "series_style": {
        "stroke_width": 2.0,           # Border/line thickness
        "stroke_opacity": 1.0,         # 0.0-1.0 transparency
        "fill": None,                  # Bar/column fill (None = use stroke)
        "marker_shape": "circle",      # "circle"|"square"|"diamond"|"none"
        "marker_size": 3.0,            # Marker size in pixels
    },
    
    # Legend configuration
    "legend": {
        "font_size": 11,               # Legend text size
        "font_family": "Arial",        # Legend font
        "font_color": "#666666",       # Legend text color
        "legend_padding": 0.25,        # Padding around legend
        "position": "topright",        # "topright"|"topleft"|"bottomright"|
                                       # "bottomleft"|"center"|"top"|"bottom"
    },
    
    # Title configuration
    "title": {
        "font_size": 14,               # Title font size
        "font_family": "Arial",        # Title font family
        "font_weight": "bold",         # "normal"|"bold"|"bolder"|"lighter"
        "font_color": "#333333",       # Title text color
    },
    
    # Axis labels configuration
    "axis_labels": {
        "font_size": 10,               # Axis label text size
        "font_family": "Arial",        # Axis label font
        "font_color": "#666666",       # Axis label color
    },
    
    # Chart padding (fraction of chart dimensions)
    "padding": {
        "h_padding": 0.05,             # Horizontal padding (5%)
        "v_padding": 0.05,             # Vertical padding (5%)
    },
    
    # Doughnut chart specific (for PieChart)
    "doughnut": {
        "inner_radius": 0.6,           # Inner radius as fraction (0-1)
        "stroke": "#FFFFFF",           # Center hole border color
        "stroke_width": 2.0,           # Center hole border width
    },
}
```

### Theme Merging Behavior

Themes use **deep merging** - partial themes inherit unspecified values from defaults:

```python
from charted import BarChart

# Minimal theme - only changes colors
color_only_theme = {
    "colors": ["#ff6b6b", "#4ecdc4", "#45b7d1", "#f7b731", "#5f27cd"],
}

# Everything else uses library defaults
chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    theme=color_only_theme
)

# Partial theme - changes title and grid
partial_theme = {
    "title": {
        "font_color": "#003366",
        "font_weight": "bold",
    },
    "v_grid": {
        "stroke": "#cccccc",
        "stroke_dasharray": "4,4",
    },
}

# Colors, series_style, legend, etc. use defaults
chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    theme=partial_theme
)
```

### Chart-Specific Theme Overrides

Apply different themes per chart type in multi-chart layouts:

```python
from charted import BarChart, LineChart

# Bar chart with custom theme
bar_theme = {
    "colors": ["#5fab9e", "#f58b51", "#f7dd72"],
    "title": {"font_color": "#2e4756"},
}

# Line chart with different theme
line_theme = {
    "colors": ["#db504a", "#36a2eb", "#ffce56"],
    "series_style": {
        "stroke_width": 3.0,
        "marker_shape": "square",
    },
}

bar_chart = BarChart(data=[120, 180, 210], labels=["Q1", "Q2", "Q3"], theme=bar_theme)
line_chart = LineChart(data=[150, 200, 180], labels=["Q1", "Q2", "Q3"], theme=line_theme)
```

### Creating Reusable Theme Libraries

Store custom themes in a module for reuse across projects:

```python
# myproject/themes.py

CORPORATE_BLUE = {
    "colors": ["#003366", "#0066cc", "#6699cc", "#99c2ff", "#cce5ff"],
    "title": {
        "font_color": "#003366",
        "font_weight": "bold",
    },
    "v_grid": {"stroke": "#e0e0e0", "stroke_dasharray": "2,2"},
    "h_grid": {"stroke": "#e0e0e0", "stroke_dasharray": "2,2"},
    "legend": {"font_color": "#555555"},
    "axis_labels": {"font_color": "#666666"},
}

ACCESSIBILITY_HIGH_CONTRAST = {
    "colors": ["#000000", "#FFFFFF", "#0066CC", "#CC0000", "#006600"],
    "title": {"font_color": "#000000", "font_weight": "bold", "font_size": 16},
    "v_grid": {"stroke": "#000000", "stroke_width": 1.0},
    "h_grid": {"stroke": "#000000", "stroke_width": 1.0},
    "series_style": {"stroke_width": 3.0},
}

DARK_MODE = {
    "colors": ["#5fab9e", "#f58b51", "#f7dd72", "#db504a", "#2e4756"],
    "title": {"font_color": "#E0E0E0"},
    "v_grid": {"stroke": "#444444"},
    "h_grid": {"stroke": "#444444"},
    "legend": {"font_color": "#CCCCCC"},
    "axis_labels": {"font_color": "#AAAAAA"},
}
```

Usage:

```python
from charted import BarChart
from myproject.themes import CORPORATE_BLUE, ACCESSIBILITY_HIGH_CONTRAST

chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    theme=CORPORATE_BLUE
)
```

### Theme Validation

Themes are validated at chart creation time. Common errors:

```python
from charted import BarChart

# Invalid: colors must be list of at least 1 color
try:
    chart = BarChart(data=[1,2,3], labels=["a","b","c"], theme={"colors": []})
except ValueError as e:
    print(f"Invalid theme: {e}")

# Invalid: position must be valid string
try:
    chart = BarChart(
        data=[1,2,3], labels=["a","b","c"],
        theme={"legend": {"position": "invalid"}}
    )
except ValueError as e:
    print(f"Invalid theme: {e}")

# Invalid: padding must be 0-1
try:
    chart = BarChart(
        data=[1,2,3], labels=["a","b","c"],
        theme={"padding": {"h_padding": 1.5}}
    )
except ValueError as e:
    print(f"Invalid theme: {e}")
```

### Debugging Theme Issues

Print effective theme to debug:

```python
from charted import BarChart
from charted.config import load_config, merge_theme

# Load config and theme
config = load_config()
effective_theme = merge_theme(config.get("theme", "light"), config)

print(f"Effective theme colors: {effective_theme['colors']}")
print(f"Title font: {effective_theme['title']}")
```

### Theme Best Practices

**Color Palettes:**
- Use 5 colors minimum (cycles for additional series)
- Ensure sufficient contrast for accessibility
- Consider color blindness (avoid red/green combinations)
- Test on both light and dark backgrounds

**Typography:**
- Title font size: 14-18pt (depends on chart height)
- Axis labels: 10-12pt
- Legend: 10-11pt
- Use bold for titles, normal for labels

**Grid Lines:**
- Light themes: light gray (#E0E0E0) dashed
- Dark themes: dark gray (#444444) solid
- Stroke width: 0.5-1.0px
- Dash pattern: "2,2" (subtle) or "4,4" (more pronounced)

**Spacing:**
- Padding: 0.05 (5%) is standard
- Legend padding: 0.25-0.5
- Bar/column gap: 0.3-0.7 (lower = tighter)
    "colors": ["#2e7d32", "#1565c0", "#c62828", "#f57c00", "#6a1b9a"],
    "title": {"font_color": "#333333"},
    "v_grid": {"stroke": "#E0E0E0", "stroke_dasharray": "2,2"},
    "h_grid": {"stroke": "#E0E0E0", "stroke_dasharray": "2,2"},
}
```

### High-Contrast Theme

- **Use case:** Accessibility, presentations on projectors
- **Colors:** Pure primary colors (black, yellow, cyan, magenta, green)
- **Grid:** Solid black lines
- **Title:** Bold black (#000000)
- **Best for:** WCAG compliance, large venue displays

```python
high_contrast_theme = {
    "colors": ["#000000", "#FFFF00", "#00FFFF", "#FF00FF", "#00FF00"],
    "title": {"font_size": 18, "font_weight": "bold", "font_color": "#000000"},
    "v_grid": {"stroke": "#000000"},
    "h_grid": {"stroke": "#000000"},
}
```

## Color Palettes

### Choosing Colors

Charted uses 5-color palettes that cycle for additional series. Good palettes should:

1. **Be distinguishable** - Avoid colors that look similar (light blue vs light green)
2. **Have consistent saturation** - Don't mix pastel with neon
3. **Consider color blindness** - Avoid red/green combinations
4. **Match your brand** - Use corporate colors when appropriate

### Recommended Palettes

**Professional:**
```python
professional = ["#2e7d32", "#1565c0", "#c62828", "#f57c00", "#6a1b9a"]
```

**Vibrant:**
```python
vibrant = ["#ff6384", "#36a2eb", "#ffce56", "#4bc0c0", "#9966ff"]
```

**Muted:**
```python
muted = ["#7f8c8d", "#95a5a6", "#bdc3c7", "#34495e", "#2c3e50"]
```

**Pastel:**
```python
pastel = ["#a8e6cf", "#dcedc1", "#ffd3b6", "#ffaaa5", "#ff8b94"]
```

## Common Patterns

### Brand-Aligned Charts

```python
from charted import BarChart

# Match your company branding
brand_theme = {
    "colors": ["#0066cc", "#004c99", "#003366", "#6699cc", "#99c2ff"],
    "title": {
        "font_color": "#003366",
        "font_family": "Helvetica",
        "font_weight": "bold",
    },
    "v_grid": {"stroke": "#e0e0e0", "stroke_dasharray": "2,2"},
    "h_grid": {"stroke": "#e0e0e0", "stroke_dasharray": "2,2"},
}

chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    theme=brand_theme
)
```

### Print-Friendly Charts

```python
print_theme = {
    "colors": ["#000000", "#444444", "#888888", "#aaaaaa", "#cccccc"],
    "title": {"font_color": "#000000", "font_weight": "bold"},
    "v_grid": {"stroke": "#000000", "stroke_dasharray": None},
    "h_grid": {"stroke": "#000000", "stroke_dasharray": None},
}
```

### Dark Mode Dashboard

```python
dashboard_theme = {
    "colors": ["#5fab9e", "#f58b51", "#f7dd72", "#db504a", "#2e4756"],
    "title": {"font_color": "#ffffff", "font_size": 16},
    "v_grid": {"stroke": "#333333"},
    "h_grid": {"stroke": "#333333"},
}
```

## Theme Validation

Always test your theme with all chart types:

```python
from charted import BarChart, LineChart, PieChart

test_data = [10, 20, 30, 40, 50]
test_labels = ["A", "B", "C", "D", "E"]

# Test across chart types
BarChart(data=test_data, labels=test_labels, theme=my_theme).save("test_bar.svg")
LineChart(data=test_data, labels=test_labels, theme=my_theme).save("test_line.svg")
PieChart(data=test_data, labels=test_labels, theme=my_theme).save("test_pie.svg")
```

## Performance Tips

- **Cache theme objects** - Don't recreate themes in loops
- **Use presets when possible** - They're pre-validated
- **Minimize overrides** - Fewer nested dicts = faster merging
- **Avoid complex stroke_dasharray** - Solid lines render faster

## Troubleshooting

### Colors not applying
- Check that you're passing a list, not a string
- Ensure hex codes have the `#` prefix
- Verify theme is passed to chart constructor, not as method

### Grid lines not visible
- Check `stroke` color isn't same as background
- Ensure `stroke_dasharray` isn't `"0,0"` (invisible)
- Verify theme is loaded correctly with `Theme.load()`

### Title not showing
- Ensure `title` parameter is set on chart
- Check `font_color` contrasts with background
- Verify `font_size` isn't too small

## API Reference

### Theme.load()

Load a theme from various input types:

```python
from charted.utils.themes import Theme

# From preset name
theme = Theme.load("dark")

# From dictionary
theme = Theme.load({"colors": ["#ff0000", "#00ff00"]})

# From None (returns default)
theme = Theme.load(None)
```

**Parameters:**
- `theme` (str | dict | None): Preset name, theme dict, or None
- **Returns:** Theme dictionary with defaults merged in

### Theme Structure

All theme keys are optional - missing keys use defaults:

| Key | Type | Description |
|-----|------|-------------|
| `colors` | list[str] | Color palette (5 hex codes) |
| `v_grid` | dict | Vertical grid configuration |
| `h_grid` | dict | Horizontal grid configuration |
| `series_style` | dict | Default series styling |
| `legend` | dict | Legend appearance |
| `title` | dict | Title typography |
| `padding` | dict | Chart padding ratios |
