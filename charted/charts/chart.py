"""Base chart class with reduced responsibilities.

Refactored to extract validation, layout, and rendering utilities into
separate modules to address God Class architectural debt (Issue #64).
"""

from charted.charts.axes import XAxis, YAxis
from charted.config import get_chart_theme, load_config
from charted.constants import DEFAULT_CHART_HEIGHT, DEFAULT_CHART_WIDTH, STRAIGHT_ANGLE
from charted.html.element import G, Path, Svg, Text
from charted.utils.colors import generate_complementary_colors
from charted.utils.defaults import DEFAULT_COLORS
from charted.utils.layout import (
    calculate_bottom_padding,
    calculate_padding_from_labels,
    calculate_top_padding,
    calculate_viewbox,
    calculate_x_label_rotation,
)
from charted.utils.rendering import (
    generate_html_wrapper,
    generate_markdown_image,
)
from charted.utils.themes import Theme
from charted.utils.transform import rotate, scale, translate
from charted.utils.types import (
    Labels,
    MeasuredText,
    SeriesStyleConfig,
    Vector,
    Vector2D,
)
from charted.utils.validation import (
    create_default_labels,
    get_data_length,
    validate_attribute_value,
    validate_data,
)


class Chart(Svg):
    """Base class for all SVG chart types.

    Provides common functionality for chart rendering including
    theme application, data validation, coordinate calculations,
    and SVG generation. All chart types inherit from this class.

    This class has been refactored to focus on core responsibilities:
    - Data representation and state management
    - Coordinate system setup
    - Delegating utilities to focused modules

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

    # =========================================================================
    # Core Representation Methods
    # =========================================================================

    def _repr_svg_(self) -> str:
        """Return SVG string for Jupyter notebook display."""
        return self.svg

    def to_svg(self) -> str:
        """Get the SVG string representation of the chart."""
        return self.svg

    def to_markdown(self, alt_text: str | None = None, width: str | None = None) -> str:
        """Generate markdown markup for the chart."""
        return generate_markdown_image(
            self.svg, alt_text, self.title.text if self._title else None, width
        )

    def _repr_html_(self) -> str:
        """Return HTML wrapper for the chart."""
        return generate_html_wrapper(self.svg)

    def save(self, path: str) -> None:
        """Save the chart to a file."""
        with open(path, "w") as f:
            f.write(self.svg)

    # =========================================================================
    # Initialization
    # =========================================================================

    def __init__(
        self,
        width: float = DEFAULT_CHART_WIDTH,
        height: float = DEFAULT_CHART_HEIGHT,
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
        axis_tick_interval: float | str | None = None,
    ):
        super().__init__(
            width=width,
            height=height,
            viewBox=calculate_viewbox(width, height),
        )

        # Validate and normalize data
        if not x_data and not y_data:
            raise Exception("No data was provided to the Chart element.")

        if not x_data and not x_labels:
            array_len = get_data_length(y_data)
            x_labels = create_default_labels(array_len)

        self.series_names = series_names
        self.series_styles = series_styles
        self.x_stacked = x_stacked
        self.zero_index = zero_index
        self.axis_tick_interval = axis_tick_interval

        # Set data with validation
        self.x_labels = x_labels
        self.y_labels = y_labels
        self.x_data = x_data
        self.y_data = y_data

        self.width = width
        self.height = height

        # Load and apply theme
        self.theme = Theme.load(theme)

        # Apply chart-type-specific overrides if available
        if chart_type:
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

        # Calculate counts
        self.x_count = (self.x_data, self.x_labels)
        self.y_count = (self.y_data, self.y_labels)

        # Initialize axes
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
            axis_tick_interval=self.axis_tick_interval,
        )

        self.y_axis = YAxis(
            parent=self,
            data=self.y_data,
            labels=y_labels,
            stacked=self.y_stacked,
            zero_index=self.zero_index,
            config=self.theme["h_grid"],
            axis_tick_interval=self.axis_tick_interval,
        )

        # Initialize offsets and values
        self.y_offsets = self.y_data
        self.x_offsets = self.x_data
        self.y_values = self.y_data
        self.x_values = self.x_data

        # Initialize colors
        if not hasattr(self, "_colors"):
            self.colors = self.theme["colors"]

        # Build SVG children
        children = [self.container, self.title]
        if self.render_axes:
            children += [self.y_axis, self.x_axis, self.zero_line]
        children += [self.representation, self.legend]
        self.add_children(*children)

    # =========================================================================
    # Data Properties (with validation)
    # =========================================================================

    @classmethod
    def _validate_data(cls, data: Vector | Vector2D | None) -> Vector2D:
        """Validate and normalize chart data (deprecated: use validation.validate_data)."""
        return validate_data(data)

    @classmethod
    def _validate_attribute_value(cls, name: str, value: float):
        """Validate attribute value (deprecated: use validation.validate_attribute_value)."""
        return validate_attribute_value(name, value)

    @property
    def x_data(self) -> Vector2D:
        return self._x_data

    @x_data.setter
    def x_data(self, data: Vector | Vector2D | None = None) -> None:
        validated_data = validate_data(data)
        self._x_data = validated_data

    @property
    def y_data(self) -> Vector2D:
        return self._y_data

    @y_data.setter
    def y_data(self, data: Vector | Vector2D | None = None) -> None:
        validated_data = validate_data(data)
        self._y_data = validated_data

    @property
    def width(self) -> float:
        return self._width

    @width.setter
    def width(self, width: float) -> None:
        self._width = validate_attribute_value("width", width)

    @property
    def height(self) -> float:
        return self._height

    @height.setter
    def height(self, height: float) -> None:
        self._height = validate_attribute_value("height", height)

    @property
    def h_padding(self) -> float:
        return self._h_padding

    @h_padding.setter
    def h_padding(self, h_padding: float) -> None:
        if h_padding > 1:
            raise Exception("h_padding must be <= 1")
        self._h_padding = validate_attribute_value("h_padding", h_padding)

    @property
    def v_padding(self) -> float:
        return self._v_padding

    @v_padding.setter
    def v_padding(self, v_padding: float) -> None:
        if v_padding > 1:
            raise Exception("v_padding must be <= 1")
        self._v_padding = validate_attribute_value("v_padding", v_padding)

    # =========================================================================
    # Layout Properties (delegated to layout utilities)
    # =========================================================================

    @property
    def plot_width(self) -> float:
        return self.width - (self.left_padding + self.right_padding)

    @property
    def plot_height(self) -> float:
        return self.height - (self.bottom_padding + self.top_padding)

    def get_base_transform(self) -> list:
        """Get base transformation matrix."""

        return [
            translate(-self.h_pad, -self.bottom_padding),
            rotate(STRAIGHT_ANGLE, self.width / 2, self.height / 2),
            scale(-1, 1),
            translate(-self.plot_width, 0),
        ]

    def _apply_stacking(self, y: float, y_offset: float) -> float:
        """Apply y-stacking if enabled."""
        return y + y_offset if self.y_stacked else y

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

    # =========================================================================
    # Padding Calculations (delegated to layout utilities)
    # =========================================================================

    @property
    def left_padding(self) -> float:
        """Calculate left padding for y-axis labels."""
        if not hasattr(self, "y_axis") or self.y_axis is None:
            return self.h_pad
        return calculate_padding_from_labels(self.y_labels, self.h_pad, self.y_axis)

    @property
    def right_padding(self) -> float:
        return self.h_pad

    @property
    def top_padding(self) -> float:
        """Calculate top padding including title."""
        return calculate_top_padding(self.v_pad, self._title)

    @property
    def bottom_padding(self) -> float:
        """Calculate bottom padding including rotated labels."""
        return calculate_bottom_padding(self.v_pad, self.x_label_rotation)

    # =========================================================================
    # Styling Properties
    # =========================================================================

    @property
    def x_label_rotation(self) -> tuple[float, float] | None:
        """Calculate rotation angle for x-axis labels."""
        return calculate_x_label_rotation(self._x_labels, self.x_width)

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
        from charted.utils.helpers import calculate_text_dimensions

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

    # =========================================================================
    # Label Properties
    # =========================================================================

    @property
    def x_labels(self) -> list[MeasuredText] | None:
        return self._x_labels

    @x_labels.setter
    def x_labels(self, x_labels: list[str]) -> None:
        from charted.utils.helpers import calculate_text_dimensions

        if x_labels:
            x_labels = [calculate_text_dimensions(label) for label in x_labels]
        self._x_labels = x_labels

    @property
    def y_labels(self) -> list[MeasuredText] | None:
        return self._y_labels

    @y_labels.setter
    def y_labels(self, y_labels: list[str]) -> None:
        from charted.utils.helpers import calculate_text_dimensions

        if y_labels:
            y_labels = [calculate_text_dimensions(label) for label in y_labels]
        self._y_labels = y_labels

    # =========================================================================
    # Count Properties
    # =========================================================================

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

    # =========================================================================
    # Stacking Properties
    # =========================================================================

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
        from charted.utils.validation import match_data_series

        x_data = match_data_series(x_data, self.y_data)

        data = []
        for arr in x_data:
            row = []
            for x in arr:
                v = self.x_axis.reproject(x)
                row.append(v)
            data.append(row)

        self._x_values = data

    # =========================================================================
    # Rendering Properties
    # =========================================================================

    @property
    def zero_line(self) -> Path:
        """Create zero line for charts with negative values."""
        from charted.utils.rendering import create_zero_line_path

        is_bar_chart = getattr(self, "y_height", None) is not None
        is_xy_line = self._x_data is not None and not is_bar_chart

        return create_zero_line_path(
            x_axis_zero=self.x_axis.zero,
            y_axis_zero=self.y_axis.zero,
            plot_width=self.plot_width,
            plot_height=self.plot_height,
            left_padding=self.left_padding,
            x_stacked=self.x_stacked,
            y_stacked=self.y_stacked,
            x_min=self.x_axis.axis_dimension.min_value,
            y_min=self.y_axis.axis_dimension.min_value,
            is_bar_chart=is_bar_chart,
            is_xy_line=is_xy_line,
        )

    @property
    def representation(self) -> G:
        """Subclass must implement this."""
        raise Exception("representation not implemented for instance of Chart.")

    @property
    def legend(self):
        """Create legend element."""
        from charted.utils.rendering import create_legend

        return create_legend(
            series_names=self.series_names,
            colors=self.colors,
            theme_config=self.theme.get("legend"),
            plot_left=self.left_padding,
            plot_right=self.left_padding + self.plot_width,
            top_padding=self.top_padding,
        )
