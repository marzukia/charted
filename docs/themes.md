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

### Using Theme.from_preset()

Load themes by name string:

```python
from charted import BarChart
from charted.themes import Theme

chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    theme=Theme.from_preset("dark")  # Alternative: "light", "high-contrast"
)
```
## Theme Structure

Themes are frozen dataclass instances (``charted.themes.Theme``). Construct them directly or load presets:

```python
from charted.themes import Theme

# Direct construction — all fields optional, uses defaults for omitted
theme = Theme(
    colors=["#2e7d32", "#1565c0", "#c62828", "#f57c00", "#6a1b9a"],
    grid_color="#E0E0E0",
    grid_dasharray="2,2",
    grid_visible=True,
    legend_position="topright",
    legend_font_size=11,
    legend_font_family="Arial",
    legend_font_color="#444444",
    title_color="#333333",
    title_font_size=16,
    title_font_family="Arial",
    background_color="#FFFFFF",
    h_padding=0.05,
    v_padding=0.05,
    marker_size=3.0,
)

# Or load a preset and override specific fields
theme = Theme.from_preset("dark").compose(Theme(
    colors=["#ff6b6b", "#4ecdc4", "#45b7d1"],
    title_font_size=20,
))
```

## Creating Custom Themes

### Basic Custom Theme

Create a theme by constructing a ``Theme`` object:

```python
from charted import BarChart
from charted.themes import Theme

corporate_theme = Theme(
    colors=["#003366", "#0066cc", "#6699cc", "#99c2ff", "#cce5ff"],
    title_color="#003366",
    grid_color="#cccccc",
    grid_dasharray="4,4",
)

chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    theme=corporate_theme
)
chart.save("corporate_chart.svg")
```

### Theme Composition

Use ``compose()`` to layer customizations on top of a preset — unspecified values inherit from the base:

```python
from charted import BarChart
from charted.themes import Theme

# Start from preset, override just colors
custom = Theme.from_preset("light").compose(
    Theme(colors=["#ff6b6b", "#4ecdc4", "#45b7d1", "#f7b731", "#5f27cd"])
)

chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    theme=custom
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
from charted.themes import Theme

dark = Theme.from_preset("dark")
# colors: ["#5fab9e", "#f58b51", "#f7dd72", "#db504a", "#2e4756"]
# title_color: "#ffffff"
# grid_color: "#444444"
# background_color: "#1a1a1a"
```

### Light Theme

- **Use case:** Professional reports, print, light backgrounds
- **Colors:** Traditional green/blue/red palette
- **Grid:** Light gray dashed lines
- **Title:** Dark gray (#333333)
- **Best for:** Corporate documents, accessibility

```python
from charted.themes import Theme

light = Theme.from_preset("light")
# colors: ["#5fab9e", "#f58b51", "#f7dd72", "#db504a", "#2e4756"]
# title_color: "#444444"
# grid_color: "#CCCCCC"
# background_color: "#FFFFFF"
```

## Complete Theme Reference

### Theme Dataclass Fields

Every theme is a frozen dataclass with these fields:

```python
from charted.themes import Theme

theme = Theme(
    colors=["#2e7d32", "#1565c0", "#c62828", "#f57c00", "#6a1b9a"],
    grid_color="#E0E0E0",              # Grid line color
    grid_dasharray="2,2",             # Dashed pattern (None = solid)
    grid_visible=True,                # Show/hide grid
    legend_position="topright",       # "topright"|"topleft"|"bottomright"|"bottomleft"
    legend_font_size=11,              # Legend text size
    legend_font_family="Arial",       # Legend font
    legend_font_color="#444444",      # Legend text color
    title_color="#444444",            # Title text color
    title_font_size=16,              # Title font size
    title_font_family="Arial",       # Title font family
    background_color="#FFFFFF",       # Chart background
    h_padding=0.05,                  # Horizontal padding (5%)
    v_padding=0.05,                  # Vertical padding (5%)
    marker_size=3.0,                 # Data point marker size
    arrow_color="#555555",           # Gantt chart dependency arrows
)
```

### Theme Composition Behavior

``compose()`` layers overrides field-by-field — omitted fields inherit from the base:

```python
from charted import BarChart
from charted.themes import Theme

# Minimal override — only changes colors, everything else from "light" preset
custom = Theme.from_preset("light").compose(
    Theme(colors=["#ff6b6b", "#4ecdc4", "#45b7d1", "#f7b731", "#5f27cd"])
)

chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    theme=custom
)

# Override title and grid on a dark base
dark_custom = Theme.from_preset("dark").compose(Theme(
    title_color="#003366",
    grid_color="#cccccc",
    grid_dasharray="4,4",
))

chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    theme=dark_custom
)
```

### Chart-Specific Theme Overrides

Apply different themes per chart type in multi-chart layouts:

```python
from charted import BarChart, LineChart
from charted.themes import Theme

bar_theme = Theme(
    colors=["#5fab9e", "#f58b51", "#f7dd72"],
    title_color="#2e4756",
)

line_theme = Theme(
    colors=["#db504a", "#36a2eb", "#ffce56"],
    marker_size=5.0,
)

bar_chart = BarChart(data=[120, 180, 210], labels=["Q1", "Q2", "Q3"], theme=bar_theme)
line_chart = LineChart(data=[150, 200, 180], labels=["Q1", "Q2", "Q3"], theme=line_theme)
```

### Creating Reusable Theme Libraries

Store custom themes in a module for reuse across projects:

```python
# myproject/themes.py
from charted.themes import Theme

CORPORATE_BLUE = Theme(
    colors=["#003366", "#0066cc", "#6699cc", "#99c2ff", "#cce5ff"],
    title_color="#003366",
    grid_color="#e0e0e0",
    grid_dasharray="2,2",
    legend_font_color="#555555",
)

ACCESSIBILITY_HIGH_CONTRAST = Theme(
    colors=["#000000", "#FFFFFF", "#0066CC", "#CC0000", "#006600"],
    title_color="#000000",
    title_font_size=16,
    grid_color="#000000",
)

DARK_MODE = Theme(
    colors=["#5fab9e", "#f58b51", "#f7dd72", "#db504a", "#2e4756"],
    title_color="#E0E0E0",
    grid_color="#444444",
    legend_font_color="#CCCCCC",
    background_color="#1a1a1a",
)
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

Themes are validated at construction time. Common errors:

```python
from charted.themes import Theme

# Invalid: colors must contain valid hex/HSL values
try:
    theme = Theme(colors=["not-a-color"])
except ValueError as e:
    print(f"Invalid theme: {e}")

# Invalid: grid_color must be valid
try:
    theme = Theme(grid_color="bad")
except ValueError as e:
    print(f"Invalid theme: {e}")
```

You can also use ``validate_theme()`` for WCAG contrast warnings:

```python
from charted import validate_theme
from charted.themes import Theme

theme = Theme(legend_font_color="#eeeeee", background_color="#ffffff")
warnings = validate_theme(theme)
if warnings:
    print("Contrast issues:", warnings)
```

### Debugging Theme Issues

Inspect the effective theme on any chart:

```python
from charted import BarChart
from charted.themes import Theme

chart = BarChart(data=[1, 2, 3], labels=["a", "b", "c"], theme="dark")
print(f"Colors: {chart.theme.colors}")
print(f"Title color: {chart.theme.title_color}")
print(f"Background: {chart.theme.background_color}")
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
from charted.themes import Theme

high_contrast = Theme.from_preset("high-contrast")
# colors: bold primaries for maximum visibility
# title_color: "#000000"
# grid_color: "#000000"
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
from charted.themes import Theme

brand_theme = Theme(
    colors=["#0066cc", "#004c99", "#003366", "#6699cc", "#99c2ff"],
    title_color="#003366",
    title_font_family="Helvetica",
    grid_color="#e0e0e0",
    grid_dasharray="2,2",
)

chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    theme=brand_theme
)
```

### Print-Friendly Charts

```python
from charted.themes import Theme

