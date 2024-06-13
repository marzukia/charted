![charted-logo](https://github.com/marzukia/charted/blob/main/docs/_static/charted-logo.png?raw=true)

[![codecov](https://codecov.io/github/marzukia/charted/graph/badge.svg?token=X5HJF0R2FJ)](https://codecov.io/github/marzukia/charted) [![charted-ci](https://github.com/marzukia/charted/actions/workflows/ci.yml/badge.svg)](https://github.com/marzukia/charted/actions/workflows/ci.yml) [![readthedocs](https://readthedocs.org/projects/charted-py/badge/?version=latest)](https://charted-py.readthedocs.io/en/latest/?badge=latest)

Charted is a zero dependency SVG chart generator that aims to provide a simple interface for generating beautiful and customisable graphs. This project is inspired by chart libraries like `mermaid.js`.

The following chart types are available:

- Column
- Line
- Scatter

The following chart types are planned to be implemented.

- Bar
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
poetry run python charted/fonts/creator.py Helvetica
```

## Links

- [Charted - Documentation](https://charted-py.readthedocs.io/en/latest/genindex.html)

## Examples

### Column

```py
from charted.charts import Column

graph = ColumnChart(
    title="Example Column Graph",
    data=[
        [50, 100, 150, 200, 250, 300],
        [25, 50, 75, 100, 125, 150],
    ],
    width=800,
    height=500,
    labels = ["foo", "bar", "foobar", "dog", "cat", "mouse"]
)
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/column.svg)

### Labelled Line Chart

```py
from charted.charts import LineChart

graph = LineChart(
    title="Example Labelled Line Graph",
    data=y_data,
    labels=labels,
)
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/line.svg)

### Dual Axis Line Chart

```py
from charted.charts import LineChart


graph = LineChart(
        title="Example XY Line Graph",
        data=[y_data[0], [-i for i in y_data[1]]],
        x_data=x_data,
)
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/xy_line.svg)

### Scatter

```py
from charted.charts import ScatterChart

x_scatter = [
    [random.random() * i for i in range(-25, 25, 1)],
    [random.random() * i for i in range(-25, 25, 1)],
]

y_scatter = [
    [random.random() * i for i in range(-25, 25, 1)],
    [random.random() * i for i in range(-25, 25, 1)],
]


graph = ScatterChart(
        title="Example Scatter Graph",
        y_data=y_scatter,
        x_data=x_scatter,
)
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/scatter.svg)
