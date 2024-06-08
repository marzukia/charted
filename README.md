# Charted

[![codecov](https://codecov.io/github/marzukia/charted/graph/badge.svg?token=X5HJF0R2FJ)](https://codecov.io/github/marzukia/charted) [![charted-ci](https://github.com/marzukia/charted/actions/workflows/ci.yml/badge.svg)](https://github.com/marzukia/charted/actions/workflows/ci.yml) [![readthedocs](https://readthedocs.org/projects/charted-py/badge/?version=latest)](https://charted-py.readthedocs.io/en/latest/?badge=latest)

Introducing Charted: A Python Library for Crafting SVG Graphs. Charted is a humble endeavour to simplify graph creation in Python. Still a work in progress, it aims to provide a straightforward solution for generating visually appealing graphs without the need for external dependencies.

The initial types of charts that are planned to be created are:

- Column
- Bar
- Donut
- Pie
- Scatter

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

## Available Charts

### Column

```py
from charted import Column

graph = Column(
    title="Example Column Chart",
    data=[
        [-240, 53, 91, 291, 98, -476, 235, 313, -150, 139, 134, 170],
        [235, 98, 189, 166, -17, 214, 163, 537, 455, 32, 251, 50],
        [25, 198, 143, 236, -127, 434, -223, 207, 325, 239, 260, 30],
        [55, -41, 43, -30, -183, -215, -329, -280, 286, 508, 150, -44],
    ],
    width=800,
    height=500,
    padding=0.15,
    labels=[
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ],
)
```

![](/docs/examples/column.svg)

### Line

```py
from charted import Line

graph = Column(
    title="Example Line Chart",
    data=[
        [-240, 53, 91, 291, 98, -476, 235, 313, -150, 139, 134, 170],
        [235, 98, 189, 166, -17, 214, 163, 537, 455, 32, 251, 50],
    ],
    width=800,
    height=500,
    padding=0.15,
    labels=[
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ],
)
```

![](/docs/examples/line.svg)
