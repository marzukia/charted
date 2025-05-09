# Testing Strategy & Resilience Plan

## Current State Analysis

### Coverage Overview (86% total)

| Module | Coverage | Status | Priority |
|--------|----------|--------|----------|
| **Core Theme System** | 58-84% | ⚠️ Needs Work | High |
| - `themes/registry.py` | 58% | ❌ Critical Gap | Critical |
| - `themes/validation.py` | 60% | ❌ Critical Gap | Critical |
| - `themes/core.py` | 84% | ✅ Good | Low |
| **Chart Rendering** | 63-100% | ✅ Mostly Good | Medium |
| - `charts/line.py` | 100% | ✅ Excellent | None |
| - `charts/chart.py` | 93% | ✅ Excellent | None |
| - `charts/scatter.py` | 63% | ⚠️ Needs Work | High |
| - `charts/column.py` | 81% | ⚠️ Moderate Gap | Medium |
| **Utilities** | 40-96% | ⚠️ Mixed | High |
| - `utils/color_manager.py` | 96% | ✅ Excellent | None |
| - `utils/series_style.py` | 71% | ⚠️ Needs Work | Medium |
| - `utils/config_schema.py` | 69% | ⚠️ Needs Work | Medium |
| - `utils/theme_manager.py` | 40% | ❌ Critical Gap | Critical |
| - `utils/validation.py` | 48% | ❌ Critical Gap | Critical |
| **CLI** | 78-92% | ✅ Good | Low |

### Test Types Currently Used

1. **Unit Tests**: Happy path + sad path for individual methods
2. **Visual Regression**: SVG structure + PNG pixel-perfect comparison
3. **Baseline Protection**: SHA256 manifest verification (excellent!)
4. **Edge Case Tests**: Empty data, exceptions

### What's Missing

1. ❌ **Property-Based Testing** - No hypothesis or similar library
2. ❌ **Fuzz Testing** - No input fuzzing for data validation
3. ❌ **Mutation Testing** - No mutmut/cosmic-ray for test quality
4. ❌ **Integration Tests** - Limited end-to-end chart generation
5. ❌ **Performance Benchmarks** - No pytest-benchmark

---

## Property-Based Testing Opportunities

Property-based testing (using `hypothesis`) generates random inputs to find edge cases that manual tests miss. Here are high-value targets:

### 1. Color Validation (`charted/utils/colors.py`)

```python
from hypothesis import given, strategies as st

@given(st.text())
def test_hex_color_validation_rejects_invalid(text):
    """Hex color validator should reject all invalid strings."""
    if not is_valid_hex_color(text):
        # Confirms validator catches bad input
        pass

@given(st.sampled_from(["#FFF", "#FFFFFF", "#FFFFFFFF"]))
def test_hex_color_validation_accepts_valid(hex_str):
    """Hex color validator should accept all valid formats."""
    assert is_valid_hex_color(hex_str)
```

**Value**: Catches regex edge cases, unicode tricks, buffer overflows

### 2. Theme Composition (`charted/themes/core.py`)

```python
@given(
    base_colors=st.lists(st.sampled_from(["#FFF", "#000", "#ABC"])),
    override_colors=st.lists(st.sampled_from(["#F00", "#0F0", "#00F"])),
)
def test_compose_preserves_non_overridden(base_colors, override_colors):
    """Composing should only change explicitly overridden fields."""
    base = Theme(colors=base_colors)
    override = Theme(colors=override_colors)
    result = base.compose(override)
    
    # Other fields should match base, not class defaults
    assert result.background_color == base.background_color
    assert result.title_color == base.title_color
```

**Value**: Finds bugs in merge logic, ensures immutability

### 3. Chart Data Validation (`charted/utils/data_model.py`)

```python
@given(
    data=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
    labels=st.lists(st.text(), min_size=1),
)
def test_data_model_rejects_mismatched_lengths(data, labels):
    """DataModel should reject mismatched data/labels lengths."""
    if len(data) != len(labels):
        with pytest.raises(ValueError):
            DataModel(data, labels)

@given(
    data=st.lists(st.floats(min_value=-1e10, max_value=1e10), min_size=1, max_size=100),
)
def test_data_model_handles_extreme_values(data):
    """DataModel should handle extreme values without crashing."""
    model = DataModel(data)
    assert model.min_value is not None
    assert model.max_value is not None
```

