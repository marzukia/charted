# Configuration Object Pattern for Chart Constructors

## Overview

This document describes the configuration object pattern designed to reduce excessive constructor parameters across all chart classes in the `charted` library. This addresses Issue #70 (Long functions & excessive parameters refactoring) and Issue #76 (Design config object pattern for chart constructors).

## Problem Statement

Current constructor parameter counts:
- `Chart.__init__`: 14 parameters
- `RadarChart.__init__`: 13 parameters
- `BarChart.__init__`: 11 parameters
- `ColumnChart.__init__`: 11 parameters
- `LineChart.__init__`: 11 parameters
- `PieChart.__init__`: 10 parameters
- `ScatterChart.__init__`: 8 parameters

This creates:
- Poor readability and discoverability
- Difficult to maintain backward compatibility
- Hard to provide sensible defaults
- IDE autocomplete becomes less useful

## Solution: Configuration Object Pattern

### Design Goals

1. **Reduce constructor parameters** to 2-4 (data, config, optional overrides)
2. **Type safety** with dataclasses for IDE support
3. **Backward compatibility** - old API continues to work
4. **Composability** - configs can be extended and overridden
5. **Follow existing patterns** - similar to `RadarRenderer` separation

### Recommended Approach: Dataclasses

We recommend **dataclasses** over TypedDict for the following reasons:

| Aspect | Dataclasses | TypedDict |
|--------|-------------|-----------|
| IDE autocomplete | ✅ Full support | ⚠️ Limited |
| Runtime validation | ✅ With `__post_init__` | ❌ None |
| Default values | ✅ Native support | ⚠️ Requires defaults |
| Inheritance | ✅ Clean subclassing | ❌ Not supported |
| Mutable vs immutable | ✅ Configurable | ✅ Read-only option |
| Serialization | ⚠️ Requires helper | ✅ dict() native |
| Type checking | ✅ Full mypy support | ✅ Full mypy support |

**Dataclasses win** for this use case because:
1. Charts need runtime validation (e.g., `inner_radius` must be 0.0-1.0)
2. We need clean inheritance hierarchies
3. Better IDE experience for users
4. Can still serialize to dict when needed

## Architecture

### Base Config Class (`ChartConfig`)

```python
@dataclass
class ChartConfig:
    """Base configuration for all chart types."""
    
    # Common appearance settings
    width: float = 500
    height: float = 500
    title: str | None = None
    theme: Theme | None = None
    
    # Data styling
    series_names: list[str] | None = None
    series_styles: list[SeriesStyleConfig] | None = None
    
    # Behavior flags
    render_axes: bool = True
    zero_index: bool = True
    
    def to_dict(self) -> dict:
        """Convert config to dictionary for serialization."""
        return dataclasses.asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create config from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in dataclasses.fields(cls)})
```

### Chart-Specific Configs

```python
@dataclass
class BarChartConfig(ChartConfig):
    """Configuration for horizontal bar charts."""
    
    # Bar-specific settings
    bar_gap: float = 0.50  # Gap between bars as ratio
    x_stacked: bool = False
    
    # Labels (bar charts use y-axis for categories)
    labels: Labels | None = None


@dataclass
class ColumnChartConfig(ChartConfig):
    """Configuration for vertical column charts."""
    
    # Column-specific settings
    column_gap: float = 0.20  # Gap between columns as ratio
    y_stacked: bool = True
    
    # Labels
    labels: Labels | None = None


@dataclass
class LineChartConfig(ChartConfig):
    """Configuration for line charts."""
    
    # Line-specific settings
    line_style: str = "solid"  # solid, dashed, dotted
    marker_shape: str = "circle"  # circle, square, diamond, none
    marker_size: float = 4.0
    area_fill: bool = False
    area_fill_opacity: float = 0.3
    
    # Data
    x_data: Vector | None = None
    labels: Labels | None = None


@dataclass
class PieChartConfig(ChartConfig):
    """Configuration for pie/doughnut charts."""
    
    # Pie-specific settings
    inner_radius: float = 0.0  # 0 = pie, >0 = doughnut
    explode: float | list[float] = 0.0
    start_angle: float = 0.0
    
    # Labels
    labels: Labels | None = None


@dataclass
class ScatterChartConfig(ChartConfig):
    """Configuration for scatter plots."""
    
    # Scatter-specific settings
    marker_shape: str = "circle"
    marker_size: float = 4.0
    
    # Data
    x_data: Vector | None = None


@dataclass
class RadarChartConfig(ChartConfig):
    """Configuration for radar/spider charts."""
    
    # Radar-specific settings
    radius: float = 0.45  # Chart radius as ratio of min dimension
    grid_levels: int = 5
    show_axis_labels: bool = True
    label_offset: float = 20.0
    
    # Labels (required for radar)
    labels: Labels
```

