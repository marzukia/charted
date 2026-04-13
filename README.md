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
uv run python charted/fonts/creator.py Helvetica
```

## Links

- [Charted - Documentation](https://charted-py.readthedocs.io/en/latest/genindex.html)

## Examples

### Column

```py
from charted import column_chart

graph = column_chart(
    data=[9.8, -29.8, 22.6, 45.0, 33.8, 35.4, 44.2],
    labels=["January", "February", "March", "April", "May", "June", "July"],
    width=600,
    height=400,
)
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/column.svg)

### Labelled Line Chart

```py
from charted import line_chart

graph = line_chart(
    data=[5 * (1.5**n) for n in range(0, 11)],
    labels=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"],
    theme={
        "colors": ["#204C9E"],
    },
)
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/line.svg)

### Dual Axis Line Chart

```py
from charted import line_chart

graph = line_chart(
    data=[
        [5 * (1.5**n) for n in range(0, 11)],
        [-5 * (1.5**n) for n in range(0, 11)],
    ],
    x_data=[-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4],
    width=600,
    height=400,
)
```

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/xy_line.svg)

### Scatter

```py
import random
from charted import scatter_chart

graph = scatter_chart(
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

![](https://raw.githubusercontent.com/marzukia/charted/main/docs/examples/scatter.svg)
