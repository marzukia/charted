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
labels = [
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
]
graph = Column(
    data=data,
    width=width,
    height=height,
    padding=padding,
    labels=[i for i in labels],
)

with open("docs/examples/column.svg", "w") as test:
    test.write(repr(graph))
