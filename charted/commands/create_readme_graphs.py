import os
from charted.charts.column import Column
from charted.utils.helpers import BASE_DIR

if __name__ == "__main__":
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
        padding=0.1,
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

    with open(os.path.join(BASE_DIR, "docs", "examples", "column.svg"), "w") as test:
        test.write(repr(graph))
