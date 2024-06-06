# Charted

Introducing Charted: A Python Library for Crafting SVG Graphs. Charted is a humble endeavour to simplify graph creation in Python. Still a work in progress, it aims to provide a straightforward solution for generating visually appealing graphs without the need for external dependencies.

The initial types of charts that are planned to be created are:

- Column
- Bar
- Donut
- Pie
- Scatter

## Available Charts

### Column

> Work In Progress

```py
from charted.charts.column import Column

width = 500
height = 500
padding = 0.1
data = [
    [-240, 53, 91, 291, 98, -476, 235, 313, -150, 139],
    [235, 98, 189, 166, -17, 214, 163, 537, 455, 32],
    [25, 198, 143, 236, -127, 434, -223, 207, 325, 239],
    [55, -41, 43, -30, -183, -215, -329, -280, 286, 508],
]
graph = Column(data=data, width=width, height=height, padding=padding)
```

![](/docs/examples/column.svg)
