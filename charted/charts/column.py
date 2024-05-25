from typing import List, Union
from charted.charts.chart import Chart
from charted.charts.plot import Plot
from charted.html.element import G, Rect
from charted.utils import (
    Vector,
    Vector2D,
    calculate_rect_dimensions,
    calculate_vector_offsets,
    normalise_vectors,
    svg_rotate,
    svg_translate,
)


class ColumnSeries(G):
    def __init__(
        self,
        data: Vector,
        color: str,
        offsets: Vector,
        rect_coordinates: Vector,
        column_width: float,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.data = data
        self.color = color
        self.offsets = offsets
        self.rect_coordinates = rect_coordinates
        self.column_width = column_width
        self.kwargs["fill"] = self.color
        self.add_children(*self.series)

    @property
    def series(self) -> List[Rect]:
        arr = []
        for x, y, height in zip(self.rect_coordinates, self.offsets, self.data):
            rect = Rect(x=x, y=y, height=height, width=self.column_width)
            arr.append(rect)
        return arr


class Column(Chart):
    colors = ["red", "green", "blue"]

    def __init__(self, data: Union[Vector | Vector2D], **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.no_columns = len(data[0])
        (self.column_width, self.column_gap, self.rect_coordinates) = (
            calculate_rect_dimensions(
                width=self.width * (1 - (self.padding * 2)),
                no_columns=self.no_columns,
                gap=0.5,
            )
        )
        self.x_coordinates = [i + self.column_width / 2 for i in self.rect_coordinates]
        self.normalised_data = normalise_vectors(
            length=self.height * (1 - (self.padding * 2)),
            vectors=data,
        )
        self.offsets = calculate_vector_offsets(self.normalised_data)
        self.add_children(self.plot, self.series)

    @property
    def series(self) -> List[ColumnSeries]:
        (x1, _, y1, _) = [i * -1 for i in self.plot.bounds]
        g = G(transform=svg_translate(x=x1, y=y1))
        for offsets, data, color in zip(
            self.offsets,
            self.normalised_data,
            self.colors,
        ):
            g.add_child(
                ColumnSeries(
                    data=data,
                    offsets=offsets,
                    rect_coordinates=self.rect_coordinates,
                    color=color,
                    column_width=self.column_width,
                    transform=svg_rotate(self.width, self.height),
                )
            )
        return g

    @property
    def plot(self) -> Plot:
        return Plot(
            width=self.width,
            height=self.height,
            padding=self.padding,
            no_y=5,
            x_coordinates=self.x_coordinates,
        )
