# charted-axes.md - Deep Dive on Axes Module

## Overview

The `axes` module (`charted/charts/axes.py`) is the core component for rendering chart axes in the charted library. It handles coordinate transformation, grid line generation, tick mark placement, and axis label rendering.

---

## Architecture

### Class Hierarchy

```
G (SVG Group element)
└── Axis (base class)
    ├── XAxis
    └── YAxis
```

### Key Classes

#### 1. `Axis` (Base Class)

**Purpose:** Abstract base class providing shared functionality for both X and Y axes.

**Key Responsibilities:**
- Calculate axis dimensions (min/max values, count)
- Generate tick mark values at appropriate intervals
- Handle stacked data visualization
- Provide coordinate transformation utilities

**Key Methods:**

| Method | Description |
|--------|-------------|
| `calculate_axis_dimensions()` | Computes min/max values and data count from input data |
| `calculate_axis_values()` | Generates tick mark values using common denominators |
| `_reproject()` | Transforms data values to pixel coordinates |
| `_reverse()` | Inverse transformation: pixels back to data values |

**Key Properties:**

| Property | Description |
|----------|-------------|
| `values` | Computed tick mark values (setter triggers calculation) |
| `labels` | Formatted text labels for tick marks |
| `reprojected_values` | Pixel coordinates of tick marks |
| `zero` | Pixel position of zero on the axis |
| `grid_lines` | SVG Path for grid lines |
| `axis_labels` | SVG Group containing axis labels |

---

#### 2. `XAxis`

**Purpose:** Horizontal axis handling x-coordinates and categories.

**Unique Features:**
- Uses `parent.plot_width` for coordinate transformation
- Grid lines extend vertically from top to bottom of plot area
- Labels positioned at bottom of chart with optional rotation
- Supports category labels (strings) or numeric values

**Key Properties:**

```python
@property
def grid_lines(self) -> Path:
    # Generates vertical grid lines
    d = [f"M{x} {0} v{self.parent.plot_height}" for x in self.coordinates]
```

---

#### 3. `YAxis`

**Purpose:** Vertical axis handling y-coordinates and values.

**Unique Features:**
- Uses `parent.plot_height` for coordinate transformation
- Grid lines extend horizontally across plot area
- Labels positioned at left edge, aligned right
- Coordinate system inverted (SVG y-axis goes down, charts typically show y going up)

**Key Properties:**

```python
@property
def grid_lines(self) -> Path:
    # Generates horizontal grid lines
    d = [f"M{0} {y} h{self.parent.plot_width}" for y in self.coordinates]
```

---

## Data Flow

### 1. Initialization

```python
# Create XAxis with data
xaxis = XAxis(
    parent=chart,
    data=[[1, 2, 3, 4, 5], [2, 4, 6, 8, 10]],
    labels=["A", "B", "C", "D", "E"]
)
```

### 2. Value Calculation (via `values` setter)

1. **Input:** Raw data array, optional labels, zero_index flag
2. **Processing:** `calculate_axis_values()` called
3. **Output:** `AxisDimension(min, max, count)` + tick values

### 3. Label Generation (via `labels` setter)

1. **Input:** Tick values from step 2
2. **Processing:** Convert to strings, measure text dimensions
3. **Output:** List of `MeasuredText` objects

### 4. Coordinate Reprojection

```python
# Transform data value to pixel coordinate
pixel_x = xaxis.reproject(data_value)
```

---

## Dependencies

### Imports

```python
from charted.html.element import G, Path, Text  # SVG elements
from charted.utils.defaults import DEFAULT_FONT, DEFAULT_FONT_SIZE
from charted.utils.helpers import (
    calculate_text_dimensions,  # Measure text for layout
    common_denominators,        # Find nice tick intervals
    round_to_clean_number,      # Round axis bounds nicely
)
from charted.utils.themes import GridConfig  # Grid styling
from charted.utils.transform import rotate, translate  # SVG transforms
from charted.utils.types import AxisDimension, MeasuredText, Vector, Vector2D
```

### Called From

```python
# charted/charts/chart.py:1
from charted.charts.axes import Axis, XAxis, YAxis
```

The `Chart` class instantiates `XAxis` and `YAxis` objects during initialization.

---

## Key Algorithms

### Common Denominators for Tick Marks

The `calculate_axis_values()` method uses `common_denominators()` to find intervals that produce "nice" tick marks:

```python
# For range [0, 100], denominators might be: [1, 2, 5, 10, 25, 50]
# Selects denominator that gives ~5-10 ticks
denominators = common_denominators(min_value, max_value)
for denominator in reversed(denominators):
    count = int(value_range / denominator)
    values = [min_value + (i * denominator) for i in range(count + 1)]
    if len(values) > 5:
        break  # Found good interval
```

### Stacked Data Handling

For stacked bar/column charts, `calculate_axis_dimensions()` aggregates values:

```python
if stacked:
    # Sum positive and negative values separately per column
    for series in data:
        for n in range(count):
            if series[n] < 0:
                min_values[n] -= abs(series[n])
            else:
                max_values[n] += series[n]
```

---

## Usage Example

```python
from charted.charts.column import ColumnChart

# Chart automatically creates XAxis and YAxis
chart = ColumnChart(
    data=[[10, 20, 30], [15, 25, 35]],
    labels=["Q1", "Q2", "Q3"]
)

# Access axis properties
xaxis = chart.xaxis
print(xaxis.values)        # [0, 1, 2, 3] - tick positions
print(xaxis.labels)        # [" ", "Q1", "Q2", "Q3", " "] - labels
print(xaxis.reprojected_values)  # Pixel coordinates
```

---

## Related Symbols

| Symbol | File | Relationship |
|--------|------|--------------|
| `Chart` | `charted/charts/chart.py` | Uses XAxis and YAxis |
| `ColumnChart` | `charted/charts/column.py` | Extends Chart, uses axes |
| `LineChart` | `charted/charts/line.py` | Extends Chart, uses axes |
| `AxisDimension` | `charted/utils/types.py` | Data class for axis bounds |
| `GridConfig` | `charted/utils/themes.py` | Styling for grid lines |
| `G`, `Path`, `Text` | `charted/html/element.py` | SVG element classes |

---

## Summary

The `axes` module provides a flexible, mathematically robust foundation for chart rendering:

- **Automatic scaling**: Calculates appropriate axis bounds and tick intervals
- **Stacked data support**: Handles stacked bar/column charts
- **Coordinate transformation**: Bridges data space and pixel space
- **SVG generation**: Outputs proper SVG elements for rendering
- **Extensible design**: Base `Axis` class with specialized `XAxis` and `YAxis` subclasses
