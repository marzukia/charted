import os
import random
from charted.charts import ColumnChart, LineChart, ScatterChart
from charted.utils.defaults import EXAMPLES_DIR


y_data = [
    [50, 100, 150, 200, 250, 300, 150, 200, 350, 225],
    [25, 50, 75, 100, 125, 150, 75, 100, 175, 112.5],
]
x_data = [-5, 0, 1, 2, 3, 4, 5, 10, 12, 20]


class Examples:
    @property
    def scatter(self):
        return ScatterChart(
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

    @property
    def column(self):
        return ColumnChart(
            title="Example Column Graph",
            data=[
                [9.8, -29.8, 22.6, 45.0, 33.8, 35.4, 44.2],
                [8.9, 33.1, -27.1, 31.2, -15.4, 32.6, 19.8],
                [-32.0, 32.3, 45.7, -3.3, -33.3, -15.7, -38.6],
            ],
            labels=["January", "February", "March", "April", "May", "June", "July"],
            width=600,
            height=400,
            v_padding=0.1,
            h_padding=0.1,
        )

    @property
    def line(self):
        return LineChart(
            title="Example Labelled Line Graph",
            data=[5 * (1.5**n) for n in range(0, 11)],
            labels=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"],
            colors=["#204C9E"],
        )

    @property
    def xy_line(self):
        return LineChart(
            title="Example XY Line Graph",
            data=[
                [5 * (1.5**n) for n in range(0, 11)],
                [-5 * (1.5**n) for n in range(0, 11)],
            ],
            x_data=[-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4],
        )


examples = Examples()
properties = [prop for prop in dir(examples) if not prop.startswith("__")]

for key in properties:
    with open(os.path.join(EXAMPLES_DIR, f"{key}.svg"), "w") as test:
        test.write(repr(getattr(examples, key)))
