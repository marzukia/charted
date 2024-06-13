import os
import random
from charted.charts import ColumnChart, LineChart, ScatterChart
from charted.utils.defaults import EXAMPLES_DIR


y_data = [
    [50, 100, 150, 200, 250, 300],
    [25, 50, 75, 100, 125, 150],
]
x_data = [-5, 0, 1, 2, 3, 4]
labels = ["foo", "bar", "foobar", "dog", "cat", "mouse"]


x_scatter = [
    [random.random() * i for i in range(-25, 25, 1)],
    [random.random() * i for i in range(-25, 25, 1)],
]

y_scatter = [
    [random.random() * i for i in range(-25, 25, 1)],
    [random.random() * i for i in range(-25, 25, 1)],
]


graphs = {
    "scatter": ScatterChart(
        title="Example Scatter Graph",
        y_data=y_scatter,
        x_data=x_scatter,
    ),
    "column": ColumnChart(
        title="Example Column Graph",
        data=y_data,
        labels=labels,
    ),
    "line": LineChart(
        title="Example Labelled Line Graph",
        data=y_data,
        labels=labels,
    ),
    "xy_line": LineChart(
        title="Example XY Line Graph",
        data=[y_data[0], [-i for i in y_data[1]]],
        x_data=x_data,
    ),
}

for key, chart in graphs.items():
    with open(os.path.join(EXAMPLES_DIR, f"{key}.svg"), "w") as test:
        test.write(repr(chart))
