# Charted Test Suite

Testing documentation for the charted library.

## Overview

The charted test suite ensures:
- **Correctness**: Charts render correctly with proper SVG output
- **Performance**: Chart generation meets performance targets
- **Accessibility**: Charts meet basic WCAG guidelines
- **Reliability**: CLI and file loading work as expected

## Test Categories

### Unit Tests (`tests/charts/`, `tests/utils/`, `tests/themes/`)

Focus on individual components:

```bash
# Run all unit tests
uv run pytest tests/charts/ tests/utils/ tests/themes/ -v

# Run specific test file
uv run pytest tests/charts/test_bar.py -v

# Run with coverage
uv run pytest tests/charts/ --cov=charted --cov-report=term-missing
```

### Property-Based Tests (`tests/properties/`)

Use Hypothesis to generate edge cases:

```bash
# Run property tests
uv run pytest tests/properties/ -v

# With specific seed for reproducibility
uv run pytest tests/properties/ --hypothesis-seed=0

# Increase examples
uv run pytest tests/properties/ --hypothesis-max-examples=200
```

### Integration Tests (`tests/cli/`)

Test end-to-end workflows:

```bash
# Run CLI integration tests
uv run pytest tests/cli/ -v

# Test specific command
uv run pytest tests/cli/test_create.py -v
```

### Visual Regression Tests (`tests/visual/`)

Verify chart rendering with different themes and edge cases:

```bash
# Run visual regression tests
uv run pytest tests/visual/ -v

# Generate SVG outputs for inspection
uv run pytest tests/visual/ --tb=short
```

### Performance Benchmarks (`tests/benchmarks/`)

Measure chart generation performance:

```bash
# Run benchmarks
uv run --with pytest-benchmark pytest tests/benchmarks/ --benchmark-only

# Save benchmark results
uv run --with pytest-benchmark pytest tests/benchmarks/ --benchmark-autosave

# Compare with previous results
uv run --with pytest-benchmark pytest tests/benchmarks/ --benchmark-compare
```

### Accessibility Tests (`tests/accessibility/`)

Check WCAG compliance:

```bash
# Run accessibility tests
uv run pytest tests/accessibility/ -v
```

## Running All Tests

```bash
# Full test suite (excluding slow benchmarks)
uv run pytest tests/ -v --ignore=tests/benchmarks/

# With coverage report
uv run pytest tests/ --cov=charted --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Test Structure

```
tests/
├── accessibility/          # WCAG accessibility tests
│   └── test_svg_accessibility.py
├── benchmarks/             # Performance benchmarks
│   └── test_chart_generation.py
├── charts/                 # Chart-specific unit tests
│   ├── test_bar.py
│   ├── test_column.py
│   ├── test_line.py
│   ├── test_pie.py
│   ├── test_radar.py
│   ├── test_scatter.py
│   ├── test_bar_extended.py
│   ├── test_column_extended.py
│   └── test_pie_extended.py
├── cli/                    # CLI integration tests
│   ├── test_batch.py
│   └── test_create.py
├── fonts/                  # Font-related tests
├── html/                   # HTML element tests
├── properties/             # Property-based tests
│   ├── test_color_properties.py
│   ├── test_data_model_properties.py
│   └── test_validation_properties.py
├── themes/                 # Theme system tests
│   └── test_registry.py
├── utils/                  # Utility function tests
│   ├── test_series_style.py
│   ├── test_series_style_extended.py
│   ├── test_theme_manager.py
│   └── test_validation.py
└── visual/                 # Visual regression tests
    └── test_visual_regression.py
```

## Writing Tests

### Unit Tests

Follow the pattern:

```python
def test_component_feature():
    """Test specific feature."""
    # Arrange
    component = Component(arg1, arg2)
    
    # Act
    result = component.method()
    
    # Assert
    assert result == expected
```

### Property-Based Tests

Use Hypothesis for edge case discovery:

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers(), min_size=1))
def test_validation_accepts_valid_data(data):
    """Validator should accept valid numeric data."""
    result = validate(data)
    assert result is not None
```

### Integration Tests

Test complete workflows:

```python
def test_cli_workflow():
    """Test end-to-end CLI workflow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup
        data_file = Path(tmpdir) / "data.json"
        data_file.write_text('{"data": [1, 2, 3]}')
        
        # Execute
        result = subprocess.run(
            ["charted", "create", "bar", "output.svg", "--data", str(data_file)]
        )
        
        # Assert
        assert result.returncode == 0
        assert Path(tmpdir, "output.svg").exists()
```

## Coverage Targets

| Module | Target | Current |
|--------|--------|---------|
| Overall | 90% | 91% ✅ |
| Core (themes, utils) | 90% | 85-100% ✅ |
| Charts | 90% | 92-100% ✅ |
| CLI | 85% | 87% ✅ |

## Continuous Integration

Tests run automatically on:
- **Pull Requests**: All tests must pass
- **Main branch**: Full test suite with coverage
- **Nightly**: Extended tests (benchmarks, mutation testing)

See `.github/workflows/ci.yml` for configuration.

## Troubleshooting

### Tests Fail Randomly

```bash
# Use fixed hypothesis seed
uv run pytest tests/properties/ --hypothesis-seed=0

# Increase timeout
uv run pytest tests/ -k "slow" --timeout=60
```

### Coverage Too Low

```bash
# See missing lines
uv run pytest --cov=charted --cov-report=term-missing

# Generate detailed HTML report
uv run pytest --cov=charted --cov-report=html
open htmlcov/index.html
```

### Benchmark Failures

```bash
# Clear benchmark data
rm -rf .benchmarks/

# Run with fewer rounds (faster)
uv run pytest tests/benchmarks/ --benchmark-min-rounds=1
```

## Related Documentation

- [Mutation Testing Guide](../notes/mutation-testing.md)
- [Fuzz Testing Guide](../notes/fuzz-testing.md)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)

## Contributing

When adding new features:
1. **Write tests first** (TDD encouraged)
2. **Achieve 90%+ coverage** for new code
3. **Add benchmarks** for performance-critical code
4. **Update documentation** if needed

For test-related issues, see [GitHub Issues](https://github.com/marzukia/charted/issues).
