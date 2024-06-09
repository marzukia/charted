import os
from charted import Column
from charted.charts.line import Line
from charted.utils.helpers import BASE_DIR

config = {
    "data": [
        [-240, 53, 91, 291, 98, -476, 235, 313, -150, 139, 134, 170],
        [235, 98, 189, 166, -17, 214, 163, 537, 455, 32, 251, 50],
        [25, 198, 143, 236, -127, 434, -223, 207, 325, 239, 260, 30],
        [55, -41, 43, -30, -183, -215, -329, -280, 286, 508, 150, -44],
    ],
    "width": 800,
    "height": 500,
    "padding": 0.15,
    "labels": [
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
}

if __name__ == "__main__":
    column = Column(title="Example Column Chart", **config)

    dual_line = Line(
        title="Example Line Chart",
        width=800,
        height=500,
        padding=0.15,
        y_data=[
            [50, 100, -200, 50, 100, 200, 50, 200, 50, 25, 50, 250],
            [25, 50, -100, 25, 50, 100, 25, 100, 25, 12.5, 25, 125],
        ],
        x_data=[-4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7],
    )

    labeled_line = Line(title="Dual Axis Line Chart", **config)

    with open(os.path.join(BASE_DIR, "docs", "examples", "column.svg"), "w") as test:
        test.write(repr(column))

    with open(os.path.join(BASE_DIR, "docs", "examples", "line.svg"), "w") as test:
        test.write(repr(dual_line))

    with open(
        os.path.join(BASE_DIR, "docs", "examples", "labeled-line.svg"), "w"
    ) as test:
        test.write(repr(labeled_line))
