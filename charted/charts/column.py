from typing import List, Optional, Union
from charted.charts.axes import XAxis
from charted.charts.chart import Chart
from charted.charts.plot import Plot
from charted.html.element import G, Rect
from charted.utils.column import (
    calculate_rect_dimensions,
    calculate_vector_offsets,
    normalise_vectors,
)
from charted.utils.plot import calculate_plot_corners
from charted.utils.transform import rotate, translate
from charted.utils.types import Labels, Vector, Vector2D


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
        for x, y, h in zip(self.rect_coordinates, self.offsets, self.data):
            arr.append(Rect(x=x, y=y, height=h, width=self.column_width))
        return arr


class Column(Chart):
    # TODO: Color generation/theming.
    colors = ["red", "green", "blue"]

    def __init__(
        self,
        data: Union[Vector | Vector2D],
        labels: Optional[Labels] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.labels = labels
        self.data = self._validate_data(data)
        self.add_children(self.plot, self.series, self.x_axis)

    def _validate_data(self, data: Union[Vector, Vector2D]) -> Union[Vector, Vector2D]:
        if len(data) == 0:
            raise Exception("No data provided.")

        max_length = max([len(i) for i in data])
        if not all([len(i) == max_length for i in data]):
            raise Exception("Not all vectors were same length")

        return data

    @property
    def _dimensions(self):
        return calculate_rect_dimensions(self.plot_width, self.no_columns)

    @property
    def column_width(self):
        return self._dimensions[0]

    @property
    def column_gap(self):
        return self._dimensions[1]

    @property
    def rect_coordinates(self):
        return self._dimensions[2]

    @property
    def no_columns(self) -> int:
        return len(self.data[0])

    @property
    def offsets(self) -> Vector:
        return calculate_vector_offsets(self.normalised_data)

    @property
    def plot_width(self) -> float:
        return self.width * (1 - (self.padding * 2))

    @property
    def plot_height(self) -> float:
        return self.height * (1 - (self.padding * 2))

    @property
    def x_coordinates(self) -> Vector:
        return [i + self.column_width / 2 for i in self.rect_coordinates]

    @property
    def normalised_data(self) -> Vector2D:
        return normalise_vectors(
            self.plot_height,
            self.data,
        )

    @property
    def series(self) -> List[ColumnSeries]:
        (x1, _, y1, _) = [i * -1 for i in self.plot.bounds]
        g = G(transform=translate(x=x1, y=y1))
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
                    transform=rotate(180, self.width / 2, self.height / 2),
                )
            )
        return g

    @property
    def plot(self) -> Plot:
        return Plot(
            bounds=calculate_plot_corners(self.width, self.height, self.padding),
            width=self.plot_width,
            height=self.plot_height,
            padding=self.padding,
            # TODO: Remove this hardcoded no_y
            no_y=5,
            x_coordinates=self.x_coordinates,
        )

    @property
    def x_axis(self) -> XAxis:
        y = self.height * (1 - self.padding)
        return XAxis(
            labels=self.labels,
            width=self.width,
            padding=self.padding,
            no_columns=self.no_columns,
            column_width=self.column_width,
            coordinates=[(x, y) for x in self.x_coordinates],
        )
