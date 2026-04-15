![charted-logo](https://github.com/marzukia/charted/blob/main/docs/_static/charted-logo.png?raw=true)

[![codecov](https://codecov.io/github/marzukia/charted/graph/badge.svg?token=X5HJF0R2FJ)](https://codecov.io/github/marzukia/charted) [![charted-ci](https://github.com/marzukia/charted/actions/workflows/ci.yml/badge.svg)](https://github.com/marzukia/charted/actions/workflows/ci.yml) [![readthedocs](https://readthedocs.org/projects/charted-py/badge/?version=latest)](https://charted-py.readthedocs.io/en/latest/?badge=latest)

Charted is a zero dependency SVG chart generator that aims to provide a simple interface for generating beautiful and customisable graphs. This project is inspired by chart libraries like `mermaid.js`.

The following chart types are available:

- Column
- Line
- Scatter
- Bar

The following chart types are planned to be implemented.

- Donut
- Pie

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

### Column

from charted.charts import ColumnChart

graph = ColumnChart(
    title="Product Sales by Quarter ($M)",
    data=[
        [45, 52, 48, 61],  # Electronics
        [32, 38, 45, 52],  # Clothing
        [28, 35, 42, 48],  # Home & Garden
        [22, 35, 42, 42],  # Sports
        [18, 25, 32, 38],  # Books
    ],
    labels=["Q1", "Q2", "Q3", "Q4"],
    width=700,
    height=500,
    theme={
        "padding": {
            "v_padding": 0.12,
            "h_padding": 0.12,
        }
    },
)

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/column.svg)

### Labelled Line Chart

```py
from charted.charts import LineChart

graph = LineChart(
    title="Example Labelled Line Graph",
    data=[5 * (1.5**n) for n in range(0, 11)],
    labels=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"],
    theme={
        "colors": ["#204C9E"],
    },
)
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/line.svg)

### Dual Axis Line Chart

from charted.charts import LineChart

graph = LineChart(
    title="Monthly Temperature vs CO2 Concentration",
    data=[
        [32, 35, 42, 52, 62, 72, 78, 76, 68, 55, 45, 38],
        [315, 318, 322, 328, 335, 342, 348, 352, 348, 342, 335, 328],
    ],
    x_data=[-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5],
    labels=[
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ],
)

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/xy_line.svg)

### Scatter

```py
from charted.charts import ScatterChart

graph = ScatterChart(
    title="Example Scatter Graph",
    y_data=[
        [random.random() * i for i in range(-25, 25, 1)],
        [random.random() * i for i in range(-25, 25, 1)],
    ],
    x_data=[
        [random.random() * i for i in range(-25, 25, 1)],
        [random.random() * i for i in range(-25, 25, 1)],
    ],
)
```

### Bar

```py
from charted.charts import BarChart

graph = BarChart(
    title="Example Bar Chart",
    data=[1, 3, 2],
    labels=["A", "B", "C"],
    width=600,
    height=400,
)
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/bar.svg)
