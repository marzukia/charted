from charted.charts.column import Column


width = 500
height = 500
padding = 0.1
data = [
    [24.0, 53.5, 91.7, 291.0, 98.4, -476.0, 235.9, 313.2, 713.6, 139.6],
    [235.1, 98.5, 189.3, 166.4, -17.9, 214.6, 163.8, 537.6, 455.5, 239.7],
    [55.0, -41.4, 43.1, -30.3, -183.1, -215.9, -329.0, -280.4, 286.2, 508.6],
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
