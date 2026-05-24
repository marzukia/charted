# AGENTS.md — Charted (Python SVG Chart Library)

## Quick API Reference

```python
import charted
from charted import (
    BarChart, ColumnChart, LineChart, ScatterChart,
    PieChart, RadarChart, AreaChart, BoxPlot, Histogram,
    HeatmapChart, GanttChart,
)

# Bar (horizontal)
BarChart(data=[10, 20, 30], labels=["A", "B", "C"], title="Sales")

# Column (vertical)
ColumnChart(data=[10, 20, 30], labels=["A", "B", "C"])

# Line
LineChart(data=[[10, 20, 30]], labels=["Jan", "Feb", "Mar"])

# Scatter — NOTE: uses x_data/y_data, NOT data=
ScatterChart(x_data=[1, 2, 3], y_data=[10, 20, 30])

# Pie
PieChart(data=[35, 28, 18], labels=["A", "B", "C"])

# Radar
RadarChart(data=[85, 90, 75, 88, 92], labels=["Spd", "Str", "Def", "Tech", "Sta"])

# Area
AreaChart(data=[10, 20, 15, 25], labels=["Q1", "Q2", "Q3", "Q4"])

# Box Plot — each item in data is a raw distribution list
BoxPlot(data=[[1,2,3,4,5,6,7], [2,4,6,8,10]], labels=["A", "B"])

# Histogram — single flat list, bins param
Histogram(data=[1.2, 2.3, 2.5, 3.1, 4.0], bins=5)

# Heatmap — 2D matrix
HeatmapChart(data=[[1,2,3],[4,5,6],[7,8,9]], labels=["R1","R2","R3"])

# Gantt
GanttChart(tasks=[{"name": "Task 1", "start": 0, "end": 5}])
```

## Common Patterns

### Single series
```python
chart = BarChart(data=[120, 180, 210], labels=["Q1", "Q2", "Q3"], title="Revenue")
chart.save("chart.svg")
```

### Multi-series
```python
chart = ColumnChart(
    data=[[12, 22, 30], [-8, -15, -20]],
    labels=["Q1", "Q2", "Q3"],
    series_names=["Revenue", "Costs"],
)
```

### Stacked vs side-by-side
```python
# Column: stacked by default (y_stacked=True). Disable:
ColumnChart(data=[[1,2],[3,4]], labels=["A","B"], y_stacked=False)

# Bar: side-by-side by default. Stack with:
BarChart(data=[[1,2],[3,4]], labels=["A","B"], x_stacked=True)
```

### Dark theme
```python
chart = BarChart(data=[1,2,3], labels=["A","B","C"], theme="dark")
```

### Custom dimensions
```python
chart = LineChart(data=[[1,2,3]], labels=["A","B","C"], width=800, height=400)
```

## Auto Chart Type

```python
from charted import auto

chart = auto([10, 20, 30])                    # <= 6 items -> PieChart
chart = auto([10, 20, 30, 40, 50, 60, 70])   # > 6 items -> BarChart
chart = auto([[1,2,3,4,5],[6,7,8,9,10]])      # few rows, many cols -> ColumnChart
chart = auto({"col_a": [1,2,3], "col_b": [4,5,6]})  # dict -> from_dataframe
```

## Output Formats

```python
chart = BarChart(data=[1,2,3], labels=["A","B","C"])

chart.save("out.svg")              # SVG file
chart.save("out.png")              # PNG (requires cairosvg)
chart.save("out.png", scale=3)     # PNG at 3x resolution

svg_str = chart.to_svg()           # Raw SVG string
html_str = chart.to_html()         # Standalone HTML with embedded SVG
b64_uri = chart.to_base64()        # data:image/svg+xml,... URI
md_str = chart.to_markdown()       # Markdown image tag with inline data URL
```

## Themes

### Built-in presets
```python
chart = BarChart(data=[1,2,3], labels=["A","B","C"], theme="light")     # default
chart = BarChart(data=[1,2,3], labels=["A","B","C"], theme="dark")
chart = BarChart(data=[1,2,3], labels=["A","B","C"], theme="high-contrast")
```

### Register custom theme
```python
from charted import Theme, register_theme

register_theme("corporate", Theme(
    background_color="#1a1a2e",
    text_color="#eaeaea",
    colors=["#0f3460", "#e94560", "#16213e"],
))
chart = BarChart(data=[1,2,3], labels=["A","B","C"], theme="corporate")
```

### Fluent style override
```python
chart = BarChart(data=[1,2,3], labels=["A","B","C"]).style(
    background_color="#000", text_color="#fff", font_size=14
)
```

### Named palettes
```python
from charted.themes.core import NAMED_PALETTES, resolve_palette
# Available: default, viridis, ocean, categorical, rainbow, monochrome,
#            pastel, sunset, forest, inferno
colors = resolve_palette("viridis")
```

## Data Loading

```python
from charted import load_csv, load_json, load_data

# Generic (auto-detects .csv/.json/.tsv)
x, y, labels = load_data("sales.csv", x_col="Quarter", y_col="Revenue")

# Specific
x, y, labels = load_csv("sales.csv", x_col="Quarter", y_col="Revenue")
x, y, labels = load_json("data.json")
```

### From pandas DataFrame
```python
from charted import from_dataframe
chart = from_dataframe(df, chart_type="BarChart", title="Sales")
```

