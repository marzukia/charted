from collections import defaultdict
from typing import List, Optional, Tuple, Union
from charted.charts.axes import Axes
from charted.charts.chart import Chart
from charted.charts.plot import Plot
from charted.fonts.utils import (
    DEFAULT_FONT,
    DEFAULT_TITLE_FONT_SIZE,
    calculate_text_dimensions,
)
from charted.html.element import G, Path, Text
from charted.utils.colors import generate_complementary_colors
from charted.utils.transform import rotate, translate
from charted.utils.types import Bounds, Labels, Vector, Vector2D


class Column(Chart):
    _colors = ["#EF6F6C", "#a74e4c", "#f5a9a7", "#477160", "#324f43", "#91aaa0"]

    def __init__(
        self,
        data: Union[Vector | Vector2D],
        title: str = None,
        labels: Optional[Labels] = None,
        colors: List[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if colors:
            self._colors = colors

        self.title_text = calculate_text_dimensions(
            title,
            font_size=DEFAULT_TITLE_FONT_SIZE,
        )
        self.labels = labels
        validated_data = self._validate_data(data)
        self.data = validated_data
        self.bounds = validated_data
        self.add_children(
            self.container,
            self.plot,
            self.series,
            self.zero_line,
            self.axes,
        )
        if self.title_text:
            self.add_child(self.title)

    def _validate_data(self, data: Union[Vector, Vector2D]) -> Union[Vector, Vector2D]:
        if len(data) == 0:
            raise Exception("No data provided.")

        max_length = max([len(i) for i in data])
        if not all([len(i) == max_length for i in data]):
            raise Exception("Not all vectors were same length")

        return data

    @property
    def colors(self) -> List[str]:
        new_colors = [*self._colors]
        while self.no_columns > len(new_colors):
            for color in generate_complementary_colors(self._colors):
                if len(new_colors) >= self.no_columns:
                    break
                new_colors.append(color)
        return new_colors

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

    @property
    def v_pad(self) -> float:
        return self.padding * self.height

    @property
    def h_pad(self) -> float:
        return self.padding * self.width

    @property
    def title(self) -> Text:
        return Text(
            transform=[
                translate(
                    x=-self.title_text.width / 2,
                    y=self.title_text.height / 4,
                )
            ],
            text=self.title_text.text,
            font_family=DEFAULT_FONT,
            font_size=DEFAULT_TITLE_FONT_SIZE,
            x=self.width / 2,
            y=self.v_pad / 2,
        )

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

    @classmethod
    def _reverse(
        cls,
        value: float,
        max_value: float,
        min_value: float,
        length: float,
    ) -> float:
        value_range = max_value - min_value
        normalised_value = value / length
        return normalised_value * value_range

    def _reverse_y(self, value: float) -> float:
        return self._reverse(value, self.max_y, self.min_y, self.plot_height)

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
        dx = self.h_pad
        dy = self.v_pad

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
            for x, y, offset in zip(
                self.x_ticks,
                reversed(y_values),
                reversed(y_offsets),
            ):
                path = Path.get_path(x, offset, self.column_width, y)
                paths.append(path)
            g.add_child(Path(d=paths, fill=color))

        return g

    @property
    def y_zero(self) -> float:
        return self._reproject_y(abs(self.bounds.y2))

    @property
    def x_zero(self) -> float:
        return self._reproject_x(abs(self.bounds.x1))

    @property
    def zero_line(self) -> Path:
        dy = (self.height * self.padding) + self.y_zero
        dx = self.width * self.padding
        return Path(
            d=[f"M{dx} {dy}", f"h{self.plot_width}z"],
            stroke="black",
        )

    @property
    def plot(self) -> Plot:
        return Plot(
            parent=self,
            bounds=self.calculate_plot_corners(
                self.width,
                self.height,
                self.padding,
            ),
            width=self.plot_width,
            height=self.plot_height,
            padding=self.padding,
            # TODO: Remove this hardcoded no_y
            no_y=5,
            x_coordinates=[i - (self.column_width / 4) for i in self.x_ticks],
        )

    @property
    def container(self) -> Path:
        return Path(fill="white", d=Path.get_path(0, 0, self.width, self.height))

    @property
    def axes(self) -> Axes:
        return Axes(parent=self)
