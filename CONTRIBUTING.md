# Contributing to Charted

Thank you for your interest in contributing to Charted! This document outlines guidelines and processes for contributing.

## Development Setup

```bash
# Install with development dependencies
uv pip install -e '.[dev]'
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=charted --cov-report=html
```

## Updating Visual Baselines

The visual regression tests in `tests/charts/test_visual.py` compare generated SVG charts against baseline files stored in `tests/baselines/`.

When you make legitimate changes to chart rendering that affect the visual output, you need to update the baselines:

### Option 1: Manual Update

1. Run the failing test to see the diff:
   ```bash
   pytest tests/charts/test_visual.py::test_column_chart_basic -v
   ```

2. Generate the new chart SVG:
   ```python
   from charted.charts.column import ColumnChart
   
   chart = ColumnChart({'A': 10, 'B': 20, 'C': 30})
   new_svg = chart.to_string()
   
   # Save as new baseline
   with open('tests/baselines/column_basic.svg', 'w') as f:
       f.write(new_svg)
   ```

3. Verify the test now passes:
   ```bash
   pytest tests/charts/test_visual.py::test_column_chart_basic -v
   ```

### Option 2: Using the Update Flag

Run tests with the `--update-baselines` flag to automatically regenerate all baselines:

```bash
pytest tests/charts/test_visual.py --update-baselines
```

**Note:** The `--update-baselines` flag is implemented via a custom pytest marker. If tests fail with "unknown option", the flag may not be implemented yet. Use the manual method above.

## When to Update Baselines

Update baselines when:
- ✅ You intentionally change chart rendering (colors, sizes, layouts)
- ✅ You fix visual bugs that affect output
- ✅ You add new visual features

Do NOT update baselines when:
- ❌ You're fixing unrelated code and tests suddenly fail (investigate first)
- ❌ The change is unintentional or you don't understand why it changed

## Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Write docstrings for public APIs
- Add tests for new features

## Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request
