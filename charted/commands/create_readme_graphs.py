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
            title="Global Temperature Anomaly by Decade",
            data=[
                [-0.16, 0.08, 0.07, 0.35, -0.05, -0.05, 0.01, -0.07, -0.13, 0.17],
                [-0.08, 0.09, 0.26, 0.02, 0.04, 0.16, 0.13, 0.28, 0.22, 0.46],
                [0.02, 0.06, 0.24, 0.19, 0.18, 0.23, 0.26, 0.41, 0.28, 0.52],
            ],
            labels=[
                "1880s",
                "1890s",
                "1900s",
                "1910s",
                "1920s",
                "1930s",
                "1940s",
                "1950s",
                "1960s",
                "1970s",
            ],
            width=700,
            height=450,
            theme={
                "padding": {
                    "v_padding": 0.1,
                    "h_padding": 0.1,
                }
            },
        )

    @property
    def line(self):
        return LineChart(
            title="Example Labelled Line Graph",
            data=[5 * (1.5**n) for n in range(0, 11)],
            labels=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"],
            theme={
                "colors": ["#204C9E"],
            },
        )

    @property
    def xy_line(self):
        return LineChart(
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


examples = Examples()
properties = [prop for prop in dir(examples) if not prop.startswith("__")]

for key in properties:
    with open(os.path.join(EXAMPLES_DIR, f"{key}.svg"), "w") as test:
        test.write(repr(getattr(examples, key)))
