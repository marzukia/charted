# Axis Tick Interval Examples

This directory contains example charts demonstrating the fixed axis tick interval functionality.

## Key Features Fixed

### 1. Zero Line Always Labeled When Spanning Negative to Positive
When an axis spans from negative to positive values, **zero is always included in both grid lines AND labels**, regardless of the tick interval setting.

**Before the fix:** Zero might be skipped if the tick interval didn't align perfectly with zero's position.

**After the fix:** Zero is explicitly added to label_values when `min_value < 0 < max_value`.

### 2. Zero Index for All-Negative Values
When `zero_index=True` and all values are negative, the axis now correctly extends to zero as the maximum value.

**Before the fix:** Only handled all-positive values (set min to 0).

**After the fix:** Handles both cases:
- All positive → set min to 0
- All negative → set max to 0

### 3. Tick Interval Control
The `axis_tick_interval` parameter now works correctly for both X and Y axes:

- **Integer (e.g., `2`)**: Show every Nth tick label
- **Percentage string (e.g., `"25%"`)**: Show ~25% of tick labels
- **Float (e.g., `0.2`)**: Show ~20% of tick labels

## Example Files

### 1. `y_axis_negative_to_positive.svg`
**Configuration:**
```python
ColumnChart(
    data=[negative_data, positive_data],
    labels=categories,
    axis_tick_interval=2,
)
```

**Key Feature:** Y-axis spans from -50 to 60. With `interval=2`, zero is still labeled even though the step might skip it.

### 2. `x_axis_negative_to_positive.svg`
**Configuration:**
```python
LineChart(
    data=y_values,
    x_data=x_values,  # [-4, -3, -2, -1, 0, 1, 2, 3, 4]
    axis_tick_interval=2,
)
```

**Key Feature:** X-axis spans from -4 to 4. Zero is explicitly labeled.

### 3. `both_axes_negative.svg`
**Configuration:**
```python
LineChart(
    data=y_data,
    x_data=x_data,
    axis_tick_interval=2,
)
```

**Key Feature:** Both axes span negative to positive. Both zero lines are labeled.

### 4. `all_quadrants.svg`
**Configuration:**
```python
LineChart(
    data=y_data,  # [-20, -10, 0, 10, 20]
    x_data=x_data,  # [-4, -2, 0, 2, 4]
    axis_tick_interval=2,
)
```

**Key Feature:** Chart spans all four quadrants. Both axes have zero labeled.

### 5. `all_negative_zero_index.svg`
**Configuration:**
```python
ColumnChart(
    data=negative_only,  # [-10, -20, -30, -40, -50]
    labels=categories,
)
```

**Key Feature:** All negative values with `zero_index=True`. Y-axis extends to 0 as max.

### 6. `percentage_interval.svg`
**Configuration:**
```python
LineChart(
    data=data,
    labels=categories,
    axis_tick_interval="25%",
)
```

**Key Feature:** Only ~25% of tick labels are shown to reduce clutter on large ranges.

### 7. `large_range_custom_interval.svg`
**Configuration:**
```python
ColumnChart(
    data=data,  # [100, 250, 500, 750, 1000, 800, 600]
    labels=categories,
    axis_tick_interval=10,
)
```

**Key Feature:** Custom interval of 10 creates clean, readable labels for large ranges.

### 8. `float_proportion_interval.svg`
**Configuration:**
```python
LineChart(
    data=data,
    labels=categories,
    axis_tick_interval=0.2,  # Show ~20% of labels
)
```

**Key Feature:** Float proportion (0.2 = 20%) provides fine-grained control over label density.

## Implementation Details

### Changes to `charted/charts/axes.py`

#### 1. Fixed Zero Inclusion in `generate_tick_values()` (lines 224-230)
```python
# Ensure 0 is always in label_values when data spans zero (for visual reference)
if min_value < 0 < max_value and label_values:
    has_zero_label = any(abs(t) < 1e-9 for t in label_values)
    if not has_zero_label:
        # Add 0.0 explicitly to ensure the zero line is labeled
        # when the axis spans across zero
        label_values = sorted(label_values + [0.0])
```

#### 2. Fixed Zero Index Handling in `calculate_axis_dimensions()` (lines 105-112)
```python
# Ensure zero is included if zero_index is True
# - If all values are positive, set min to 0
# - If all values are negative, set max to 0
if zero_index:
    if min_value > 0:
        min_value = 0
    elif max_value < 0:
        max_value = 0
```

#### 3. Fixed Zero Inclusion for Labeled Axes in `calculate_axis_values()` (lines 260-262)
```python
# Ensure zero is included in values when spanning negative to positive
if min_val < 0 < max_val and 0 not in values:
    values = sorted(values + [0])
```

## Running the Examples

```bash
cd ~/git/charted
python examples/axis-interval-demos/demo_axis_intervals.py
```

This will regenerate all example SVGs in `/tmp/charted-axis-demos/`.

## Tests

Comprehensive tests are in `tests/charts/test_axis_tick_interval.py`:

```bash
python -m pytest tests/charts/test_axis_tick_interval.py -xvs
```

All 14 tests pass, covering:
- Zero inclusion when spanning negative to positive
- Zero index for all-positive and all-negative values
- Integer, percentage, and float interval formats
- Both X and Y axis support
- Edge cases with small ranges and values between -1 and 1
