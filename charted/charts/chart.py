from charted.charts.axes import XAxis, YAxis
from charted.html.element import G, Path, Svg, Text
from charted.utils.defaults import DEFAULT_COLORS
from charted.utils.exceptions import InvalidValue
from charted.utils.helpers import calculate_text_dimensions

from charted.utils.themes import Theme
from charted.utils.transform import translate
from charted.utils.types import Labels, MeasuredText, Vector, Vector2D


class Chart(Svg):
    x_stacked: bool = False
    y_stacked: bool = False

    def __init__(
        self,
        width: float = 500,
        height: float = 500,
        zero_index: bool = True,
        x_data: Vector | Vector2D | None = None,
        y_data: Vector | Vector2D | None = None,
        x_labels: Labels | None = None,
        y_labels: Labels | None = None,
        series_names: list[str] | None = None,
        title: str | None = None,
        theme: Theme | None = None,
    ):
        super().__init__(
            width=width,
            height=height,
            viewBox=self.calculate_viewbox(width, height),
        )

        if not x_data and not x_labels and not y_data and not y_labels:
            raise InvalidValue("data", "No data was provided to the Chart element.")

        # Handle empty lists by treating them as None
        if y_data is not None and len(y_data) == 0:
            y_data = None
        if x_data is not None and len(x_data) == 0:
            x_data = None

        # Auto-generate x_labels if x_data/x_labels not provided but y_data is
        if not x_data and not x_labels and y_data is not None:
            array_len = len(y_data[0]) if isinstance(y_data[0], list) else len(y_data)
            x_labels = [" " for i in range(array_len)]

        # Auto-generate y_labels if y_data/y_labels not provided but x_data is
        if not y_data and not y_labels and x_data is not None:
            array_len = len(x_data[0]) if isinstance(x_data[0], list) else len(x_data)
            y_labels = [" " for i in range(array_len)]

        self.series_names = series_names
        self.theme = Theme.load(theme)

        self.zero_index = zero_index

        self.x_labels = x_labels
        self.y_labels = y_labels
        self.x_data = x_data
        self.y_data = y_data

        self.width = width
        self.height = height
        self.h_padding = self.theme.get("padding", {}).get("h_padding", 0.05)
        self.v_padding = self.theme.get("padding", {}).get("v_padding", 0.05)

        self._title = None
        if title:
            self._title = calculate_text_dimensions(title)

        self.x_axis = XAxis(
            parent=self,
            data=self.x_data,
            labels=x_labels,
            stacked=self.x_stacked,
            zero_index=self.zero_index,
            config=self.theme.get("v_grid", {}),
        )

        self.y_axis = YAxis(
            parent=self,
            data=self.y_data,
            labels=y_labels,
            stacked=self.y_stacked,
            zero_index=self.zero_index,
            config=self.theme.get("h_grid", {}),
        )

        self.y_offsets = self.y_data if self.y_data else []

        self.y_values = self.y_data if self.y_data else []
        self.x_values = self.x_data if self.x_data else []
        self.colors = self.theme.get("colors", [])

        self.add_children(
            self.container,
            self.title,
            self.y_axis,
            self.x_axis,
            self.zero_line,
            self.representation,
            self.legend,
        )

    @classmethod
    def _validate_data(cls, data: Vector | Vector2D | None) -> Vector2D:
        if not data:
            return None

        if len(data) == 0:
            raise InvalidValue("data", "No data provided.")

        if not isinstance(data[0], list):
            data = [data]

        max_length = max([len(i) for i in data])

        if not all([len(i) == max_length for i in data]):
            raise InvalidValue("data", "Not all vectors were same length")

        return data

    def validate_x_data(self, data: Vector | Vector2D | None) -> Vector2D:
        return self._validate_data(data)

    def validate_y_data(self, data: Vector | Vector2D | None) -> Vector2D:
        return self._validate_data(data)

    @classmethod
    def _validate_attribute_value(cls, name: str, value: float):
        if value < 0:
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
    def x_count(self) -> int:
        if self.x_data:
            return len(self.x_data[0])
        elif self.x_labels:
            return len(self.x_labels)
        return 0

    @property
    def y_count(self) -> int:
        if self.y_data:
            return len(self.y_data[0])
        elif self.y_labels:
            return len(self.y_labels)
        return 0

    @property
    def plot_width(self) -> float:
        return self.width - (self.left_padding + self.right_padding)

    @property
    def plot_height(self) -> float:
        return self.height - (self.bottom_padding + self.top_padding)

    @property
    def colors(self) -> list[str]:
        return self._colors

    @colors.setter
    def colors(self, colors) -> None:
        if not colors:
            colors = [*DEFAULT_COLORS]
        while self.x_count > len(colors):
            colors = [*colors, *DEFAULT_COLORS]
        self._colors = colors

    @property
    def title(self) -> MeasuredText:
        if not self._title:
            return None
        return Text(
            transform=[
                translate(
                    self.left_padding + self._title.width / 2,
                    self._title.height / 2 + self.top_padding,
                )
            ],
            text=self._title.text,
            fill=self.theme.get("title", {}).get("font_color", "#444444"),
            font_family=self.theme.get("title", {}).get("font_family", "sans-serif"),
            font_weight=self.theme.get("title", {}).get("font_weight", "normal"),
            font_size=self.theme.get("title", {}).get("font_size", "14px"),
            text_anchor="middle",
            dominant_baseline="middle",
        )

    @title.setter
    def title(self, value: str | None) -> None:
        if value:
            self._title = calculate_text_dimensions(value)
        else:
            self._title = None

    @property
    def left_padding(self) -> float:
        return self.width * self.h_padding

    @property
    def right_padding(self) -> float:
        return self.width * self.h_padding

    @property
    def top_padding(self) -> float:
        title_height = 0
        if self._title:
            title_height = self._title.height
        return self.height * self.v_padding + title_height

    @property
    def bottom_padding(self) -> float:
        if not self.x_labels:
            return self.height * self.v_padding

        def get_label_dimensions(label):
            if isinstance(label, MeasuredText):
                return label.height, label.width
            else:
                return 12, 8

        max_label_height = max(
            [get_label_dimensions(label)[0] for label in self.x_labels]
        )
        max_label_width = max(
            [get_label_dimensions(label)[1] for label in self.x_labels]
        )

        return max(
            self.height * self.v_padding,
            max_label_height + max_label_width * 0.25,
        )

    @property
    def base_transform(self) -> list:
        return [translate(self.left_padding, self.bottom_padding)]

    @property
    def container(self) -> G:
        return G(
            id="container",
            transform=[
                translate(
                    self.left_padding,
                    self.top_padding,
                )
            ],
        )

    @property
    def legend(self) -> G:
        if not self.series_names:
            return G()

        g = G(transform=[translate(self.width - self.right_padding, self.top_padding)])

        for i, series_name in enumerate(self.series_names):
            row_y = i * 20
            g.add_child(
                Text(
                    text=series_name,
                    x=0,
                    y=row_y,
                    font_family=self.theme.get("legend", {}).get(
                        "font_family", "sans-serif"
                    ),
                    font_weight=self.theme.get("legend", {}).get(
                        "font_weight", "normal"
                    ),
                    font_size=self.theme.get("legend", {}).get("font_size", "11px"),
                )
            )

        return g

    @property
    def zero_line(self) -> Path | None:
        if self.y_axis and self.y_axis.zero is not None:
            return Path(
                d=Path.get_path(0, self.y_axis.zero, self.width, self.y_axis.zero),
                stroke=self.theme.get("zero_line", "#000000"),
                stroke_width=1,
            )
        return None

    @property
    def representation(self):
        raise NotImplementedError(
            "Subclasses must implement the representation property."
        )

    def _calculate_labels(self) -> Labels:
        return self.x_labels

    def calculate_viewbox(
        self, width: float, height: float
    ) -> tuple[float, float, float, float]:
        return (0, 0, width, height)
