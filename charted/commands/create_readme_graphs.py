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
        # Multi-column chart showing sales by product category over quarters
        return ColumnChart(
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


if __name__ == "__main__":
    examples = Examples()
    properties = [prop for prop in dir(examples) if not prop.startswith("__")]

    for key in properties:
        with open(os.path.join(EXAMPLES_DIR, f"{key}.svg"), "w") as test:
            test.write(repr(getattr(examples, key)))
