![charted-logo](https://github.com/marzukia/charted/blob/main/docs/_static/charted-logo.png?raw=true)

[![codecov](https://codecov.io/github/marzukia/charted/graph/badge.svg?token=X5HJF0R2FJ)](https://codecov.io/github/marzukia/charted) [![charted-ci](https://github.com/marzukia/charted/actions/workflows/ci.yml/badge.svg)](https://github.com/marzukia/charted/actions/workflows/ci.yml) [![readthedocs](https://readthedocs.org/projects/charted-py/badge/?version=latest)](https://charted-py.readthedocs.io/en/latest/?badge=latest)

Charted is a zero-dependency SVG chart generator for Python. It produces clean, publication-quality charts entirely in Python — no JavaScript, no browser, no external services. Drop the SVG into a web page, a PDF report, or a README and it just works.

Key features:

- **No dependencies** — pure Python, ships as a single package
- **Negative values** — all chart types handle positive/negative data with a proper zero baseline
- **Multi-series** — side-by-side bars, grouped columns, overlapping lines with distinct colours
- **Themeable** — override colours, padding, and grid styles via a simple dict
- **Embeddable** — output is a single SVG string; write it to a file or inline it in HTML

## Chart Types

### Available

- Column
- Line
- Scatter
- Bar
- Pie

### Planned

- Donut

## Installation

```sh
pip install charted
```

### `tkinter`

I've tried to avoid using `tkinter` in this library as it can be fiddly to install depending on your OS. However, it's still partially used if you're looking to expand Charted. Instead of using `tkinter` to calculate text dimensions on the fly, font definitions are created in `fonts/definitions/`.

New font definitions can be created by using:

```sh
uv run python charted/commands/create_font_definition.py Helvetica
```

## Links

- [Charted - Documentation](https://charted-py.readthedocs.io/en/latest/genindex.html)

## Examples

### Column — multi-series with negatives

```py
from charted.charts import ColumnChart

graph = ColumnChart(
    title="Year-over-Year Growth Rate (%) by Segment",
    data=[
        [12, -8, 22, 18, -5, 30],    # Revenue
        [-3, -15, 5, -2, -20, 8],    # Costs
        [9, -23, 17, 16, -25, 38],   # Net
    ],
    labels=["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"],
    width=700,
    height=500,
    theme={
        "padding": {
            "v_padding": 0.12,
            "h_padding": 0.10,
        }
    },
)
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/column.svg)

### Line — multi-series signal data

```py
import math
from charted.charts import LineChart

n = 20
graph = LineChart(
    title="Signal Analysis: Raw vs Filtered vs Baseline",
    data=[
        [math.sin(i * 0.5) * 30 + (i % 7 - 3) * 5 for i in range(n)],  # Raw
        [math.sin(i * 0.5) * 25 for i in range(n)],                      # Filtered
        [math.sin(i * 0.5) * 10 - 5 for i in range(n)],                  # Baseline
    ],
    labels=[str(i) for i in range(n)],
    width=700,
    height=400,
)
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/line.svg)

### Line — XY mode with temperature anomaly data

```py
from charted.charts import LineChart

years = list(range(1990, 2010))
anomalies = [-15, -5, 10, 20, 5, 25, 15, 30, 10, 20, 40, 25, 45, 30, 50, 35, 60, 55, 45, 70]

graph = LineChart(
    title="Temperature Anomaly vs Baseline (1990-2009)",
    data=[anomalies, [0] * len(years)],
    x_data=years,
    labels=[str(y) for y in years],
    width=700,
    height=400,
)
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/xy_line.svg)

### Bar — single series with negatives

```py
from charted.charts import BarChart

graph = BarChart(
    title="Profit/Loss by Region ($M)",
    data=[-12, 34, -8, 52, -5, 28, 41, -19, 15, 60],
    labels=["North", "South", "East", "West", "Central", "Pacific", "Atlantic", "Mountain", "Plains", "Metro"],
    width=700,
    height=500,
)
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/bar.svg)

### Bar — multi-series side-by-side

```py
from charted.charts import BarChart

graph = BarChart(
    title="Revenue vs Expenses by Quarter ($K)",
    data=[
        [120, -45, 180, -30, 210, -60],   # Revenue
        [-80, -20, -95, -15, -110, -25],  # Expenses
    ],
    labels=["Q1 Prod", "Q1 Ops", "Q2 Prod", "Q2 Ops", "Q3 Prod", "Q3 Ops"],
    width=700,
    height=500,
)
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/bar_multi.svg)

### Pie

```py
from charted.charts import PieChart

graph = PieChart(
    title="Sales Distribution",
    data=[45, 30, 15, 10],
    labels=["Electronics", "Clothing", "Food", "Other"],
    width=500,
    height=400,
)
```
