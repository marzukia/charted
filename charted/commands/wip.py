from charted.charts import LineChart

# fmt: off
data = [7101, 7002, 6933, 6933, 6903, 6974, 6903, 6832, 6733, 6803, 6844, 6829, 6859, 6776, 6692, 6622, 6650, 6608, 6651, 6567, 6539, 6456, 6537, 6498, 6528, 6485, 6585, 6556, 6486, 6430, 6459, 6446, 6517, 6546, 6587, 6657, 6755, 6784, 6713, 6724, 6712, 6656, 6698, 6641, 6669, 6599, 6599, 6669, 6767, 6670, 6727, 6754, 6783, 6699, 6728, 6769, 6839, 6798, 6729]
# data2 = [i * 10 for i in data]
# fmt: on

# chart = LineChart(
#     title="Test",
#     data=[data],
#     zero_index=False,
#     theme={
#         "colors": ["#ff0000"],
#         "marker": {
#             "marker_size": 0,
#         },
#         "title": {
#             "font_color": "#ff0000",
#         },
#         "v_grid": None,
#         "h_grid": {
#             "stroke": "#dddddd",
#             "stroke_dasharray": "4 2",
#         },
#     },
# )

chart = LineChart(
    title="Example Labelled Line Graph",
    data=[5 * (1.5**n) for n in range(0, 11)],
    labels=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"],
    theme={
        "colors": ["#204C9E"],
    },
)

print(repr(chart))
