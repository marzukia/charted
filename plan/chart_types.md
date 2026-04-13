# Test Plan: Chart Types (Column, Line, Scatter)

**Created:** 2025-01-XX  
**Priority:** HIGH  
**Goal:** Guarantee chart rendering functionality before refactoring

## Objectives

1. **Verify chart construction** - All three chart types can be instantiated with valid data
2. **Verify SVG output** - Charts generate valid, well-formed SVG
3. **Verify data transformation** - Input data correctly mapped to visual elements
4. **Guard against regressions** - Catch breaking changes before they reach users

## Test Categories

### Happy Path Tests (60%)

| Test Case | Input | Expected Output | Verify |
|-----------|-------|-----------------|--------|
| `test_column_basic` | `[10, 20, 30]` | Valid SVG with 3 bars | `assert "<rect"` in output, 3 bars rendered |
| `test_line_basic` | `[(0,10), (1,20), (2,30)]` | Valid SVG with polyline | `assert "<polyline"` in output |
| `test_scatter_basic` | `[(0,10), (1,20), (2,30)]` | Valid SVG with circles | `assert "<circle"` in output 3 times |
| `test_column_stacked` | `[[10,5], [15,10], [20,15]]` | Stacked bars with 2 segments | 6 `<rect>` elements total |
| `test_line_multi_series` | `[[10,20,30], [15,25,35]]` | Multiple polylines | 2 `<polyline>` elements |
| `test_scatter_multi_series` | `[[...], [...]]` | Multiple point series | Correct circle count |

### Sad Path Tests (40%)

| Test Case | Input | Expected Behavior | Verify |
|-----------|-------|-------------------|--------|
| `test_column_empty_data` | `[]` | `ValueError` raised | `pytest.raises(ValueError)` |
| `test_line_empty_data` | `[]` | `ValueError` raised | `pytest.raises(ValueError)` |
| `test_scatter_empty_data` | `[]` | `ValueError` raised | `pytest.raises(ValueError)` |
| `test_column_single_point` | `[42]` | Renders 1 bar | 1 `<rect>` element |
| `test_line_single_point` | `[(0, 42)]` | Renders single point | 1 `<polyline>` or point marker |
| `test_scatter_single_point` | `[(0, 42)]` | Renders single circle | 1 `<circle>` element |
| `test_column_negative_values` | `[-10, -20, -30]` | Bars render below axis | SVG contains negative y-coords or visual markers |
| `test_line_negative_values` | `[(0,-10), (1,-20)]` | Line passes through negative | SVG renders without error |
| `test_scatter_negative_values` | `[(0,-10), (1,-20)]` | Points in negative quadrant | SVG renders without error |
| `test_column_large_values` | `[1e6, 2e6, 3e6]` | No overflow, renders | SVG valid, no NaN/Inf in output |
| `test_line_large_values` | `[(0,1e6), (1,2e6)]` | No overflow | SVG renders without error |
| `test_column_unicode_labels` | `[10, 20]`, labels=`["日本語", "中文"]` | Unicode renders | SVG contains UTF-8 characters |

## Test File Structure

```python
# tests/charts/test_column.py
class TestColumnChartHappyPath:
    def test_basic_column_chart(...): ...
    def test_stacked_column_chart(...): ...
    
class TestColumnChartSadPath:
    def test_empty_data_raises(...): ...
    def test_single_point(...): ...
    def test_negative_values(...): ...
    def test_large_values(...): ...

# tests/charts/test_line.py
class TestLineChartHappyPath: ...
class TestLineChartSadPath: ...

# tests/charts/test_scatter.py
class TestScatterChartHappyPath: ...
class TestScatterChartSadPath: ...
```

## Acceptance Criteria

- ✅ All happy path tests pass
- ✅ All sad path tests pass (edge cases handled gracefully)
- ✅ Code coverage for column.py, line.py, scatter.py > 80%
- ✅ No regressions in existing tests
- ✅ Visual baselines updated if rendering changes

## Regression Risk

- `tests/charts/test_visual.py` - 16 existing tests rely on these modules
- `tests/charts/test_chart.py` - 3 base chart tests

## Timeline

- **Day 1:** Write happy path tests for all 3 chart types
- **Day 2:** Write sad path tests, verify coverage
- **Day 3:** Debug failures, update baselines if needed