## API Usage Examples

### Before (Current API)

```python
# BarChart with many parameters
chart = BarChart(
    data=[120, 180, 210],
    labels=['Q1', 'Q2', 'Q3'],
    bar_gap=0.3,
    width=600,
    height=400,
    zero_index=True,
    title="Sales by Quarter",
    theme="dark",
    series_names=["Revenue"],
    series_styles=[{"fill": "#3498db"}],
    x_stacked=False
)
```

### After (New Config API)

```python
# Using config object - cleaner and more discoverable
config = BarChartConfig(
    width=600,
    height=400,
    title="Sales by Quarter",
    theme="dark",
    bar_gap=0.3,
    labels=['Q1', 'Q2', 'Q3'],
    series_names=["Revenue"],
    series_styles=[{"fill": "#3498db"}]
)

chart = BarChart(data=[120, 180, 210], config=config)
```

### After (Backward Compatible API)

```python
# Old API still works - backward compatible
chart = BarChart(
    data=[120, 180, 210],
    labels=['Q1', 'Q2', 'Q3'],
    width=600,
    title="Sales by Quarter"
)

# Or mix config with overrides
config = BarChartConfig(width=600, title="Sales")
chart = BarChart(
    data=[120, 180, 210],
    config=config,
    labels=['Q1', 'Q2', 'Q3']  # Override specific param
)
```

### Advanced: Config Reuse and Composition

```python
# Define reusable config
dark_theme_config = BarChartConfig(
    width=800,
    height=600,
    theme="dark",
    bar_gap=0.25,
    series_styles=[{"fill": "#3498db"}, {"fill": "#e74c3c"}]
)

# Use across multiple charts
chart1 = BarChart(data=quarter1_data, config=dark_theme_config, labels=labels)
chart2 = BarChart(data=quarter2_data, config=dark_theme_config, labels=labels)

# Override specific settings
light_config = dark_theme_config.copy()
light_config.theme = "light"
chart3 = BarChart(data=quarter3_data, config=light_config, labels=labels)
```

## Implementation Strategy

### Phase 1: Create Config Classes

**File**: `charted/config.py` (extend existing) or `charted/chart_config.py` (new)

```python
# Add to charted/config.py
from dataclasses import dataclass, field
from typing import Self

@dataclass
class ChartConfig:
    # Base implementation...
    pass

# Chart-specific configs follow...
```

### Phase 2: Update Chart Constructors

Pattern for each chart class (e.g., `BarChart`):

```python
def __init__(
    self,
    data: Vector | Vector2D,
    config: BarChartConfig | None = None,
    # Keep old params for backward compatibility
    labels: Labels = None,
    bar_gap: float = None,
    width: float = 500,
    height: float = 500,
    # ... other params
):
    # Merge config with explicit params (explicit wins)
    if config is None:
        config = BarChartConfig()
    
    # Apply config values if not explicitly provided
    labels = labels if labels is not None else config.labels
    bar_gap = bar_gap if bar_gap is not None else config.bar_gap
    width = width if width != 500 else config.width  # Only if using default
    height = height if height != 500 else config.height
    # ... repeat for all params
    
    # Store final config
    self.config = config
    
    # Rest of initialization...
```

