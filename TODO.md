# Technical Debt - Charted Library

## High Priority

### 1. ~~Incorrect type checking in `charted/html/element.py`~~ ✅ DONE
**Line 14, 69**: Using `type(x) is list` instead of `isinstance(x, list)` or `type(x) == list`

---

### 2. ~~Mutable default arguments in `charted/html/element.py`~~ ✅ DONE
**Lines 6-7**:

---

### 3. ~~Unused `__new__` method in `charted/html/element.py`~~ ✅ DONE
**Lines 29-32**:

---

### 4. ~~Inconsistent exception handling in `charted/charts/chart.py`~~ ✅ DONE
**Lines 40, 107, 116**:

---

### 5. ~~Dead/redundant code in `charted/charts/chart.py`~~ ✅ DONE
**Lines 16-18**:

---

### 6. ~~Confusing variable naming in `charted/charts/chart.py`~~ ✅ DONE
**Lines 63-64**:

---

### 7. Unused class attributes in `charted/charts/column.py` ✅ DONE
**Line 8**:

---

### 8. ~~Incorrect comparison in `charted/charts/chart.py`~~ ✅ DONE
**Line 206**:

---

## Medium Priority

### 9. Missing type hints in several files

Multiple functions and methods lack proper type hints:
- `charted/charts/axes.py`: Several methods missing return type hints
- `charted/charts/chart.py`: Some methods lack complete type annotations
- `charted/utils/helpers.py`: Functions lack type hints

---

### 10. Duplicate code in `charted/charts/line.py` and `charted/charts/scatter.py`

Both files have nearly identical `representation` property implementations with the same transform chain:

```python
g = G(
    opacity=0.8,
    transform=[
        translate(-self.h_pad, -self.bottom_padding),
        rotate(180, self.width / 2, self.height / 2),
        scale(-1, 1),
        translate(-self.plot_width, 0),
    ],
)
```

**Issue**: This transform logic should be extracted to a common method in the `Chart` base class.

---

### 11. Magic numbers throughout the codebase

Examples:
- `charted/charts/column.py` line 40: `column_gap: float = 0.50`
- `charted/charts/scatter.py` line 47: `r=4` for marker size
- `charted/charts/line.py` line 57: `stroke_width=2`

**Issue**: These should be configurable via theme or constants.

---

### 12. Inconsistent error messages

- `charted/charts/chart.py` line 40: "No data was provided to the Chart element."
- `charted/charts/chart.py` line 107: "No data provided."
- `charted/charts/axes.py` line 25: "Need labels or data."

**Issue**: Inconsistent style and capitalization.

---

### 13. Redundant property accessors in `charted/charts/axes.py`

**Lines 200-218**: The `labels` property setter has complex logic that could be simplified:

```python
@labels.setter
def labels(self, labels: Vector | list[str] = None) -> None:
    if not labels:
        labels = []
        precision = 0
        for label in self.values:
            if "." in str(label):
                decimal_value = str(label).split(".")[-1]
                if float(decimal_value) > 0:
                    precision = 1
            value = round(label, precision) if precision > 0 else int(label)
            labels.append(value)
    else:
        labels = [*labels]
```

**Issue**: String manipulation for float precision detection is fragile. Use proper numeric methods.

---

### 14. Missing docstrings

Many classes and methods lack docstrings:
- `charted/charts/column.py`: `ColumnChart` class missing docstring
- `charted/charts/line.py`: `LineChart` class missing docstring
- `charted/charts/scatter.py`: `ScatterChart` class missing docstring

---

### 15. `None` handling inconsistency

Throughout the codebase, `None` defaults are used inconsistently:
- Some functions use `| None = None`
- Some use default values
- Line 42 in `chart.py`: `if not x_data and not x_labels:` - doesn't distinguish between `None` and empty list

---

## Low Priority

### 16. Import organization

Some files have unorganized imports. Following PEP 8, imports should be grouped:
1. Standard library
2. Third-party
3. Local application

---

### 17. Unused imports

Check for unused imports in:
- `charted/charts/chart.py`: `generate_complementary_colors` may not be used
- `charted/charts/axes.py`: Check if all helper functions are used

---

### 18. String concatenation vs f-strings

Some places still use string concatenation:
- `charted/html/element.py` line 43-47: Could use f-strings more efficiently

---

## Testing Gaps

### 19. Incomplete test coverage

Current tests don't cover:
- Error cases for invalid data
- Edge cases (empty data, single point, very large numbers)
- Stacking functionality
- Theme customization

---

### 20. No integration tests

No tests that verify complete chart generation from data to SVG output.

---

## Documentation

### 21. Missing README examples

The README shows basic usage but lacks:
- Multi-series charts
- Custom themes
- Error handling examples

---

### 22. No CHANGELOG

No version history or changelog file.

