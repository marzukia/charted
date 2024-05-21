from charted.html.element import G, Line, Rect, Svg
from charted.html.formatter import format_html
from charted.utils import (
    calculate_axis_coordinates,
    calculate_rect_dimensions,
    calculate_svg_rotate,
    calculate_svg_transform,
    calculate_vector_attributes,
    calculate_vector_offsets,
    calculate_viewbox,
)

width = 600
height = 400

padding = 0.1

data1 = [24.0, 53.5, 91.7, 291.0, 98.4, 476.0, 235.9, 313.2, 713.6, 139.6]
data2 = [235.1, 98.5, 189.3, 166.4, 17.9, 214.6, 163.8, 537.6, 455.5, 239.7]
data3 = [55.0, 41.4, 43.1, 30.3, 183.1, 215.9, 329.0, 280.4, 286.2, 508.6]
data = [data1, data2, data3]

colors = ["red", "green", "blue"]
offsets = calculate_vector_offsets(data)
min_value, max_value, no_columns = calculate_vector_attributes(data)
column_width, column_gap, rect_coordinates, x_coordinates = calculate_rect_dimensions(
    width, no_columns
)
y_coordinates = calculate_axis_coordinates(max_value, 5)


svg = Svg(
    viewBox=calculate_viewbox(width, height),
    width=width,
    height=height,
    id="svg",
)


plot = G(
    transform=calculate_svg_transform(width, height, max_value, padding),
    id="plot",
)


grids = G(
    transform=calculate_svg_rotate(width, height),
    stroke="#ccc",
    id="grid",
)
for x in x_coordinates:
    line = Line(x1=x, y1=0, x2=x, y2=max_value)
    grids.add_child(line)

for y in y_coordinates:
    line = Line(x1=0, y1=y, x2=width, y2=y)
    grids.add_child(line)

plot.add_child(grids)

for i, vector in enumerate(data):
    series = G(
        transform=calculate_svg_rotate(width, height),
        fill=colors[i],
        opacity="75%",
        id=f"series{i + 1}",
    )
    for j, x in enumerate(rect_coordinates):
        rect = Rect(x=x, y=offsets[i][j], height=vector[j], width=column_width)
        series.add_child(rect)
    plot.add_child(series)

svg.add_child(plot)

print(format_html(svg.html))