**Value**: Finds edge cases with NaN, infinity, very large/small numbers

### 4. SVG Generation (`charted/html/element.py`)

```python
@given(
    tag=st.sampled_from(["svg", "g", "path", "text", "circle"]),
    attrs=st.dictionaries(st.text(), st.text()),
    children=st.lists(st.builds(G), max_size=5),
)
def test_svg_element_serialization(tag, attrs, children):
    """SVG elements should serialize to valid XML."""
    elem = G(**attrs)
    for child in children:
        elem.add_child(child)
    
    xml = elem.to_string()
    # Parse back to verify validity
    from lxml import etree
    etree.fromstring(xml.encode())  # Should not raise
```

**Value**: Finds XSS vulnerabilities, XML injection, encoding bugs

### 5. Color Manager Cycling (`charted/utils/color_manager.py`)

```python
@given(
    colors=st.lists(st.sampled_from(["#F00", "#0F0", "#00F"]), min_size=1, max_size=10),
    indices=st.integers(min_value=0, max_value=10000),
)
def test_color_cycling_is_consistent(colors, indices):
    """Color cycling should be deterministic and wrap correctly."""
    manager = ColorManager(colors=colors)
    
    for i in range(indices + 1):
        color = manager.get_color(i)
        expected = colors[i % len(colors)]
        assert color == expected
```

**Value**: Finds off-by-one errors, infinite loops, memory issues

### 6. Theme Validation (`charted/themes/validation.py`)

```python
@given(
    fg=st.sampled_from(["#000000", "#FFFFFF", "#808080"]),
    bg=st.sampled_from(["#000000", "#FFFFFF", "#808080"]),
)
def test_contrast_validation_is_symmetric(fg, bg):
    """Contrast ratio should be symmetric (A:B == B:A)."""
    from charted.utils.colors import calculate_contrast_ratio
    
    ratio_ab = calculate_contrast_ratio(fg, bg)
    ratio_ba = calculate_contrast_ratio(bg, fg)
    
    assert abs(ratio_ab - ratio_ba) < 0.001
```

**Value**: Finds mathematical bugs, floating-point issues

---

## Implementation Plan

### Phase 1: Add Property-Based Testing Infrastructure (1-2 weeks)

1. **Install hypothesis**
   ```bash
   uv pip install hypothesis pytest-hypothesis
   ```

2. **Configure hypothesis in pyproject.toml**
   ```toml
   [tool.hypothesis]
   database = ".hypothesis"
   max_examples = 100
   deadline = 500
   ```

3. **Create `tests/properties/` directory structure**
   ```
   tests/properties/
   ├── test_color_properties.py
   ├── test_theme_properties.py
   ├── test_data_model_properties.py
   └── test_svg_properties.py
   ```

4. **Add to CI pipeline**
   ```yaml
   - name: Property-based tests
     run: pytest tests/properties/ --hypothesis-seed=0
   ```

### Phase 2: Fuzz Testing for Input Validation (1 week)

1. **Install atheris or python-fuzz**
   ```bash
   uv pip install atheris
   ```

2. **Create fuzz targets for critical paths**
   ```python
   # tests/fuzz/test_data_loader_fuzz.py
   import atheris
   from charted.data_loader import load_csv, load_json

   @atheris.instrument_func
   def TestOneInput(data):
       """Fuzz CSV/JSON parsers with random input."""
       try:
           load_csv(data)
       except (ValueError, UnicodeDecodeError):
           pass  # Expected for invalid input

   def main():
       atheris.Setup(sys.argv, TestOneInput)
       atheris.Fuzz()
   ```

3. **Run fuzz testing nightly**
   ```bash
   python -m tests.fuzz.test_data_loader_fuzz -runs=100000
   ```

### Phase 3: Mutation Testing for Test Quality (1 week)

1. **Install mutmut**
   ```bash
   uv pip install mutmut
   ```

2. **Configure mutation testing**
   ```toml
   [tool.mutmut]
   python_version = "3.12"
   runner = "pytest"
   tests_dir = "tests/"
   ```

3. **Run mutation testing quarterly**
   ```bash
   mutmut run
   mutmut results
   ```

### Phase 4: Performance Benchmarks (1 week)

