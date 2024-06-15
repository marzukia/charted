from charted.charts.axes import XAxis, YAxis
from charted.html.element import G, Path, Svg, Text
from charted.utils.colors import generate_complementary_colors
from charted.utils.defaults import DEFAULT_COLORS, DEFAULT_FONT, DEFAULT_TITLE_FONT_SIZE
from charted.utils.exceptions import InvalidValue
from charted.utils.helpers import (
    calculate_rotation_angle,
    calculate_text_dimensions,
    rotate_coordinate,
)
from charted.utils.transform import translate
from charted.utils.types import Labels, MeasuredText, Vector, Vector2D


class Chart(Svg):
    x_stacked: bool = False
    y_stacked: bool = False

    def __init__(
        self,
        width: float = 500,
        height: float = 500,
        h_padding: float = 0.1,
        v_padding: float = 0.1,
        zero_index: bool = True,
        x_data: Vector | Vector2D | None = None,
        y_data: Vector | Vector2D | None = None,
        x_labels: Labels | None = None,
        y_labels: Labels | None = None,
        title: str | None = None,
        colors: list[str] | None = None,
    ):
        super().__init__(
            width=width,
            height=height,
            viewBox=self.calculate_viewbox(width, height),
        )

        if not x_data and not y_data:
            raise Exception("No data was provided to the Chart element.")

        self.x_labels = x_labels
        self.y_labels = y_labels
        self.x_data = x_data
        self.y_data = y_data

        self.width = width
        self.height = height
        self.h_padding = h_padding
        self.v_padding = v_padding

        self.plot_height = height
        self.plot_width = width

        self.x_count = (self.x_data, self.x_labels)
        self.y_count = (self.y_data, self.y_labels)

        self.zero_index = zero_index

        self.x_axis = XAxis(
            parent=self,
            data=self.x_data,
            labels=x_labels,
            stacked=self.x_stacked,
            zero_index=self.zero_index,
        )

        self.y_axis = YAxis(
            parent=self,
            data=self.y_data,
            labels=y_labels,
            stacked=self.y_stacked,
            zero_index=self.zero_index,
        )

        self.y_offsets = self.y_data

        self.y_values = self.y_data
        self.x_values = self.x_data

        self.colors = colors
        self.title = title

        self.add_children(
            self.container,
            self.title,
            self.y_axis,
            self.x_axis,
            self.zero_line,
            self.representation,
        )

    @classmethod
    def _validate_data(cls, data: Vector | Vector2D | None) -> Vector2D:
        if not data:
            return None

        if len(data) == 0:
            raise Exception("No data provided.")

        if type(data[0]) is not list:
            data = [data]

        max_length = max([len(i) for i in data])

        if not all([len(i) == max_length for i in data]):
            raise Exception("Not all vectors were same length")

        return data

    def validate_x_data(self, data: Vector | Vector2D | None) -> Vector2D:
        return self._validate_data(data)

    def validate_y_data(self, data: Vector | Vector2D | None) -> Vector2D:
        return self._validate_data(data)

    @classmethod
    def _validate_attribute_value(cls, name: str, value: float):
        if value <= 0:
            raise InvalidValue(name, value)
        return value

    @property
    def x_data(self) -> Vector2D:
        return self._x_data

    @x_data.setter
    def x_data(self, data: Vector | Vector2D | None = None) -> None:
        validated_data = self.validate_x_data(data)
        self._x_data = validated_data

    @property
    def y_data(self) -> Vector2D:
        return self._y_data

    @y_data.setter
    def y_data(self, data: Vector | Vector2D | None = None) -> None:
        validated_data = self.validate_y_data(data)
        self._y_data = validated_data

    @property
    def width(self) -> float:
        return self._width

    @width.setter
    def width(self, width: float) -> None:
        self._width = self._validate_attribute_value("width", width)

    @property
    def height(self) -> float:
        return self._height

    @height.setter
    def height(self, height: float) -> None:
        self._height = self._validate_attribute_value("height", height)

    @property
    def h_padding(self) -> float:
        return self._h_padding

    @h_padding.setter
    def h_padding(self, h_padding: float) -> None:
        if h_padding > 1:
            raise InvalidValue("h_padding", h_padding)
        self._h_padding = self._validate_attribute_value("h_padding", h_padding)

    @property
    def v_padding(self) -> float:
        return self._v_padding

    @v_padding.setter
    def v_padding(self, v_padding: float) -> None:
        if v_padding > 1:
            raise InvalidValue("v_padding", v_padding)
        self._v_padding = self._validate_attribute_value("v_padding", v_padding)

    @property
    def plot_width(self) -> float:
        return self._plot_width

    @plot_width.setter
    def plot_width(self, width: float) -> None:
        calculated = width - (self.h_pad * 2)
        if calculated < 0:
            raise Exception("'calculated' was negative, check width and h_padding.")
        self._plot_width = calculated

    @property
    def plot_height(self) -> float:
        return self.height - (self.bottom_padding + self.top_padding)

    @plot_height.setter
    def plot_height(self, height: float) -> None:
        calculated = self.height - (self.v_pad * 2)
        if calculated < 0:
            raise Exception("'calculated' was negative, check height and v_padding.")
        self._plot_height = calculated

    @property
    def colors(self) -> list[str]:
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
    def title(self) -> MeasuredText:
        if not self._title:
            return None
        return Text(
            transform=[
                translate(
                    x=-self._title.width / 2,
                    y=self._title.height / 4,
                )
            ],
            text=self._title.text,
            font_family=DEFAULT_FONT,
            font_weight="bold",
            font_size=DEFAULT_TITLE_FONT_SIZE,
            x=self.width / 2,
            y=self.v_pad / 2,
        )

    @title.setter
    def title(self, text: str) -> None:
        if text:
            self._title = calculate_text_dimensions(
                text,
                font_size=DEFAULT_TITLE_FONT_SIZE,
            )
        else:
            self._title = None

    @property
    def v_pad(self) -> float:
        return self.v_padding * self.height

    @property
    def h_pad(self) -> float:
        return self.h_padding * self.width

    @property
    def container(self) -> Path:
        return Path(
            fill="white",
            d=Path.get_path(0, 0, self.width, self.height),
        )

    @property
    def x_labels(self) -> list[MeasuredText] | None:
        return self._x_labels

    @x_labels.setter
    def x_labels(self, x_labels: list[str]) -> None:
        if x_labels:
            x_labels = [calculate_text_dimensions(label) for label in x_labels]
        self._x_labels = x_labels

    @property
    def y_labels(self) -> list[MeasuredText] | None:
        return self._y_labels

    @y_labels.setter
    def y_labels(self, y_labels: list[str]) -> None:
        if y_labels:
            y_labels = [calculate_text_dimensions(label) for label in y_labels]
        self._y_labels = y_labels

    @property
    def x_label_rotation(self) -> tuple[float, float, float]:
        if not self.x_labels:
            return None

        rotation_angle = 0
        width = 0
        for label in self.x_labels:
            angle = calculate_rotation_angle(label.width, self.x_width)
            width = max(width, label.width)
            if angle and (angle > rotation_angle):
                rotation_angle = max(angle, rotation_angle)

        return rotation_angle, width

    @property
    def top_padding(self) -> float:
        return self.v_pad

    @property
    def bottom_padding(self) -> float:
        if not self.x_label_rotation:
            return self.v_pad

        rotation_angle, width = self.x_label_rotation
        x, y = (width, 0)
        _, dy = rotate_coordinate(x, y, rotation_angle)
        return self.v_pad + abs((dy - y))

    @property
    def x_count(self) -> int:
        return self._x_count

    @x_count.setter
    def x_count(self, kwargs: tuple[Vector2D | None, list[str] | None]) -> None:
        x_data, x_labels = kwargs
        if not x_data:
            cnt = len(x_labels)
        elif x_data:
            cnt = len(x_data[0])
        self._x_count = cnt

    @property
    def y_count(self) -> int:
        return self._y_count

    @y_count.setter
    def y_count(self, kwargs: tuple[Vector2D | None, list[str] | None]) -> None:
        y_data, y_labels = kwargs
        if not y_data:
            cnt = len(y_labels)
        cnt = len(y_data[0])
        self._y_count = cnt

    @property
    def y_offsets(self) -> Vector2D:
        return self._y_offsets

    @y_offsets.setter
    def y_offsets(self, y_data: Vector2D | None = None) -> None:
        offsets = []
        negative_offsets = [0] * self.y_count
        positive_offsets = [0] * self.y_count

        for row in y_data:
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

        self._y_offsets = [[self.y_axis.reproject(y) for y in arr] for arr in offsets]

    @property
    def x_width(self) -> float:
        return self.plot_width / self.x_count

    @property
    def y_values(self) -> Vector2D:
        return self._y_values

    @y_values.setter
    def y_values(self, y_data: Vector2D) -> None:
        data = []
        for arr in y_data:
            row = []
            for y in arr:
                if not self.y_stacked:
                    v = self.y_axis.reproject(y)
                else:
                    v = self.y_axis.reproject(abs(y))
                    if y < 0:
                        v = -v
                row.append(v)
            data.append(row)
        self._y_values = data

    @property
    def x_values(self) -> Vector2D:
        return self._x_values

    @x_values.setter
    def x_values(self, x_data: Vector2D) -> None:
        if not x_data and self.x_labels:
            x_data = [[i for i in range(len(self.x_labels))]]
        else:
            x_data = [*x_data]

        y_len = len(self.y_data)
        if len(x_data) != y_len:
            if not len(x_data) == 1:
                raise Exception("x and y data series do not match")
            x_data = x_data * y_len

        xz = self.x_axis.reproject(self.x_axis.axis_dimension.min_value)

        data = []
        for arr in x_data:
            row = []
            for x in arr:
                v = self.x_axis.reproject(x) + xz
                row.append(v)
            data.append(row)

        self._x_values = data

    @property
    def zero_line(self) -> Path:
        paths = []
        if self.x_axis.axis_dimension.min_value < 0:
            paths += [
                f"M{self.x_axis.zero} {0}",
                f"v{self.plot_height}z",
            ]

        if self.y_axis.axis_dimension.min_value < 0:
            y = self.plot_height - self.y_axis.zero
            min_y = self.y_axis.axis_dimension.min_value
            if self.y_stacked and min_y < 0:
                y -= self.y_axis.reproject(abs(min_y))

            paths += [
                f"M{0} {y}",
                f"h{self.plot_width}z",
            ]

        if len(paths) > 0:
            return Path(
                transform=[translate(self.h_pad, self.v_pad)],
                d=paths,
                stroke="black",
            )

    @property
    def representation(self) -> G:
        raise Exception("representation not implemented for instance of Chart.")
