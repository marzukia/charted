from typing import List, Optional, Union

from charted.charts.axes import Axes
from charted.charts.chart import Chart
from charted.charts.plot import Plot
from charted.fonts.utils import (
    DEFAULT_FONT,
    DEFAULT_TITLE_FONT_SIZE,
    calculate_text_dimensions,
)
from charted.html.element import Circle, G, Path, Text
from charted.utils.transform import rotate, translate
from charted.utils.types import Labels, Vector, Vector2D


class Line(Chart):

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
        self.labels = [*labels, " "]
        validated_data = self._validate_data(data)
        self.data = validated_data
        self.bounds = validated_data
        self.add_children(
            self.container,
            self.plot,
            self.points,
            self.zero_line,
            self.axes,
        )
        if self.title_text:
            self.add_child(self.title)

    @classmethod
    def get_bounds(cls, data: Vector2D):
        agg = []
        n = len(data[0])
        for arr in data:
            for v in arr:
                agg.append(v)

        min_x = 0
        min_y = min(agg)
        max_x = n - 1
        max_y = max(agg)

        return (min_x, min_y, max_x, max_y)

    @property
    def no_columns(self) -> int:
        return len(self.data[0]) + 1

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
            font_weight="bold",
            font_size=DEFAULT_TITLE_FONT_SIZE,
            x=self.width / 2,
            y=self.v_pad / 2,
        )

    @property
    def column_width(self) -> float:
        return self.plot_width / self.no_columns

    @property
    def x_ticks(self) -> Vector:
        return [
            (self.plot_width / self.no_columns) * i for i in range(0, self.no_columns)
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
    def points(self) -> G:
        dx = self.h_pad
        dy = self.v_pad

        if self.min_y < 0:
            dy += self._reproject_y(abs(self.min_y))

        g = G(
            transform=[
                rotate(180, self.width / 2, self.height / 2),
                translate(x=(dx + self.column_width), y=dy),
            ],
        )

        for y_values, color in zip(self.y_values, self.colors):
            series = G(fill="white", stroke=color, stroke_width=2)
            points = []
            path = []
            for i, (x, y) in enumerate(zip(self.x_ticks, y_values)):
                if i == 0:
                    path.append(f"M{x} {y}")
                else:
                    path.append(f"L{x} {y}")
                c = Circle(cx=x, cy=y, r=4)
                points.append(c)
            line = Path(d=path, fill="none")
            series.add_children(line, *points)
            g.add_children(series)

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
            x_coordinates=self.x_ticks,
        )

    @property
    def container(self) -> Path:
        return Path(fill="white", d=Path.get_path(0, 0, self.width, self.height))

    @property
    def axes(self) -> Axes:
        return Axes(parent=self)
