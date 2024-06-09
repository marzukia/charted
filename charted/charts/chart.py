from typing import List, Optional, Tuple, Union

from charted.charts.axes import Axes
from charted.charts.plot import Plot
from charted.fonts.utils import (
    DEFAULT_FONT,
    DEFAULT_TITLE_FONT_SIZE,
    calculate_text_dimensions,
)
from charted.html.element import Path, Svg, Text
from charted.html.formatter import format_html
from charted.utils.colors import generate_complementary_colors
from charted.utils.transform import translate
from charted.utils.types import Bounds, Labels, MeasuredText, Vector, Vector2D

DEFAULT_COLORS = ["#EF6F6C", "#477160", "#a74e4c", "#f5a9a7", "#324f43", "#91aaa0"]


class Chart(Svg):
    def __init__(
        self,
        width: float,
        height: float,
        padding: float,
        data: Union[Vector | Vector2D],
        labels: Optional[Labels] = None,
        title: str = None,
        colors: List[str] = None,
        **kwargs,
    ):
        super().__init__(
            width=width,
            height=height,
            viewBox=self.calculate_viewbox(width, height),
            **kwargs,
        )
        self.labels = labels
        validated_data = self._validate_data(data)
        self.data = validated_data
        self.bounds = validated_data
        self.colors = colors
        self.title_text = title
        self.width = width
        self.height = height
        self.padding = padding

    @classmethod
    def calculate_plot_corners(
        cls,
        width: float,
        height: float,
        padding: float = 0,
    ) -> Bounds:
        x_padding = width * padding
        y_padding = height * padding
        x1 = 0 + x_padding
        x2 = width - x_padding
        y1 = 0 + y_padding
        y2 = height - y_padding
        return Bounds(x1, x2, y1, y2)

    @property
    def plot(self) -> Plot:
        return Plot(
            parent=self,
            bounds=self.calculate_plot_corners(
                self.width,
                self.height,
                self.padding,
            ),
            width=self.width,
            height=self.height,
            padding=self.padding,
        )

    def __repr__(self):
        return format_html(self.html)

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
    def plot_width(self) -> float:
        return self.width * (1 - (self.padding * 2))

    @property
    def plot_height(self) -> float:
        return self.height * (1 - (self.padding * 2))

    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        return Bounds(*self._bounds)

    @bounds.setter
    def bounds(self, data: Vector2D) -> None:
        self._bounds = self.get_bounds(data)
        self.min_x, self.min_y, self.max_x, self.max_y = self._bounds

    def _validate_data(self, data: Union[Vector, Vector2D]) -> Vector2D:
        if len(data) == 0:
            raise Exception("No data provided.")

        if type(data[0]) is not list:
            data = [data]

        max_length = max([len(i) for i in data])

        if not all([len(i) == max_length for i in data]):
            raise Exception("Not all vectors were same length")

        return data

    @property
    def v_pad(self) -> float:
        return self.padding * self.height

    @property
    def h_pad(self) -> float:
        return self.padding * self.width

    @property
    def colors(self) -> List[str]:
        return self._colors

    @colors.setter
    def colors(self, colors) -> None:
        if not colors:
            colors = [*DEFAULT_COLORS]
        new_colors = [*colors]
        while self.x_count > len(new_colors):
            for color in generate_complementary_colors(colors):
                if len(new_colors) >= self.x_count:
                    break
                new_colors.append(color)
        self._colors = new_colors

    @property
    def y_zero(self) -> float:
        return self._reproject_y(abs(self.bounds.y2))

    @property
    def x_zero(self) -> float:
        return self._reproject_x(abs(self.bounds.x1))

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
    def title_text(self) -> MeasuredText:
        return self._title_text

    @title_text.setter
    def title_text(self, text: str) -> None:
        if text:
            self._title_text = calculate_text_dimensions(
                text,
                font_size=DEFAULT_TITLE_FONT_SIZE,
            )
        else:
            self._title_text = None

    @property
    def axes(self) -> Axes:
        return Axes(parent=self)

    @property
    def container(self) -> Path:
        return Path(fill="white", d=Path.get_path(0, 0, self.width, self.height))
