from collections import defaultdict
from typing import Optional, Tuple, Union
from charted.charts.chart import Chart
from charted.charts.plot import Plot
from charted.html.element import G, Path
from charted.utils.column import get_path
from charted.utils.plot import calculate_plot_corners
from charted.utils.transform import rotate, translate
from charted.utils.types import Bounds, Labels, Vector, Vector2D


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
        validated_data = self._validate_data(data)
        self.data = validated_data
        self.bounds = validated_data
        self.add_children(self.plot, self.series, self.zero_line)  # self.x_axis

    def _validate_data(self, data: Union[Vector, Vector2D]) -> Union[Vector, Vector2D]:
        if len(data) == 0:
            raise Exception("No data provided.")

        max_length = max([len(i) for i in data])
        if not all([len(i) == max_length for i in data]):
            raise Exception("Not all vectors were same length")

        return data

    @property
    def plot_width(self) -> float:
        return self.width * (1 - (self.padding * 2))

    @property
    def plot_height(self) -> float:
        return self.height * (1 - (self.padding * 2))

    @classmethod
    def get_bounds(cls, data: Vector2D):
        agg = defaultdict(list)
        n = len(data[0])
        for i in range(n):
            for arr in data:
                agg[i].append(arr[i])

        min_x = 0
        min_y = min([sum([x for x in i if x <= 0]) for i in agg.values()])
        max_x = n - 1
        max_y = max([sum([x for x in i if x >= 0]) for i in agg.values()])

        return (min_x, min_y, max_x, max_y)

    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        return Bounds(*self._bounds)

    @bounds.setter
    def bounds(self, data: Vector2D) -> None:
        self._bounds = self.get_bounds(data)
        self.min_x, self.min_y, self.max_x, self.max_y = self._bounds

    @property
    def no_columns(self) -> int:
        return len(self.data[0])

    @classmethod
    def _reproject(
        cls,
        value: float,
        max_value: float,
        min_value: float,
        length: float,
    ) -> float:
        value_range = max_value - min_value
        normalised_value = value / value_range
        return normalised_value * length

    def _reproject_x(self, value: float) -> float:
        return self._reproject(value, self.max_x, self.min_x, self.plot_width)

    def _reproject_y(self, value: float) -> float:
        return self._reproject(value, self.max_y, self.min_y, self.plot_height)

    def reproject(self, coordinate: Tuple[float, float]) -> Tuple[float, float]:
        return [self._reproject_x(coordinate[0]), self._reproject_y(coordinate[1])]

    @property
    def column_width(self, spacing: float = 0.5) -> float:
        width = self.plot_width / (self.no_columns + (self.no_columns + 1) * spacing)
        return width

    @property
    def x_ticks(self) -> Vector:
        return [
            ((self.plot_width / self.no_columns) * i) + (self.column_width / 4)
            for i in range(0, self.no_columns)
        ]

    @property
    def y_values(self) -> Vector2D:
        data = []
        for arr in self.data:
            row = []
            for y in arr:
                v = self._reproject_y(abs(y))
                if y < 0:
                    v = -v
                row.append(v)
            data.append(row)
        return data

    @property
    def y_offset(self) -> Vector2D:
        offsets = []
        negative_offsets = [0] * self.no_columns
        positive_offsets = [0] * self.no_columns

        for row in self.data:
            row_offsets = []
            for i, y in enumerate(row):
                current_offset = 0
                if y >= 0:
                    current_offset = positive_offsets[i]
                    positive_offsets[i] += y
                elif y < 0:
                    current_offset = negative_offsets[i]
                    negative_offsets[i] -= abs(y)
                row_offsets.append(current_offset)
            offsets.append(row_offsets)

        return [[self._reproject_y(y) for y in arr] for arr in offsets]

    @property
    def series(self) -> G:
        dx = self.padding * self.width
        dy = self.padding * self.height

        if self.min_y < 0:
            dy += self._reproject_y(abs(self.min_y))

        g = G(
            transform=[
                rotate(180, self.width / 2, self.height / 2),
                translate(x=dx, y=dy),
            ]
        )
        for y_values, y_offsets, color in zip(
            self.y_values, self.y_offset, self.colors
        ):
            paths = []
            for x, y, offset in zip(self.x_ticks, y_values, y_offsets):
                path = get_path(x, offset, self.column_width, y)
                paths.append(path)
            g.add_child(Path(d=paths, fill=color))
        return g

    @property
    def zero_line(self) -> Path:
        yz = self._reproject_y(abs(0 - self.bounds.y2))
        dy = self.height * self.padding + yz
        dx = self.width * self.padding
        return Path(
            d=[f"M{dx} {dy}", f"h{self.plot_width}z"],
            stroke="black",
        )

    @property
    def plot(self) -> Plot:
        return Plot(
            bounds=calculate_plot_corners(
                self.width,
                self.height,
                self.padding,
            ),
            width=self.plot_width,
            height=self.plot_height,
            padding=self.padding,
            # TODO: Remove this hardcoded no_y
            no_y=5,
            y0=self._reproject_y(abs(0 - self.bounds.y2)),
            x0=self._reproject_x(abs(0 - self.bounds.x1)),
            x_coordinates=[i - (self.column_width / 4) for i in self.x_ticks],
        )


#    @property
#    def x_axis(self) -> XAxis:
#        y = self.height * (1 - self.padding)
#        return XAxis(
#            labels=self.labels,
#            width=self.width,
#            padding=self.padding,
#            no_columns=self.no_columns,
#            column_width=self.column_width,
#            coordinates=[(x, y) for x in self.x_ticks],
#        )