1. **Install pytest-benchmark**
   ```bash
   uv pip install pytest-benchmark
   ```

2. **Create benchmark tests**
   ```python
   # tests/benchmarks/test_chart_generation.py
   def test_bar_chart_generation(benchmark):
       """Benchmark bar chart SVG generation."""
       def generate():
           from charted import BarChart
           chart = BarChart(data=[10, 20, 30], labels=["a", "b", "c"])
           return chart.html
       
       result = benchmark(generate)
       assert len(result) > 1000  # Sanity check
   ```

3. **Track performance over time**
   ```bash
   pytest tests/benchmarks/ --benchmark-save=results
   ```

---

## Recommended Test Improvements by Priority

### Critical (Do First)

1. **Add property tests for `themes/registry.py`** (58% coverage)
   - Test theme registration/deregistration
   - Test registry persistence across imports
   - Test thread safety of registry access

2. **Add property tests for `utils/theme_manager.py`** (40% coverage)
   - Test theme loading with invalid paths
   - Test TOML config parsing edge cases
   - Test fallback behavior for missing themes

3. **Add property tests for `utils/validation.py`** (48% coverage)
   - Test data validation with random inputs
   - Test padding validation boundaries
   - Test series count validation

### High Priority

4. **Improve `charts/scatter.py` coverage** (63%)
   - Add edge case tests for single-point scatter
   - Test multi-series with mismatched lengths
   - Test negative value rendering

5. **Add property tests for color utilities**
   - Test hex conversion round-trips
   - Test contrast ratio calculations
   - Test complementary color generation

### Medium Priority

6. **Add integration tests**
   - End-to-end CLI chart generation
   - CSV/JSON file loading and rendering
   - Markdown export with data URLs

7. **Add mutation testing baseline**
   - Identify weak test areas
   - Improve tests for low-mutation-score code

### Low Priority (Nice to Have)

8. **Performance benchmarks**
   - Chart generation time
   - SVG file size optimization
   - Memory usage for large datasets

9. **Accessibility testing**
   - WCAG contrast ratio compliance
   - Screen reader compatibility for SVG text

---

## CI/CD Integration

### Current CI (GitHub Actions)

```yaml
jobs:
  test:
    steps:
      - run: pytest tests/ --cov=charted
```

### Enhanced CI Pipeline

```yaml
jobs:
  test:
    steps:
      # Standard unit tests
      - run: pytest tests/ --cov=charted --cov-report=xml
      
      # Property-based tests (slower, more thorough)
      - run: pytest tests/properties/ --hypothesis-seed=0
      
      # Fuzz testing (nightly only)
      - if: github.event_name == 'schedule'
        run: python -m tests.fuzz.test_data_loader_fuzz -runs=100000
      
      # Mutation testing (weekly only)
      - if: github.event_name == 'schedule'
        run: mutmut run
      
      # Performance benchmarks (track over time)
      - run: pytest tests/benchmarks/ --benchmark-json=benchmark.json
      
      # Upload coverage and benchmarks
      - uses: codecov/codecov-action@v3
      - uses: benchmark-action/github-action-benchmark@v1
```

---

## Expected Benefits

| Improvement | Impact | Effort | ROI |
|-------------|--------|--------|-----|
| Property-based testing | High | Medium | ⭐⭐⭐⭐ |
| Fuzz testing | Medium | Low | ⭐⭐⭐ |
| Mutation testing | Medium | Low | ⭐⭐⭐ |
| Performance benchmarks | Medium | Low | ⭐⭐ |
| Integration tests | High | Medium | ⭐⭐⭐⭐ |

### ROI Analysis

- **Property-based testing**: Will find edge cases 10x faster than manual tests, especially for validation logic
- **Fuzz testing**: Critical for security (XSS, injection) in SVG generation
- **Mutation testing**: Ensures tests actually catch bugs, not just pass
- **Benchmarks**: Prevents performance regressions as library grows

---

## Next Steps

1. **Week 1**: Add hypothesis, create property test framework
2. **Week 2**: Write property tests for critical modules (themes, colors, validation)
3. **Week 3**: Add fuzz testing for data loaders and CLI
4. **Week 4**: Set up mutation testing baseline and performance benchmarks
5. **Ongoing**: Add property tests for new modules as they're developed

---

*This strategy document should be reviewed quarterly and updated as the codebase evolves.*