### Phase 3: Add Config Property Access

```python
class BarChart(Chart):
    @property
    def config(self) -> BarChartConfig:
        """Access chart configuration."""
        return self._config
    
    @config.setter
    def config(self, value: BarChartConfig):
        self._config = value
```

### Phase 4: Deprecation Warnings (Optional - Future)

For future major version, add deprecation warnings to old-style usage:

```python
import warnings

def __init__(self, data, labels=None, bar_gap=None, ...):
    if labels is not None or bar_gap is not None:  # Old API detected
        warnings.warn(
            "Passing parameters directly to constructor is deprecated. "
            "Use config object instead: BarChart(data=data, config=BarChartConfig(labels=...))",
            DeprecationWarning,
            stacklevel=2
        )
```

## Type Safety Benefits

### IDE Autocomplete

```python
config = BarChartConfig(
    # IDE shows all available fields with types and defaults
    width=600,      # float = 500
    height=400,     # float = 500
    title="Sales",  # str | None = None
    bar_gap=0.3,    # float = 0.50
    # ... autocomplete for all fields
)
```

### Type Checking (mypy/pyright)

```python
# ❌ Type error - caught by static analysis
config = BarChartConfig(invalid_param=True)  # Error: unexpected keyword

# ✅ Type error - caught early
config.width = "500"  # Error: str not assignable to float
```

## Migration Guide

### For Library Users

**Step 1**: No changes required - existing code continues to work

**Step 2** (Optional): Migrate to config objects gradually

```python
# Before
chart = BarChart(data=[1, 2, 3], labels=['a', 'b', 'c'], width=600)

# After (optional)
config = BarChartConfig(width=600, labels=['a', 'b', 'c'])
chart = BarChart(data=[1, 2, 3], config=config)
```

### For Library Developers

1. Create config classes first
2. Update constructors to accept optional config parameter
3. Merge config with explicit parameters (explicit wins)
4. Add config property for runtime access
5. Test backward compatibility thoroughly

## Testing Strategy

### Unit Tests

```python
def test_bar_chart_config_defaults():
    config = BarChartConfig()
    assert config.width == 500
    assert config.height == 500
    assert config.bar_gap == 0.50

def test_backward_compatibility():
    # Old API should work
    chart1 = BarChart(data=[1, 2, 3], labels=['a', 'b'], width=600)
    
    # New API should work
    config = BarChartConfig(width=600, labels=['a', 'b'])
    chart2 = BarChart(data=[1, 2, 3], config=config)
    
    # Both should produce equivalent results
    assert chart1.width == chart2.width

def test_config_override():
    config = BarChartConfig(width=600)
    chart = BarChart(data=[1, 2, 3], config=config, width=800)
    assert chart.width == 800  # Explicit param wins
```

## Future Enhancements

1. **Config validation**: Add `__post_init__` for runtime validation
   ```python
   def __post_init__(self):
       if not 0 <= self.inner_radius <= 1:
           raise ValueError("inner_radius must be between 0 and 1")
   ```

2. **Builder pattern** for complex configs:
   ```python
   config = BarChartConfig.builder() \
       .with_width(600) \
       .with_theme("dark") \
       .build()
   ```

3. **From TOML/JSON**: Load configs from files
   ```python
   config = BarChartConfig.from_file(".chartedrc.toml")
   ```

4. **Schema validation** with Pydantic for advanced use cases

## Related Issues

- Issue #70: Long functions & excessive parameters refactoring
- Issue #76: Design config object pattern for chart constructors

## References

- [Python Dataclasses Documentation](https://docs.python.org/3/library/dataclasses.html)
- [RadarRenderer Pattern](../utils/radar_renderer.py) - Example of logic extraction
- [Existing Config System](../config.py) - Current TOML configuration