### From dict
```python
from charted import from_dict
chart = from_dict({
    "chart_type": "BarChart",
    "data": [10, 20, 30],
    "title": "Sales",
})
```

## Config Serialization

```python
# Save chart config for later replay
config = chart.to_config()  # -> dict with chart_type, data, labels, theme, etc.

# Recreate chart from config
from charted.charts.chart import Chart
new_chart = Chart.from_config(config)

# Override specific params on recreation
new_chart = Chart.from_config(config, title="Updated Title", width=800)
```

## describe()

Returns structured metadata for agent reasoning about a chart:

```python
chart = BarChart(data=[120, -50, 210], labels=["Q1", "Q2", "Q3"], title="P&L")
info = chart.describe()
# {
#   "chart_type": "BarChart",
#   "title": "P&L",
#   "dimensions": {"width": 500, "height": 500},
#   "series": [{"name": None, "count": 3, "min": -50.0, "max": 210.0, "mean": 93.33, "sum": 280.0}],
#   "labels": ["Q1", "Q2", "Q3"],
#   "label_count": 3,
#   "series_count": 1,
#   "theme": "light",
#   "has_negative_values": True,
#   "stacked": False,
# }
```

## MCP Server

The `mcp_server/` directory exists but is not yet implemented. When available, install with:
```sh
pip install 'charted[mcp]'
```

## DuckDB Integration

Located in `duckdb_ext/` (separate package, not part of core charted wheel).

```python
import duckdb
from duckdb_ext.extension import charted_query, load

con = load()  # returns a duckdb connection with UDFs registered

# Python helper — runs query, generates chart
charted_query(
    con,
    "SELECT quarter, revenue FROM sales",
    chart_type="bar",
    title="Sales",
    output="/tmp/chart.svg",
)
```

Chart type short names: `bar`, `column`, `line`, `scatter`, `pie`, `radar`, `area`, `box`, `histogram`, `heatmap`.

## CLI

```sh
# Create a chart from data file
python -m charted create bar output.svg --data sales.csv
python -m charted create column chart.svg -d data.json

# Batch: convert all files in a directory
python -m charted batch input_dir/ output_dir/
python -m charted batch input_dir/ output_dir/ --chart-type line

# Help
python -m charted --help
```

Supported chart types in CLI: `bar`, `column`, `line`, `pie`, `radar`, `scatter`.

## Development

```sh
# Install with dev deps
uv pip install -e '.[dev]'

# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/charts/test_visual.py::test_column_chart_basic -v

# Lint
ruff check .
ruff format .

# Auto-fix lint
ruff check --fix .

# Pre-commit hooks
pre-commit run --all-files

# Update visual baselines (ONLY when intentional rendering changes are approved)
python scripts/update_baselines.py
python scripts/update_baselines.py column_basic  # specific chart
```

### TDD approach

1. Write/modify tests first
2. Run tests to confirm failure
3. Implement the change
4. Confirm tests pass
5. Run `ruff check .` before committing

## Baseline Protection

**BASELINES ARE SACRED AND NON-NEGOTIABLE.**

The `tests/baselines/` directory contains SVG + PNG files that define correct rendering output. They are protected by SHA256 manifests (`MANIFEST.sha256`, `PNG_MANIFEST.sha256`).

**Rules:**
- NEVER update baselines to make broken code pass tests
- NEVER assume a baseline change is "fine" or "minor"
- ALWAYS treat baseline failures as bugs in your code
- ALWAYS fix the code to match the baseline, not the other way around

**When baselines MAY be updated (ALL conditions required):**
1. User explicitly requests a rendering change
2. Adding NEW chart types (no existing baseline)
3. Fixing a provably wrong baseline (document extensively)
4. Explicit approval BEFORE making changes

**How protection works:**
- `conftest.py` loads manifests at session start
- Computes SHA256 of each baseline file
- If hashes don't match manifests, pytest exits immediately
- On PNG failure, diff images are written to `tests/diffs/`

## Pitfalls

| Mistake | Fix |
|---------|-----|
| `chart.save("out.png")` fails | Install cairosvg: `pip install cairosvg` |
| ScatterChart with `data=[...]` | Use `x_data=` and `y_data=` params instead |
| Multi-series scatter with flat lists | Wrap in lists: `x_data=[[1,2],[3,4]], y_data=[[5,6],[7,8]]` |
| LineChart with flat `data=[1,2,3]` | Wrap: `data=[[1,2,3]]` (expects list-of-lists) |
| BoxPlot with summary stats | Pass raw distributions, not quartiles |
| Histogram with labels | Histogram auto-bins; don't pass labels |
| Updated baselines to fix test | NEVER do this. Fix the code. |
| Importing pandas/numpy in core | Zero-dep principle: never in `charted/` package |
| Missing series_names in legend | Pass `series_names=["A", "B"]` for multi-series |

## Zero-dep Principle

The `charted` package itself has **zero runtime dependencies**. Everything in `charted/` must be pure Python stdlib only.

Optional extras pull their own deps:
- PNG export: `cairosvg` (via `pip install charted[png]` or just `pip install cairosvg`)
- Dev/test: `pytest`, `pillow`, `numpy`, `cairosvg`, `ruff`, `pre-commit`
- DuckDB extension: `duckdb` (separate package in `duckdb_ext/`)
- MCP server: not yet implemented

Never add runtime deps to `[project.dependencies]` in pyproject.toml.
