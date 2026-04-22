from charted.charts.axes import Axis, XAxis, YAxis
from charted.config import get_chart_theme
from charted.html.element import G, Path, Rect, Svg, Text
from charted.utils.colors import generate_complementary_colors
from charted.utils.defaults import DEFAULT_COLORS
from charted.utils.exceptions import InvalidValue
from charted.utils.helpers import (
    calculate_rotation_angle,
    calculate_text_dimensions,
    rotate_coordinate,
)
from charted.utils.themes import Theme
from charted.utils.transform import translate
from charted.utils.types import (
    Labels,
    MeasuredText,
    SeriesStyleConfig,
    Vector,
    Vector2D,
)


class Chart(Svg):
    """Base class for all SVG chart types.

    Provides common functionality for chart rendering including
    theme application, data validation, coordinate calculations,
    and SVG generation. All chart types inherit from this class.

    Attributes:
        x_stacked: If True, stack series along x-axis
        y_stacked: If True, stack series along y-axis
        render_axes: Whether to draw axes and grid lines
        theme: Applied theme configuration
        colors: Auto-generated color palette for series

    Example:
        >>> from charted.charts.chart import Chart
        >>> # Use concrete subclasses instead:
        >>> from charted import BarChart, LineChart, PieChart
    """

    x_stacked: bool = False
    y_stacked: bool = False
    render_axes: bool = True
    render_axes: bool = True

    def _repr_svg_(self) -> str:
        """Return SVG string for Jupyter notebook display.

        This method is automatically called by Jupyter to render
        SVG charts inline in notebooks.

        Returns:
            str: The SVG string representation of the chart.
        """
        return self.svg

    def to_svg(self) -> str:
        """Get the SVG string representation of the chart.

        Returns:
            str: The complete SVG markup as a string.
        """
        return self.svg

    def to_markdown(self, alt_text: str | None = None, width: str | None = None) -> str:
        """Generate markdown markup for the chart.

        Args:
            alt_text: Alternative text for the image. Defaults to title if available.
            width: Optional width specification (e.g., '500px' or '100%').

        Returns:
            str: Markdown image syntax with data URL.

        Example:
            >>> chart = BarChart(data=[1, 2, 3], labels=['a', 'b', 'c'])
            >>> print(chart.to_markdown())
            ![chart](data:image/svg+xml,{encoded_svg})
        """
        from urllib.parse import quote

        svg_data = self.svg
        alt = alt_text or (self.title if self.title else "chart")

        # Encode SVG as data URL
        encoded = quote(svg_data)
        data_url = f"data:image/svg+xml,{encoded}"

        if width:
            return f"![{alt}]({data_url}){{width={width}}}"
        return f"![{alt}]({data_url})"

    def _repr_html_(self) -> str:
        """Return HTML wrapper for the chart.

        This method is called by IPython/Jupyter when displaying
        objects in HTML format. Wraps the SVG in a container div.

        Returns:
            str: HTML string with the embedded SVG.
        """
        return f'<div style="display: inline-block;">{self.svg}</div>'

    def save(self, path: str) -> None:
        """Save the chart to a file.

        Args:
            path: File path to save the SVG file.
        """
        with open(path, "w") as f:
            f.write(self.svg)

    def __init__(
        self,
        width: float = 500,
        height: float = 500,
        zero_index: bool = True,
        x_data: Vector | Vector2D | None = None,
        y_data: Vector | Vector2D | None = None,
        series_styles: list[SeriesStyleConfig] | None = None,
        x_labels: Labels | None = None,
        y_labels: Labels | None = None,
        series_names: list[str] | None = None,
        x_stacked: bool = False,
        title: str | None = None,
        theme: Theme | None = None,
        chart_type: str | None = None,
    ):
        super().__init__(
            width=width,
            height=height,
            viewBox=self.calculate_viewbox(width, height),
        )

        if not x_data and not y_data:
            raise Exception("No data was provided to the Chart element.")

        if not x_data and not x_labels:
            array_len = len(y_data[0]) if type(y_data[0]) is list else len(y_data)
            x_labels = [" " for i in range(array_len)]

        self.series_names = series_names
        self.series_styles = series_styles
        self.x_stacked = x_stacked
        self.series_names = series_names
        self.x_stacked = x_stacked

        self.zero_index = zero_index

        self.x_labels = x_labels
        self.y_labels = y_labels
        self.x_data = x_data
        self.y_data = y_data

        self.width = width
        self.height = height
        self.x_stacked = x_stacked

        # Load and apply theme
        self.theme = Theme.load(theme)

        # Apply chart-type-specific overrides if available
        if chart_type:
            from charted.config import load_config

            config = load_config()
            chart_override = get_chart_theme(config, chart_type)
            if chart_override:
                chart_theme = Theme.load(chart_override)
                # Merge: chart override takes precedence over base theme
                for key in self.theme:
                    if key not in chart_theme:
                        chart_theme[key] = self.theme[key]
                    elif isinstance(self.theme[key], dict) and isinstance(
                        chart_theme[key], dict
                    ):
                        for subkey in self.theme[key]:
                            if subkey not in chart_theme[key]:
                                chart_theme[key][subkey] = self.theme[key][subkey]
                self.theme = chart_theme

        self.h_padding = self.theme["padding"]["h_padding"]
        self.v_padding = self.theme["padding"]["v_padding"]

        self.title = title

        self.x_count = (self.x_data, self.x_labels)
        self.y_count = (self.y_data, self.y_labels)

        self.x_axis = XAxis(
            parent=self,
            data=self.x_data,
            labels=x_labels,
            stacked=self.x_stacked,
            zero_index=(
                False
                if (x_data is not None and x_labels is not None)
                else self.zero_index
            ),
            config=self.theme["v_grid"],
        )

        self.y_axis = YAxis(
            parent=self,
            data=self.y_data,
            labels=y_labels,
            stacked=self.y_stacked,
            zero_index=self.zero_index,
            config=self.theme["h_grid"],
        )

        self.y_offsets = self.y_data
        self.x_offsets = self.x_data

        self.y_values = self.y_data
        self.x_values = self.x_data

        self.colors = self.theme["colors"]

        children = [self.container, self.title]
        if self.render_axes:
            children += [self.y_axis, self.x_axis, self.zero_line]
        children += [self.representation, self.legend]
        self.add_children(*children)

    @classmethod
    def _validate_data(cls, data: Vector | Vector2D | None) -> Vector2D:
        if data is not None and len(data) == 0:
            raise Exception("No data was provided.")

        if not data:
            return None

        if type(data[0]) is not list:
            data = [data]

        max_length = max([len(i) for i in data])

        if not all([len(i) == max_length for i in data]):
            raise Exception("Not all vectors were same length")

        return data

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
        validated_data = self._validate_data(data)
        self._x_data = validated_data

    @property
    def y_data(self) -> Vector2D:
        return self._y_data

    @y_data.setter
    def y_data(self, data: Vector | Vector2D | None = None) -> None:
        validated_data = self._validate_data(data)
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
        return self.width - (self.left_padding + self.right_padding)

    @property
    def plot_height(self) -> float:
        return self.height - (self.bottom_padding + self.top_padding)

    def get_base_transform(self) -> list:
        from charted.utils.transform import rotate, scale

        return [
            translate(-self.h_pad, -self.bottom_padding),
            rotate(180, self.width / 2, self.height / 2),
            scale(-1, 1),
            translate(-self.plot_width, 0),
        ]

    @property
    def x_offset(self) -> float:
        """Calculate x-offset for charts with x_labels.

        Ordinal charts (no explicit x_data): shift by one tick width so data
        points sit at the centre of their column.  XY charts (explicit x_data
        provided): positions are already correct from reproject; offset is 0.
        """
        if self.x_labels and self._x_data is None:
            return self.x_axis.reproject(1)
        return 0

    def _apply_stacking(self, y: float, y_offset: float) -> float:
        """Apply y-stacking if enabled."""
        return y + y_offset if self.y_stacked else y

    @property
    def colors(self) -> list[str]:
        return self._colors

    @colors.setter
    def colors(self, colors) -> None:
        if not colors:
            colors = [*DEFAULT_COLORS]
        new_colors = [*colors]
        if self.y_data:
            series_count = len(self.y_data)
        elif self.x_data:
            series_count = len(self.x_data)
        else:
            series_count = 0
        target = max(series_count, self.x_count)
        while target > len(new_colors):
            for color in generate_complementary_colors(colors):
                if len(new_colors) >= target:
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
                    y=self._title.height,
                )
            ],
            text=self._title.text,
            fill=self.theme["title"]["font_color"],
            font_family=self.theme["title"]["font_family"],
            font_weight=self.theme["title"]["font_weight"],
            font_size=self.theme["title"]["font_size"],
            x=self.width / 2,
            y=self.v_pad / 2,
        )

    @title.setter
    def title(self, text: str) -> None:
        if text:
            self._title = calculate_text_dimensions(
                text,
                font=self.theme["title"]["font_family"],
                font_size=self.theme["title"]["font_size"],
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
    def left_padding(self) -> float:
        labels = self.y_labels

        if not labels:
            _, values = Axis.calculate_axis_values(
                data=self.y_data,
                stacked=self.y_stacked,
                zero_index=self.zero_index,
            )
            labels = [str(round(x, 2)) for x in values]

        max_width = 0.0
        for label in labels:
            if hasattr(label, "width"):
                width = label.width
            else:
                width = calculate_text_dimensions(str(label)).width
            if width > max_width:
                max_width = width

        return self.h_pad + max_width

    @property
    def right_padding(self) -> float:
        return self.h_pad

    @property
    def top_padding(self) -> float:
        offset = 0
        if self._title:
            offset += self._title.height * 1.5
        return self.v_pad + offset

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
            self._y_count = len(y_labels)
            return
        cnt = len(y_data[0])
        self._y_count = cnt

    @property
    def y_offsets(self) -> Vector2D:
        return self._y_offsets

    @y_offsets.setter
    def y_offsets(self, y_data: Vector2D | None = None) -> None:
        if not y_data:
            offsets = [[0] * self.y_count]
            self._y_offsets = [
                [self.y_axis.reproject(y) for y in arr] for arr in offsets
            ]
            return

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
    def x_offsets(self):
        return self._x_offsets

    @x_offsets.setter
    def x_offsets(self, x_data=None):
        if not x_data or not getattr(self, "x_stacked", False):
            offsets = [[0] * self.x_count]
            self._x_offsets = [
                [self.x_axis.reproject(x) for x in arr] for arr in offsets
            ]
            return

        # For x_stacked horizontal bars, accumulate offsets per bar index
        # (mirrors y_offsets logic for vertical stacking)
        offsets = []
        negative_offsets = [0] * self.x_count
        positive_offsets = [0] * self.x_count

        for row in x_data:
            row_offsets = []
            for i, x in enumerate(row):
                current_offset = 0
                if x >= 0:
                    current_offset = positive_offsets[i]
                    positive_offsets[i] += x
                elif x < 0:
                    current_offset = negative_offsets[i]
                    negative_offsets[i] -= abs(x)
                row_offsets.append(current_offset)
            offsets.append(row_offsets)

        self._x_offsets = [[self.x_axis.reproject(x) for x in arr] for arr in offsets]

    @property
    def x_width(self) -> float:
        return self.plot_width / self.x_count

    @property
    def y_values(self) -> Vector2D:
        return self._y_values

    @y_values.setter
    def y_values(self, y_data: Vector2D) -> None:
        if not y_data:
            self._y_values = [[0] * self.y_count]
            return

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

        y_len = len(self.y_data) if self.y_data else 0
        if len(x_data) != y_len:
            if not len(x_data) == 1:
                raise Exception("x and y data series do not match")
            x_data = x_data * y_len

        data = []
        for arr in x_data:
            row = []
            for x in arr:
                v = self.x_axis.reproject(x)
                row.append(v)
            data.append(row)

        self._x_values = data

    @property
    def zero_line(self) -> Path:
        paths = []
        is_bar_chart = getattr(self, "y_height", None) is not None
        is_xy_line = self._x_data is not None and not is_bar_chart
        if self.x_axis.axis_dimension.min_value < 0 and not is_xy_line:
            x = self.x_axis.zero
            min_x = self.x_axis.axis_dimension.min_value
            # Mirror y_stacked compensation: in stacked mode with negative
            # values the x-axis reproject is relative-to-zero, so shift
            # right by reproject(abs(min_x)) for absolute placement.
            if self.x_stacked and min_x < 0:
                x += self.x_axis.reproject(abs(min_x))
            paths += [
                f"M{x} {0}",
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
                transform=[translate(self.left_padding, self.top_padding)],
                d=paths,
                stroke="black",
            )

    @property
    def representation(self) -> G:
        raise Exception("representation not implemented for instance of Chart.")

    @property
    def legend(self):
        if not self.theme["legend"] or not self.series_names:
            return None

        legend_entries = [
            calculate_text_dimensions(x, font_size=self.theme["legend"]["font_size"])
            for x in self.series_names
        ]
        icon_height = max(x.height for x in legend_entries)
        legend_width = max(x.width for x in legend_entries) + icon_height + 2
        legend_height = len(legend_entries) * (icon_height + 2)

        # Anchor legend fully inside the plot borders. The background Rect is
        # translated by -legend_width*padding/2 on x, so its right edge sits
        # at x0 + legend_width*(1 + padding/2). We solve for x0 so the right
        # edge lands just inside the plot's right border (with a small inset).
        pad = self.theme["legend"]["legend_padding"]
        plot_right = self.left_padding + self.plot_width
        plot_left = self.left_padding
        inset = 4
        positions = {
            "topright": {
                "x0": plot_right - inset - legend_width * (1 + pad / 2),
                "y0": self.top_padding + inset + legend_height * (pad / 2),
            },
            "topleft": {
                "x0": plot_left + inset + legend_width * (pad / 2),
                "y0": self.top_padding + inset + legend_height * (pad / 2),
            },
        }

        position = positions.get(self.theme["legend"]["position"], None)
        if not position:
            raise Exception("Invalid position.")

        x0, y0 = position["x0"], position["y0"]

        legend = G()
        legend.add_child(
            Rect(
                transform=translate(
                    x=-(legend_width * self.theme["legend"]["legend_padding"] / 2),
                    y=-(legend_height * self.theme["legend"]["legend_padding"] / 2),
                ),
                x=x0,
                y=y0,
                width=legend_width * (1 + self.theme["legend"]["legend_padding"]),
                height=legend_height * (1 + self.theme["legend"]["legend_padding"]),
                fill="#ffffff",
                stroke="#CCCCCC",
            )
        )

        for i, (legend_text, color) in enumerate(zip(legend_entries, self.colors)):
            h = legend_text.height
            g = G(transform=translate(0, y=(2 * i) + h))
            y = y0 + (i * h)
            rect = Rect(y=y - h, x=x0, width=h, height=h, fill=color)
            text = Text(
                y=y - (h / 4),
                x=x0 + 2 + h,
                text=legend_text.text,
                font_size=self.theme["legend"]["font_size"],
                font_family="Helvetica",
            )
            g.add_children(rect, text)
            legend.add_child(g)

        return legend
