# charted - Chart Symbol Deep Dive

## Overview

**Location:** `charted/charts/chart.py` (526 lines)

**What it does:** The `Chart` class is the core rendering engine for this Python charting library. It inherits from `Svg` and provides the foundation for generating SVG-based charts (line, column, scatter) with configurable themes, axes, labels, and styling.

---

## Key Architecture

### Inheritance Hierarchy
```
Chart → Svg → (HTML/SVG element base)
```

### Constructor Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `width` | float | 500 | Chart width in pixels |
| `height` | float | 500 | Chart height in pixels |
| `zero_index` | bool | True | Whether data is zero-indexed |
| `x_data` | Vector \| Vector2D | None | X-axis data values |
| `y_data` | Vector \| Vector2D | None | Y-axis data values |
| `x_labels` | Labels | None | X-axis label strings |
| `y_labels` | Labels | None | Y-axis label strings |
| `series_names` | list[str] | None | Names for multi-series charts |
| `title` | str | None | Chart title |
| `theme` | Theme | None | Visual theme configuration |

---

## Dependencies

### Internal Imports
| Module | Purpose |
|--------|--------|
| `charted.charts.axes` | `Axis`, `XAxis`, `YAxis` classes for axis rendering |
| `charted.html.element` | `G`, `Path`, `Rect`, `Svg`, `Text` - SVG element primitives |
| `charted.utils.colors` | `generate_complementary_colors` for color generation |
| `charted.utils.defaults` | `DEFAULT_COLORS` fallback color palette |
| `charted.utils.exceptions` | `InvalidValue` exception type |
| `charted.utils.helpers` | Coordinate transformation utilities |
| `charted.utils.themes` | `Theme` class for styling configuration |
| `charted.utils.transform` | `translate` function for coordinate transforms |
| `charted.utils.types` | Type definitions: `Labels`, `MeasuredText`, `Vector`, `Vector2D` |

---

## Core Properties & Methods

### Data Properties
- `x_data` / `y_data` - Validated data vectors (with setters that validate)
- `x_labels` / `y_labels` - Text labels converted to `MeasuredText` objects
- `colors` - Auto-generated color palette based on data count

### Dimension Properties
- `width` / `height` - Chart dimensions (validated ≥ 0)
- `plot_width` / `plot_height` - Usable area after padding
- `h_padding` / `v_padding` - Padding ratios (0-1 range)

### Rendering Components (Properties)
- `container` - White background `Path`
- `title` - Centered title `Text` element
- `x_axis` / `y_axis` - Axis rendering objects
- `zero_line` - Zero reference line
- `representation` - The actual chart data visualization
- `legend` - Series legend

### Validation Methods
- `_validate_data()` - Ensures data is non-empty and all series equal length
- `validate_x_data()` / `validate_y_data()` - Public validation wrappers
- `_validate_attribute_value()` - Ensures numeric values ≥ 0

---

## Rendering Pipeline

The `__init__` method orchestrates the render pipeline:

1. **Initialize SVG** - Calls parent `Svg.__init__()` with dimensions
2. **Validate data** - Ensures at least one axis has data
3. **Apply theme** - Loads theme configuration
4. **Store data** - Sets x/y data and labels (with validation)
5. **Create axes** - Instantiates `XAxis` and `YAxis` objects
6. **Generate colors** - Creates color palette for series
7. **Add children** - Builds SVG element tree:
   ```
   container → title → y_axis → x_axis → zero_line → representation → legend
   ```

---

## Where It's Called From

The `Chart` class is the parent class for specific chart types:
- `Line` - Line charts
- `Column` - Column/bar charts  
- `Scatter` - Scatter plots

These subclasses override the `representation` property to render their specific visualization.

---

## Key Design Patterns

1. **Builder Pattern** - Configuration through constructor, rendering deferred to property access
2. **Template Method** - `representation` property provides hook for subclasses
3. **Validation on Set** - Property setters validate before assignment
4. **Theme Injection** - Visual styling decoupled via `Theme` objects