print_theme = Theme(
    colors=["#000000", "#444444", "#888888", "#aaaaaa", "#cccccc"],
    title_color="#000000",
    grid_color="#000000",
    grid_dasharray=None,
)
```

### Dark Mode Dashboard

```python
from charted.themes import Theme

dashboard_theme = Theme(
    colors=["#5fab9e", "#f58b51", "#f7dd72", "#db504a", "#2e4756"],
    title_color="#ffffff",
    title_font_size=16,
    grid_color="#333333",
    background_color="#1a1a1a",
)
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
- **Minimize overrides** - Compose only what you need
- **Avoid complex stroke_dasharray** - Solid lines render faster

## Troubleshooting

### Colors not applying
- Check that you're passing a list, not a string
- Ensure hex codes have the `#` prefix
- Verify theme is passed to chart constructor, not as method

### Grid lines not visible
- Check `stroke` color isn't same as background
- Ensure `stroke_dasharray` isn't `"0,0"` (invisible)
- Verify theme is loaded correctly with `Theme.from_preset()`

### Title not showing
- Ensure `title` parameter is set on chart
- Check `font_color` contrasts with background
- Verify `font_size` isn't too small

## API Reference

### Theme.from_preset() / Theme.compose()

Load built-in themes and layer customizations:

```python
from charted.themes import Theme

# From preset name
theme = Theme.from_preset("dark")

# Compose custom overrides on top of a preset
theme = Theme.from_preset("light").compose(Theme(colors=["#ff0000", "#00ff00"]))

# Direct construction with defaults
theme = Theme(colors=["#ff0000", "#00ff00"], grid_color="#999999")
```

**Theme.from_preset(name):**
- `name` (str): Preset name — "light", "dark", or "high-contrast"
- **Returns:** Frozen Theme dataclass instance

**Theme.compose(overrides):**
- `overrides` (Theme | None): Theme with fields to override
- **Returns:** New Theme with overrides applied on top of self

### Theme Fields

Theme is a frozen dataclass with these fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `colors` | list[str] | 5 default colors | Color palette for series |
| `grid_color` | str | "#CCCCCC" | Grid line color |
| `grid_dasharray` | str \| None | None | Dash pattern (e.g., "2,2") |
| `grid_visible` | bool | True | Show/hide grid |
| `legend_position` | str | "topright" | Legend placement |
| `legend_font_size` | int | 11 | Legend text size |
| `legend_font_family` | str | "Arial" | Legend font |
| `legend_font_color` | str | "#444444" | Legend text color |
| `title_color` | str | "#444444" | Title text color |
| `title_font_size` | int | 16 | Title font size |
| `title_font_family` | str | "Arial" | Title font |
| `background_color` | str | "#FFFFFF" | Chart background |
| `h_padding` | float | 0.05 | Horizontal padding ratio |
| `v_padding` | float | 0.05 | Vertical padding ratio |
| `marker_size` | float | 3.0 | Marker size in pixels |
| `h_grid` | dict | Horizontal grid configuration |
| `series_style` | dict | Default series styling |
| `legend` | dict | Legend appearance |
| `title` | dict | Title typography |
| `padding` | dict | Chart padding ratios |
