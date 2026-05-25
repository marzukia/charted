![charted-logo](https://github.com/marzukia/charted/blob/main/docs/_static/charted-logo.png?raw=true)

[![codecov](https://codecov.io/github/marzukia/charted/graph/badge.svg)](https://codecov.io/github/marzukia/charted) [![charted-ci](https://github.com/marzukia/charted/actions/workflows/ci.yml/badge.svg)](https://github.com/marzukia/charted/actions/workflows/ci.yml)

**Charted** is a zero-dependency SVG chart library for Python. Drop in a list of numbers, get back a clean SVG string — no numpy, no pandas, no heavy dependencies. 11 chart types, multi-series support, theming, and a CLI so you can generate charts without writing code.

> **Core principle:** charted itself has zero runtime dependencies. PNG export and MCP server support are opt-in extras that pull in their own dependencies — the base library stays pure Python.

```sh
pip install charted
```

```python
from charted import BarChart

chart = BarChart(
    title="Sales by Quarter",
    data=[120, 180, 210, 150],
    labels=["Q1", "Q2", "Q3", "Q4"],
)
chart.save("chart.svg")
chart.save("chart.png")  # PNG export (requires cairosvg)
```

---

## Why Charted?

- **Zero runtime dependencies** — pure Python, no numpy/pandas required
- **11 chart types** — Bar, Column, Line, Scatter, Pie, Radar, Area, Box Plot, Histogram, Heatmap, Gantt
- **Multi-series support** — stacked, side-by-side, grouped layouts
- **Negative values handled** — proper zero baseline calculations
- **SVG and PNG output** — SVG natively, PNG via optional `cairosvg` (`pip install charted[png]`)
- **Theme system** — 3 built-in presets + custom theme composition
- **Per-series styling** — granular control with SeriesStyle builders
- **Data loading** — CSV/JSON parsers built-in
- **Markdown export** — generate embed-ready markdown snippets
- **CLI included** — create charts without writing Python code
- **Jupyter ready** — charts render inline automatically
- **Base Chart class** — unified API for dynamic chart type selection

---

## Quick Tour

Every chart type shares the same simple interface — pass data, labels, dimensions, and a title:

```python
from charted.charts import BarChart, LineChart, PieChart

# Bar — single series with axis title
BarChart(
    title="Average App Rating by Category",
    data=[4.6, 4.2, 3.8, 4.5, 3.1, 4.0, 4.3],
    labels=["Games", "Social", "News", "Health", "Finance", "Music", "Photo"],
    x_label="Rating (out of 5)",
    width=600, height=400,
).save("bar.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/bar.svg)

```python
# Bar — multi-series temperature comparison
BarChart(
    title="Summer vs Winter Avg. Temperature (°C)",
    data=[[35, 28, 22, 14, 8], [18, 12, 5, -2, -12]],
    labels=["Dubai", "Sydney", "Tokyo", "London", "Moscow"],
    series_names=["Summer", "Winter"],
    x_label="Temperature (°C)",
    width=600, height=400,
).save("bar_multi.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/bar_multi.svg)

```python
# Bar — stacked marketing spend
BarChart(
    title="Marketing Spend by Channel ($K)",
    data=[[45, 60, 55, 70], [30, 25, 40, 35], [15, 20, 18, 22]],
    labels=["Q1", "Q2", "Q3", "Q4"],
    series_names=["Digital", "Print", "Events"],
    x_stacked=True, x_label="Spend ($K)",
    width=600, height=350,
).save("bar_stacked.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/bar_stacked.svg)

```python
# Bar — side-by-side trade balance
BarChart(
    title="Trade Balance: Exports vs Imports ($B)",
    data=[[320, 180, 95, 210], [-280, -195, -110, -165]],
    labels=["China", "Germany", "Australia", "Japan"],
    series_names=["Exports", "Imports"],
    x_label="Value ($B)",
    width=600, height=350,
).save("bar_sidebyside.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/bar_sidebyside.svg)

---

```python
# Column — multi-series revenue by product line
from charted.charts import ColumnChart

ColumnChart(
    title="Quarterly Revenue by Product Line ($M)",
    data=[[12, 18, 22, 28], [8, 10, 15, 19], [5, 7, 6, 11]],
    labels=["Q1", "Q2", "Q3", "Q4"],
    series_names=["SaaS", "Consulting", "Hardware"],
    y_label="Revenue ($M)",
    width=600, height=400,
).save("column.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/column.svg)

```python
# Column — stacked website traffic
ColumnChart(
    title="Website Traffic by Source (K visits)",
    data=[[120, 140, 165, 180, 210], [80, 75, 90, 95, 100], [40, 55, 60, 70, 85]],
    labels=["Jan", "Feb", "Mar", "Apr", "May"],
    series_names=["Organic", "Paid", "Referral"],
    y_label="Visits (K)",
    width=600, height=400,
).save("column_stacked.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/column_stacked.svg)

```python
# Column — side-by-side language popularity
ColumnChart(
    title="Developer Survey: Language Popularity (%)",
    data=[[67, 45, 38, 30, 22], [62, 48, 42, 35, 28]],
    labels=["Python", "JavaScript", "Go", "Rust", "TypeScript"],
    series_names=["2024", "2025"],
    y_stacked=False, y_label="Respondents (%)",
    width=600, height=400,
).save("column_sidebyside.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/column_sidebyside.svg)

---

```python
# Line — multi-series stock price comparison
from charted.charts import LineChart

LineChart(
    title="Stock Price (Normalized to 100)",
    data=[
        [100, 105, 98, 112, 120, 115, 125, 130, 128, 140, 138, 150],
        [100, 97, 102, 108, 104, 110, 115, 112, 118, 122, 125, 130],
        [100, 103, 106, 104, 108, 112, 110, 115, 120, 118, 122, 128],
    ],
    labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    series_names=["ACME Corp", "Globex Inc", "Initech"],
    width=600, height=400,
).save("line.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/line.svg)

```python
# Line — XY mode with temperature anomaly data
import math
years = list(range(1990, 2010))
anomalies = [-15, -5, 10, 20, 5, 25, 15, 30, 10, 20, 40, 25, 45, 30, 50, 35, 60, 55, 45, 70]
baseline = [round(5 + 2 * math.sin(i * 0.4) + i * 0.5, 1) for i in range(len(years))]

LineChart(
    title="Temperature Anomaly vs 5-Year Rolling Baseline (1990-2009)",
    data=[anomalies, baseline],
    x_data=years,
    labels=[str(y) for y in years],
    width=600, height=400,
).save("xy_line.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/xy_line.svg)

```python
# Line — single series with reference line and data label
LineChart(
    title="Monthly Revenue — Corner Coffee Co. ($K)",
    data=[[18, 22, 19, 25, 28, 32, 35, 38, 30, 27, 24, 42]],
    labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    series_names=["Revenue"], y_label="Revenue ($K)",
    h_lines=[28.3],
    data_labels=["", "", "", "", "", "", "", "", "", "", "", "$42K"],
    width=600, height=400,
).save("line_single.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/line_single.svg)

---

```python
# Scatter — quadrant analysis with reference lines and quadrant labels
import random
from charted.charts import ScatterChart

random.seed(42)
hp_x = [round(65 + random.gauss(0, 8), 1) for _ in range(12)]
hp_y = [round(70 + random.gauss(0, 10), 1) for _ in range(12)]
gp_x = [round(35 + random.gauss(0, 8), 1) for _ in range(12)]
gp_y = [round(65 + random.gauss(0, 10), 1) for _ in range(12)]
sc_x = [round(60 + random.gauss(0, 10), 1) for _ in range(12)]
sc_y = [round(35 + random.gauss(0, 8), 1) for _ in range(12)]

ScatterChart(
    title="Employee Performance Quadrant",
    x_data=[hp_x, gp_x, sc_x], y_data=[hp_y, gp_y, sc_y],
    series_names=["High Performers", "Growth Potential", "Steady Contributors"],
    x_label="Skills Score", y_label="Engagement Score",
    h_lines=[50.0], v_lines=[50.0],
    quadrant_labels=["Disengaged Experts", "Stars", "At Risk", "Rising Talent"],
    width=600, height=500,
).save("scatter.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/scatter.svg)

```python
# Scatter — single series with data labels
random.seed(7)
cities = ["Austin", "Denver", "Portland", "Nashville", "Raleigh",
          "Boise", "Tampa", "Phoenix", "Atlanta", "Seattle"]
sqft = [1200, 1450, 1600, 1800, 2000, 2200, 2500, 2800, 3100, 3500]
prices = [round(180 + (s - 1200) * 0.12 + random.gauss(0, 30), 0) for s in sqft]

ScatterChart(
    title="Home Price vs Size — Mid-Market Cities",
    x_data=sqft, y_data=prices,
    series_names=["Median Price"],
    data_labels=cities,
    x_label="Square Footage", y_label="Price ($K)",
    width=600, height=450,
).save("scatter_single.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/scatter_single.svg)

---

```python
# Pie — cloud market share
from charted.charts import PieChart

PieChart(
    title="Global Cloud Market Share (2025)",
    data=[33, 22, 10, 8, 27],
    labels=["AWS", "Azure", "GCP", "Alibaba", "Others"],
    width=550, height=450,
).save("pie.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/pie.svg)

```python
# Pie — doughnut time breakdown
PieChart(
    title="Time Spent Per Day (hours)",
    data=[8, 7, 2, 3, 2, 2],
    labels=["Sleep", "Work", "Exercise", "Commute", "Cooking", "Leisure"],
    inner_radius=0.5, width=550, height=450,
).save("pie_doughnut.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/pie_doughnut.svg)

---

```python
# Radar — framework evaluation
from charted.charts import RadarChart

RadarChart(
    title="Frontend Framework Evaluation",
    data=[85, 70, 90, 60, 75, 80],
    labels=["Performance", "Ecosystem", "DX", "Bundle Size", "TypeScript", "Community"],
    width=550, height=450,
).save("radar.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/radar.svg)

```python
# Radar — athlete comparison
RadarChart(
    title="Athlete Comparison: Sprint vs Endurance",
    data=[[92, 65, 55, 80, 70], [60, 90, 95, 65, 85]],
    labels=["Speed", "Stamina", "Recovery", "Power", "Agility"],
    series_names=["Sprinter", "Marathoner"],
    width=550, height=450,
).save("radar_multi.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/radar_multi.svg)

---

```python
# Area — daily step count
import random
from charted.charts import AreaChart

random.seed(99)
steps = [round(6000 + 4000 * math.sin(i * 0.45) + random.gauss(0, 800)) for i in range(30)]

AreaChart(
    title="Daily Step Count — April 2025",
    data=steps,
    labels=[str(d + 1) for d in range(30)],
    width=600, height=380,
).save("area.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/area.svg)

```python
# Area — energy production by source
AreaChart(
    title="Energy Production by Source (GWh)",
    data=[
        [120, 125, 130, 140, 155, 170, 180, 190],
        [80, 90, 95, 100, 110, 115, 125, 135],
        [60, 55, 50, 48, 45, 40, 38, 35],
    ],
    labels=["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
    series_names=["Solar", "Wind", "Coal"],
    width=600, height=400,
).save("area_multi.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/area_multi.svg)

---

```python
# Box Plot — server response times
import random
from charted.charts import BoxPlot

random.seed(42)
box_a = [round(random.gauss(50, 10), 1) for _ in range(50)] + [95, 5, 102]
box_b = [round(random.gauss(70, 15), 1) for _ in range(50)] + [120, 30, 130]
box_c = [round(random.gauss(30, 8), 1) for _ in range(50)] + [55, 8, 60]

BoxPlot(
    title="Response Time by Server Region (ms)",
    data=[box_a, box_b, box_c],
    labels=["US-East", "EU-West", "AP-South"],
    width=600, height=400,
).save("boxplot.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/boxplot.svg)

---

```python
# Histogram — exam score distribution
import random
from charted.charts import Histogram

random.seed(42)
scores = [random.gauss(50, 15) for _ in range(500)]

Histogram(
    title="Exam Score Distribution (500 Students)",
    data=scores,
    bins=10, width=600, height=400,
).save("histogram.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/histogram.svg)

---

```python
# Heatmap — monthly temperature matrix
from charted.charts import HeatmapChart

HeatmapChart(
    title="Average Temperature (°C) — Monthly by City",
    data=[
        [35, 36, 38, 40, 43, 45, 47, 46, 44, 41, 38, 36],
        [22, 24, 28, 32, 36, 40, 42, 41, 38, 33, 27, 23],
        [15, 18, 22, 27, 32, 37, 40, 39, 35, 29, 22, 17],
        [5, 8, 14, 20, 26, 32, 35, 34, 29, 22, 14, 7],
        [-2, 2, 10, 18, 25, 31, 34, 33, 27, 19, 10, 3],
    ],
    x_labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    y_labels=["Dubai", "Sydney", "Tokyo", "Berlin", "Moscow"],
    width=600, height=400,
    low_color="#21639e", high_color="#f97316",
    show_values=True, value_format=".0f",
).save("heatmap.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/heatmap.svg)

```python
# Gantt — product launch timeline
from charted.charts import GanttChart

GanttChart(
    title="Product Launch Timeline — Q1 2026",
    data=[(0, 2), (1, 4), (3, 6), (5, 8), (6, 9)],
    labels=["Research", "Design", "Development", "QA", "Launch"],
    width=600, height=380,
    dependencies=[(0, 1), (0, 2), (2, 3), (3, 4)],
    show_today_line=True,
    x_position=4.5,
).save("gantt.svg")
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/gantt.svg)

---

## Theming

Three built-in presets — light, dark, high-contrast — plus custom theme composition:

```python
from charted import BarChart

# Built-in themes
chart = BarChart(data=[120, 180, 210], labels=["Q1", "Q2", "Q3"], theme="light")
chart = BarChart(data=[120, 180, 210], labels=["Q1", "Q2", "Q3"], theme="dark")
chart = BarChart(data=[120, 180, 210], labels=["Q1", "Q2", "Q3"], theme="high-contrast")
```

| Theme | Preview |
|-------|---------|
| Light | ![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples_themes/light.svg) |
| Dark | ![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples_themes/dark.svg) |
| High Contrast | ![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples_themes/high-contrast.svg) |

See the [Theming docs](docs/THEMING.md) for custom palettes, font overrides, and per-series styling.

---

## CLI Usage

Generate charts without writing Python:

```sh
# From CSV
python -m charted create bar output.svg --data sales.csv

# From JSON
python -m charted create column chart.svg -d data.json

# Batch from directory
python -m charted batch input_data/ output_svg/
```

**CSV format:**
```csv
Quarter,Revenue,Expenses
Q1,120,80
Q2,180,95
Q3,210,110
```

**JSON format:**
```json
{
  "labels": ["Q1", "Q2", "Q3"],
  "data": [[120, 180, 210], [80, 95, 110]],
  "series_names": ["Revenue", "Expenses"]
}
```

Full CLI docs: `python -m charted --help`

---

## Data Loading

Load CSV/JSON without pandas:

```python
from charted import load_csv, load_json, BarChart

# From CSV
x, y, labels = load_csv("sales.csv", x_col="Quarter", y_col="Revenue")
chart = BarChart(data=y, labels=x, title=labels[0])
chart.save("sales.svg")

# From JSON
x, y, labels = load_json("data.json")
chart = ColumnChart(data=y, labels=x)
```

---

## Jupyter Notebook

Charts render inline automatically — no extra setup needed:

```python
from charted.charts import BarChart

chart = BarChart(
    title="Sales by Quarter",
    data=[120, 180, 210, 150],
    labels=["Q1", "Q2", "Q3", "Q4"],
)
# Renders inline in the notebook cell
```

---

## Markdown Export

```python
from charted import BarChart

chart = BarChart(data=[120, 180, 210], labels=["Q1", "Q2", "Q3"], title="Sales")

# With file path
chart.save("docs/sales.svg")
md = chart.to_markdown(path="docs/sales.svg")  # ![Sales](docs/sales.svg)

# As inline data URL
md = chart.to_markdown()  # Data URL embedded in markdown
```

---

## Base Chart Class

Dynamically select chart type at runtime:

```python
from charted import Chart

chart = Chart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    title="Sales",
    chart_type="bar",  # or column, line, scatter, pie, area, boxplot, histogram, heatmap, gantt
)
chart.save("chart.svg")

# Access all chart methods
svg = chart.to_svg()
md = chart.to_markdown()
```

---

## Installation

```sh
pip install charted
```

Optional extras (these add dependencies — the core library stays zero-dep):
```sh
pip install 'charted[png]'     # PNG export via cairosvg
pip install 'charted[mcp]'     # MCP server for AI agent integration
pip install 'charted[duckdb]'  # generate charts from SQL queries
pip install 'charted[dev]'     # dev tools including PNG visual testing
```

## PNG Export

Save charts directly as PNG by using the `.png` extension:

```python
chart = BarChart(data=[10, 20, 30], labels=["A", "B", "C"])
chart.save("chart.svg")          # SVG (no extra dependencies)
chart.save("chart.png")          # PNG (requires cairosvg)
chart.save("chart.png", scale=3) # PNG at 3x resolution
```

PNG export requires `cairosvg`. If it's not installed, `save()` raises a helpful `ImportError` with install instructions.

---

## MCP Server (AI Agent Integration)

Charted includes an MCP server so AI agents (Claude Code, Cursor, etc.) can generate charts without writing Python:

```sh
# Register with Claude Code
claude mcp add charted -- charted-mcp

# Or run standalone
charted-mcp
```

Exposes tools: `create_chart`, `list_chart_types`, `list_themes`, `chart_from_csv`. Requires `pip install charted[mcp]`.

---

## Links

- [Full Documentation](https://charted.mrzk.io)
- [Configuration Reference](docs/config.md)
- [Theming Guide](docs/THEMING.md)
- [Font Definitions](docs/fonts.md)

### Font System

Charted avoids tkinter by using pre-defined font metrics in `fonts/definitions/`. Generate new font definitions:

```sh
uv run python charted/commands/create_font_definition.py Helvetica
```
