# Test Plan: Axis Rendering (XAxis, YAxis)

**Created:** 2025-01-XX  
**Priority:** HIGH  
**Goal:** Verify axis labeling, grid lines, and tick marks render correctly

## Objectives

1. **Verify axis construction** - XAxis/YAxis instantiate correctly with parameters
2. **Verify tick generation** - Ticks placed at correct intervals
3. **Verify grid line rendering** - Grid lines align with ticks
4. **Verify label formatting** - Numbers formatted correctly (decimal places, prefixes)

## Test Categories

### Happy Path Tests (60%)

| Test Case | Input | Expected Output | Verify |
|-----------|-------|-----------------|--------|
| `test_xaxis_basic_ticks` | `range=100, ticks=10` | 10 ticks at 0,10,20...90 | 10 tick marks, positions correct |
| `test_yaxis_basic_ticks` | `range=100, ticks=10` | 10 ticks at 0,10,20...90 | 10 tick marks, positions correct |
| `test_xaxis_with_labels` | `labels=['A','B','C']` | 3 text labels at tick positions | SVG contains "A", "B", "C" |
| `test_yaxis_with_gridlines` | `gridlines=True` | Horizontal lines at each tick | `<line>` elements with correct y |
| `test_xaxis_decimal_format` | `precision=2` | Labels show 2 decimals | "10.00", "20.00" in SVG |
| `test_yaxis_range_explicit` | `min=0, max=50` | Range exactly 0-50 | Tick bounds verify via lxml |

### Sad Path Tests (40%)

| Test Case | Input | Expected Behavior | Verify |
|-----------|-------|-------------------|--------|
| `test_xaxis_zero_range` | `min=0, max=0` | Graceful handling or error | Exception or default range applied |
| `test_yaxis_invalid_ticks` | `ticks=0` | Error or sensible default | Exception or falls back to auto |
| `test_xaxis_negative_ticks` | `ticks=-5` | Error raised | `ValueError` or `AssertionError` |
| `test_yaxis_overflow_labels` | `range=1e10, ticks=100` | Labels don't overlap or crash | SVG renders, may truncate labels |
| `test_xaxis_nan_input` | `min=float('nan')` | Error raised | `ValueError` with NaN message |
| `test_yaxis_none_labels` | `labels=None` | Default numeric labels | Auto-generated number labels appear |
| `test_xaxis_empty_string_labels` | `labels=["","",""]` | Renders empty or spaces | SVG valid, no crash |
| `test_yaxis_huge_precision` | `precision=20` | Reasonable truncation | Labels < 100 chars each |

## Test File Structure

```python
# tests/charts/test_axes.py

class TestXAxisHappyPath:
    def test_basic_ticks(self): ...
    def test_custom_labels(self): ...
    def test_with_gridlines(self): ...
    def test_decimal_formatting(self): ...

class TestXAxisSadPath:
    def test_zero_range(self): ...
    def test_invalid_tick_count(self): ...
    def test_nan_input(self): ...

class TestYAxisHappyPath:
    def test_basic_ticks(self): ...
    def test_with_gridlines(self): ...
    def test_explicit_range(self): ...

class TestYAxisSadPath:
    def test_zero_range(self): ...
    def test_negative_ticks(self): ...
    def test_label_overflow(self): ...
```

## Acceptance Criteria

- ✅ All happy path tests pass
- ✅ All sad path tests pass (edge cases handled gracefully)
- ✅ Code coverage for axes.py > 70%
- ✅ Visual output matches baselines for happy path
- ✅ No regressions in chart rendering tests

## Regression Risk

- `tests/charts/test_visual.py` - All 16 visual tests use axes
- `tests/charts/test_chart.py` - Base chart tests may instantiate axes
- **Critical:** axes.py is 362 lines, core rendering logic - HIGH regression risk

## Dependencies

- lxml for SVG parsing
- May need to refactor `Axis` base class if it's too abstract

## Timeline

- **Day 1:** Happy path tests for XAxis (basic functionality)
- **Day 2:** Happy path tests for YAxis + sad path for both
- **Day 3:** Edge cases, coverage review, debug failures
