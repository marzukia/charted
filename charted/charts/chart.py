"""Base chart class with reduced responsibilities.

Refactored to extract validation, layout, and rendering utilities into
separate modules to address God Class architectural debt (Issue #64).
"""

from charted.charts.axes import XAxis, YAxis
from charted.constants import (
    AXIS_BORDER_COLOR,
    AXIS_BORDER_WIDTH,
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
    REFERENCE_LINE_DASH,
    REFERENCE_LINE_WIDTH,
)
from charted.html.element import ClipPath, Defs, G, Path, Rect, Svg, Text
from charted.themes.core import Theme
from charted.utils.color_manager import ColorManager
from charted.utils.data_model import DataModel
from charted.utils.layout_engine import LayoutEngine
from charted.utils.rendering import (
    generate_html_wrapper,
    generate_markdown_image,
)
from charted.utils.theme_manager import ThemeManager
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
    pad_x_labels: bool = True

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
        title_text = self._title.text if self._title else None
        return generate_markdown_image(self.svg, alt_text, title_text, width)

    def to_html(
        self, style: str = "display: inline-block;", tooltips: bool = False
    ) -> str:
        """Return standalone HTML with embedded SVG.

        Args:
            style: CSS style for the container div.
            tooltips: If True, attach a native SVG ``<title>`` to each data
                mark so browsers show a built-in hover tooltip (no
                JavaScript). File output via ``to_svg()``/``save()`` is never
                affected.

        Returns:
            HTML string with the SVG embedded in a div.
        """
        if not tooltips:
            return generate_html_wrapper(self.svg, style)

        # Regenerate the data-mark representation with <title> children, then
        # restore the inert state so to_svg()/save() stay unchanged.
        self._tooltips = True
        try:
            self._build_children()
            svg = self.html
        finally:
            self._tooltips = False
            self._build_children()
        return generate_html_wrapper(svg, style)

    def _repr_html_(self) -> str:
        """Return HTML wrapper for the chart."""
        return self.to_html()

    def to_base64(self) -> str:
        """Return the SVG as a data URI for inline embedding.

        Returns:
            Data URL string (e.g. 'data:image/svg+xml,<encoded-svg>').
        """
        from urllib.parse import quote

        return f"data:image/svg+xml,{quote(self.svg)}"

    def save(self, path: str, *, scale: int = 2) -> None:
        """Save the chart to a file.

        File format is detected from the extension:
        - .svg: writes raw SVG markup
        - .png: rasterizes via cairosvg (must be installed separately)

        Args:
            path: Destination file path.
            scale: Resolution multiplier for PNG output (default 2x).

        Raises:
            ImportError: If saving as PNG and cairosvg is not installed.
            ValueError: If the file extension is not supported.
        """
        import os

        ext = os.path.splitext(path)[1].lower()

        if ext == ".svg":
            with open(path, "w") as f:
                f.write(self.svg)
        elif ext == ".png":
            try:
                import cairosvg
            except ImportError:
                raise ImportError(
                    "PNG export requires cairosvg. "
                    "Install it with: pip install cairosvg"
                ) from None
            cairosvg.svg2png(bytestring=self.svg.encode(), write_to=path, scale=scale)
        else:
            raise ValueError(
                f"Unsupported file extension '{ext}'. Supported: .svg, .png"
            )

    def style(self, **kwargs) -> "Chart":
        """Fluently apply theme overrides.

        Args:
            **kwargs: Theme attribute overrides (e.g. background_color='#fff',
                      font_family='sans-serif', legend_font_size=12).

        Returns:
            self for chaining.

        Example:
            >>> chart = BarChart(...).style(background_color='#fff', font_size=13)
        """
        from charted.themes.core import Theme

        # Build an override Theme from kwargs
        override = Theme(**{k: v for k, v in kwargs.items() if hasattr(Theme, k)})
        self.theme = self.theme.compose(override)
        return self

    def to_config(self) -> dict:
        """Serialize chart configuration to a dict.

        Returns a dict with all constructor parameters needed to
        recreate the chart, plus theme info.

        Returns:
            Dict suitable for JSON serialization or agent workflows.
        """
        import dataclasses

        cfg = {
            "chart_type": self.__class__.__name__,
            "width": self._width,
            "height": self._height,
            "title": self._title.text if self._title else None,
            "labels": [
                label.text if hasattr(label, "text") else str(label)
                for label in (self.x_labels or [])
            ],
            "series_names": self.series_names,
            "x_stacked": self.x_stacked,
            "zero_index": self.zero_index,
        }
        if self.data_model:
            cfg["x_data"] = self.data_model.x_data
            cfg["y_data"] = self.data_model.y_data
        if self.series_styles:
            cfg["series_styles"] = [
                dataclasses.asdict(s) if dataclasses.is_dataclass(s) else s
                for s in self.series_styles
            ]
        return cfg

    @classmethod
    def from_config(cls, config: dict, **overrides) -> "Chart":
        """Recreate a chart from a config dict.

        Merges ``overrides`` on top of ``config`` so agents can tweak
        individual parameters without rebuilding the whole dict.

        Args:
            config: Dict returned by ``to_config()``.
            **overrides: Override any config key.

        Returns:
            Chart instance of the appropriate subclass.
        """
        import inspect

        from charted.charts import _CHART_CLASSES

        merged = dict(config)
        merged.update(overrides)

        chart_type = merged.pop("chart_type", None)
        cls_map = _CHART_CLASSES()
        chart_cls = cls_map.get(chart_type, cls)
        if chart_cls is None:
            chart_cls = cls

        # Only pass keys the target chart class accepts
        sig = inspect.signature(chart_cls.__init__)
        valid_params = set(sig.parameters.keys()) - {"self"}
        filtered = {k: v for k, v in merged.items() if k in valid_params}

        # Map common aliases: y_data -> data, x_data -> x_data
        if "data" in valid_params and "data" not in filtered:
            if "y_data" in merged:
                filtered["data"] = merged["y_data"]
            elif "x_data" in merged:
                filtered["data"] = merged["x_data"]
        if "y_data" in valid_params and "y_data" not in filtered and "data" in merged:
            filtered["y_data"] = merged["data"]

        return chart_cls(**filtered)

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
        subtitle: str | None = None,
        theme: Theme | None = None,
        chart_type: str | None = None,
        x_label: str | None = None,
        y_label: str | None = None,
        data_labels: list[str] | list[list[str]] | None = None,
        h_lines: list[float] | None = None,
        v_lines: list[float] | None = None,
        reference_lines: list[dict] | None = None,
        colors: list[str] | None = None,
    ):
        super().__init__(
            width=width,
            height=height,
            viewBox=f"0 0 {width} {height}",
        )

        # Validate and normalize data using DataModel
        if not x_data and not y_data:
            from charted.utils.exceptions import NoDataError

            raise NoDataError()

        # Create default x_labels if not provided (for ordinal charts)
        if not x_data and not x_labels:
            # y_data might be Vector (1D) or Vector2D (2D) - handle both
            if y_data and isinstance(y_data[0], list):
                array_len = len(y_data[0])
            elif y_data:
                array_len = len(y_data)
            else:
                array_len = 0
            x_labels = DataModel.create_default_labels(array_len)

        # Initialize DataModel for data validation and normalization
        self.data_model = DataModel(
            x_data=x_data,
            y_data=y_data,
            x_labels=x_labels,
            y_labels=y_labels,
            zero_index=zero_index,
        )

        self.series_names = series_names
        self.series_styles = series_styles
        self.x_stacked = x_stacked
        self.zero_index = zero_index
        self._x_label = x_label
        self._y_label = y_label
        self._data_labels = data_labels
        self._h_lines = h_lines or []
        self._v_lines = v_lines or []

        # Parse reference_lines convenience API into h_lines/v_lines + labels
        self._reference_line_labels: list[dict] = []
        if reference_lines:
            for ref in reference_lines:
                value = ref["value"]
                axis = ref.get("axis", "y")
                label = ref.get("label")
                if axis == "x":
                    self._v_lines.append(value)
                else:
                    self._h_lines.append(value)
                self._reference_line_labels.append(
                    {"value": value, "axis": axis, "label": label}
                )
        # Normalize empty lists to None for _render_reference_lines check
        self._h_lines = self._h_lines or None
        self._v_lines = self._v_lines or None

        # Set internal attributes directly (properties are read-only)
        self._width = width
        self._height = height

        # Load and apply theme using ThemeManager
        self.theme = ThemeManager.load_theme(theme, chart_type)

        # Apply color shorthand: override theme colors if provided
        if colors:
            from dataclasses import replace as dc_replace

            self.theme = dc_replace(self.theme, colors=list(colors))

        # Set internal padding attributes directly (properties are read-only)
        self._h_padding = self.theme.h_padding
        self._v_padding = self.theme.v_padding

        # Set internal title directly (title property is read-only)
        from charted.utils.helpers import calculate_text_dimensions

        if title:
            self._title = calculate_text_dimensions(
                title,
                font=self.theme.title_font_family,
                font_size=self.theme.title_font_size,
            )
        else:
            self._title = None

        # Set subtitle
        if subtitle:
            self._subtitle = calculate_text_dimensions(
                subtitle,
                font=self.theme.title_font_family,
                font_size=self.theme.title_font_size - 4,
            )
        else:
            self._subtitle = None

        # Initialize LayoutEngine for layout calculations
        self.layout = LayoutEngine(
            width=width,
            height=height,
            h_padding=self.h_padding,
            v_padding=self.v_padding,
            x_labels=self.data_model.x_labels,
            y_labels=self.data_model.y_labels,
            title=self._title,
            has_x_axis_label=bool(x_label),
            has_y_axis_label=bool(y_label),
        )

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
            config=self.theme.resolved_grid_color,
            pad_labels=self.pad_x_labels,
        )

        self.y_axis = YAxis(
            parent=self,
            data=self.y_data,
            labels=y_labels,
            stacked=self.y_stacked,
            zero_index=self.zero_index,
            config=self.theme.resolved_grid_color,
        )

        # Initialize internal offsets and values directly (properties are read-only)
        # For ordinal charts (no x_data), generate default x-values [0, 1, 2, ...]
        if self.x_data:
            # XY chart: transform x_data through axis reproject
            self._x_values = [
                [self.x_axis.reproject(x) for x in arr] for arr in self.x_data
            ]

            # Calculate stacking offsets for x-axis (for horizontal bar charts)
            if getattr(self, "x_stacked", False):
                offsets = []
                negative_offsets = [0.0] * self.x_count
                positive_offsets = [0.0] * self.x_count

                for row in self.x_data:
                    row_offsets = []
                    for i, x in enumerate(row):
                        current_offset = 0.0
                        if x >= 0:
                            current_offset = positive_offsets[i]
                            positive_offsets[i] += x
                        elif x < 0:
                            current_offset = negative_offsets[i]
                            negative_offsets[i] -= abs(x)
                        row_offsets.append(current_offset)
                    offsets.append(row_offsets)

                self._x_offsets = [
                    [self.x_axis.reproject(x) for x in arr] for arr in offsets
                ]
            else:
                # Non-stacked: all offsets are zero
                self._x_offsets = [[0.0] * len(arr) for arr in self.x_data]
        else:
            # Ordinal chart: use index-based values transformed through axis
            indices = [float(i) for i in range(self.x_count)]
            x_vals = [self.x_axis.reproject(i) for i in indices]
            # Create one row of x_values per y_data series for multi-series charts
            num_series = len(self.y_data) if self.y_data else 1
            self._x_offsets = [[0.0] * self.x_count] * num_series
            self._x_values = [x_vals] * num_series

        # Transform y_values through y_axis reproject, handling stacking correctly
        data = []
        for arr in self.y_data:
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

        # Calculate stacking offsets (cumulative for stacked charts)
        offsets = []
        negative_offsets = [0.0] * self.y_count
        positive_offsets = [0.0] * self.y_count

        for row in self.y_data:
            row_offsets = []
            for i, y in enumerate(row):
                current_offset = 0.0
                if y >= 0:
                    current_offset = positive_offsets[i]
                    positive_offsets[i] += y
                elif y < 0:
                    current_offset = negative_offsets[i]
                    negative_offsets[i] -= abs(y)
                row_offsets.append(current_offset)
            offsets.append(row_offsets)

        # Transform offsets through y_axis
        self._y_offsets = [[self.y_axis.reproject(y) for y in arr] for arr in offsets]

        # Initialize ColorManager for automatic color cycling
        self._color_manager = ColorManager(colors=self.theme.colors)

        # Initialize colors (set internal variable directly since property is read-only)
        if not hasattr(self, "_colors"):
            self._colors = self.theme.colors

        # Whether data marks should carry native <title> tooltips. Off for
        # file output (to_svg/save); toggled on only by to_html(tooltips=True).
        self._tooltips = False

        self._build_children()

    def _build_children(self) -> None:
        """Assemble the chart's SVG child elements.

        Called once during ``__init__`` and again whenever the tooltip flag
        changes so the data-mark representation can be regenerated.
        """
        # Build SVG children with plot clipping mask
        plot_clip = ClipPath(
            id="plot-clip",
        )
        plot_clip.add_child(
            Rect(
                x=0,
                y=0,
                width=self.plot_width,
                height=self.plot_height,
            )
        )
        defs = Defs()
        defs.add_child(plot_clip)

        children = [self.container, self.title, self.subtitle_element, defs]
        if self.render_axes:
            children += [self.y_axis, self.x_axis, self.zero_line]
        children += [self.representation, self.legend]
        # Add plot border (bottom and left edges) darker than grid
        if self.render_axes:
            lp = self.left_padding
            tp = self.top_padding
            pw = self.plot_width
            ph = self.plot_height
            children.append(
                Path(
                    d=[
                        f"M{lp} {tp} v{ph}",
                        f"M{lp} {tp + ph} h{pw}",
                    ],
                    stroke=AXIS_BORDER_COLOR,
                    stroke_width=AXIS_BORDER_WIDTH,
                    fill="none",
                )
            )
        # Add reference lines (rendered inside the plot area)
        ref_lines = self._render_reference_lines()
        if ref_lines:
            children.append(ref_lines)
        # Add axis title labels
        axis_labels = self._render_axis_labels()
        if axis_labels:
            children.extend(axis_labels)
        self.children = []
        self.add_children(*children)

    # =========================================================================
    # Data Properties (read-only, delegated to DataModel)
    # =========================================================================

    @property
    def x_data(self) -> Vector2D:
        """Get x-axis data from DataModel (read-only)."""
        return self.data_model.x_data

    @property
    def y_data(self) -> Vector2D:
        """Get y-axis data from DataModel (read-only)."""
        return self.data_model.y_data

    @property
    def width(self) -> float:
        """Chart width (read-only)."""
        return self._width

    @property
    def height(self) -> float:
        """Chart height (read-only)."""
        return self._height

    @property
    def h_padding(self) -> float:
        """Horizontal padding fraction (read-only)."""
        return self._h_padding

    @property
    def v_padding(self) -> float:
        """Vertical padding fraction (read-only)."""
        return self._v_padding

    # =========================================================================
    # Layout Properties (delegated to layout utilities)
    # =========================================================================

    @property
    def plot_width(self) -> float:
        """Get plot area width from LayoutEngine."""
        return self.layout.plot_width

    @property
    def plot_height(self) -> float:
        """Get plot area height from LayoutEngine."""
        return self.layout.plot_height

    def get_base_transform(self) -> list:
        """Get base transformation from LayoutEngine."""
        return self.layout.get_base_transform()

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
        if self.x_labels and not self.data_model.x_data:
            return self.x_axis.reproject(1)
        return 0

    # =========================================================================
    # Padding Calculations (delegated to layout utilities)
    # =========================================================================

    @property
    def left_padding(self) -> float:
        """Get left padding from LayoutEngine."""
        return self.layout.left_padding

    @property
    def right_padding(self) -> float:
        """Get right padding from LayoutEngine."""
        return self.layout.right_padding

    @property
    def top_padding(self) -> float:
        """Get top padding from LayoutEngine."""
        return self.layout.top_padding

    @property
    def bottom_padding(self) -> float:
        """Get bottom padding from LayoutEngine."""
        return self.layout.bottom_padding

    @property
    def x_label_rotation(self) -> tuple[float, float] | None:
        """Get x-label rotation from LayoutEngine."""
        return self.layout.x_label_rotation

    @property
    def colors(self) -> list[str]:
        """Get color palette with automatic cycling (read-only)."""
        # Expand palette if more colors are needed and return the list
        return self._color_manager.ensure_palette_size(
            max(len(self.x_values or []), len(self.y_values or []))
        )

    @property
    def title(self) -> MeasuredText | None:
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
            fill=self.theme.title_color,
            font_family=self.theme.title_font_family,
            font_weight="bold",
            font_size=self.theme.title_font_size,
            x=self.width / 2,
            y=self.v_pad / 2,
        )

    @property
    def subtitle_element(self) -> Text | None:
        """Render subtitle as smaller text below the title."""
        if not self._subtitle:
            return None
        subtitle_font_size = self.theme.title_font_size - 4
        # Position below the title (or at top if no title)
        if self._title:
            y_pos = self.v_pad / 2 + self._title.height + subtitle_font_size
        else:
            y_pos = self.v_pad / 2 + subtitle_font_size
        return Text(
            transform=[
                translate(
                    x=-self._subtitle.width / 2,
                    y=self._subtitle.height,
                )
            ],
            text=self._subtitle.text,
            fill=self.theme.title_color,
            font_family=self.theme.title_font_family,
            font_size=subtitle_font_size,
            x=self.width / 2,
            y=y_pos,
        )

    @property
    def v_pad(self) -> float:
        return self.v_padding * self.height

    @property
    def h_pad(self) -> float:
        return self.h_padding * self.width

    @property
    def container(self) -> Path:
        """Create chart background rectangle using theme background color."""
        return Path(
            fill=self.theme.background_color,
            d=Path.get_path(0, 0, self.width, self.height),
        )

    # =========================================================================
    # Label Properties (read-only, delegated to DataModel)
    # =========================================================================

    @property
    def x_labels(self) -> list[MeasuredText] | None:
        """Get x-axis labels from DataModel (read-only)."""
        return self.data_model.x_labels

    @property
    def y_labels(self) -> list[MeasuredText] | None:
        """Get y-axis labels from DataModel (read-only)."""
        return self.data_model.y_labels

    # =========================================================================
    # Count Properties (read-only, delegated to DataModel)
    # =========================================================================

    @property
    def x_count(self) -> int:
        """Get x-axis count from DataModel (read-only)."""
        return self.data_model.x_count

    @property
    def y_count(self) -> int:
        """Get y-axis count from DataModel (read-only)."""
        return self.data_model.y_count

    # =========================================================================
    # Stacking Properties (read-only)
    # =========================================================================

    @property
    def y_offsets(self) -> Vector2D:
        """Get y-offsets (read-only)."""
        return self._y_offsets

    @property
    def x_offsets(self) -> Vector2D | None:
        """Get x-offsets (read-only)."""
        return self._x_offsets

    @property
    def x_width(self) -> float:
        """Get width per x-label."""
        return self.plot_width / self.x_count if self.x_count else 0

    @property
    def y_values(self) -> Vector2D:
        """Get y-values (read-only)."""
        return self._y_values

    @property
    def x_values(self) -> Vector2D:
        """Get x-values (read-only)."""
        return self._x_values

    # =========================================================================
    # Rendering Properties
    # =========================================================================

    @property
    def zero_line(self) -> Path:
        """Create zero line for charts with negative values."""
        from charted.utils.rendering import create_zero_line_path

        is_bar_chart = getattr(self, "y_height", None) is not None
        is_xy_line = self.data_model.x_data is not None and not is_bar_chart

        # For stacked axes, the reproject function uses value/value_range instead of
        # (value - min)/value_range. This causes zero to be at position 0.
        # For zero lines, we need the actual position of value=0 in the axis range.
        x_axis_zero = self.x_axis.zero
        y_axis_zero = self.y_axis.zero

        # If stacked and min < 0, reproject(0) returns 0, but we need (0 - min)/range * length
        if self.x_stacked and self.x_axis.axis_dimension.min_value < 0:
            x_range = (
                self.x_axis.axis_dimension.max_value
                - self.x_axis.axis_dimension.min_value
            )
            x_axis_zero = (
                (0 - self.x_axis.axis_dimension.min_value) / x_range * self.plot_width
            )

        if self.y_stacked and self.y_axis.axis_dimension.min_value < 0:
            y_range = (
                self.y_axis.axis_dimension.max_value
                - self.y_axis.axis_dimension.min_value
            )
            # For Y-axis with negative values, we need to calculate the zero position
            # The Y-axis grid lines are inverted (max at top, min at bottom)
            # But create_zero_line_path expects y_axis_zero from the BOTTOM (like X-axis)
            # So we calculate: plot_height - ((max - 0) / range * plot_height)
            # = (plot_height * range - plot_height * (max - 0)) / range
            # = plot_height * (range - max) / range
            # = plot_height * (-min) / range  (since range = max - min)
            y_axis_zero = (
                self.plot_height * (-self.y_axis.axis_dimension.min_value) / y_range
            )

        stroke_color = (
            self.theme.resolved_axis_border_color if hasattr(self, "theme") else "black"
        )

        return create_zero_line_path(
            x_axis_zero=x_axis_zero,
            y_axis_zero=y_axis_zero,
            plot_width=self.plot_width,
            plot_height=self.plot_height,
            left_padding=self.left_padding,
            top_padding=self.top_padding,
            x_stacked=self.x_stacked,
            y_stacked=self.y_stacked,
            x_min=self.x_axis.axis_dimension.min_value,
            y_min=self.y_axis.axis_dimension.min_value,
            is_bar_chart=is_bar_chart,
            is_xy_line=is_xy_line,
            stroke_color=stroke_color,
        )

    @property
    def representation(self) -> G:
        """Subclass must implement this."""
        raise Exception("representation not implemented for instance of Chart.")

    @property
    def legend(self) -> G | None:
        """Create legend element."""
        from charted.utils.rendering import create_legend

        # Pass legend config as dict or Theme object
        legend_config = {
            "font_size": self.theme.legend_font_size,
            "position": self.theme.legend_position,
            "font_family": self.theme.legend_font_family,
            "font_color": self.theme.legend_font_color,
            "background_color": self.theme.background_color,
        }

        return create_legend(
            series_names=self.series_names,
            colors=self.colors,
            theme_config=legend_config,
            plot_left=self.left_padding,
            plot_right=self.left_padding + self.plot_width,
            top_padding=self.top_padding,
            plot_height=self.plot_height,
        )

    # =========================================================================
    # Introspection
    # =========================================================================

    def describe(self) -> dict:
        """Return a structured dictionary of chart metadata.

        Useful for AI agents that need to reason about a chart they just
        created. Contains chart type, dimensions, series statistics,
        labels, and layout flags.

        Returns:
            Dict with keys: chart_type, title, dimensions, series,
            labels, label_count, series_count, theme, has_negative_values,
            stacked.
        """
        # Determine the raw data series to compute stats over.
        # PieChart stores its real data in _pie_data; base class gets synthetic data.
        # BarChart stores values in x_data (horizontal bars); detect via x_stacked attr.
        if hasattr(self, "_pie_data"):
            raw_series = [self._pie_data]
        elif getattr(self, "x_stacked", False) or (
            self.data_model.x_data and self.__class__.__name__ == "BarChart"
        ):
            raw_series = self.data_model.x_data
        else:
            raw_series = self.data_model.y_data

        # Build per-series stats
        series_info = []
        for i, series_data in enumerate(raw_series):
            name = None
            if self.series_names and i < len(self.series_names):
                name = self.series_names[i]
            count = len(series_data)
            s_min = float(min(series_data))
            s_max = float(max(series_data))
            s_sum = float(sum(series_data))
            s_mean = s_sum / count if count else 0.0
            series_info.append(
                {
                    "name": name,
                    "count": count,
                    "min": s_min,
                    "max": s_max,
                    "mean": s_mean,
                    "sum": s_sum,
                }
            )

        # Determine labels list — check pie labels, then y_labels (BarChart),
        # then x_labels (most chart types)
        if hasattr(self, "_pie_labels") and self._pie_labels:
            labels = [
                lbl.text if hasattr(lbl, "text") else str(lbl)
                for lbl in self._pie_labels
            ]
        elif self.y_labels:
            labels = [
                lbl.text if hasattr(lbl, "text") else str(lbl) for lbl in self.y_labels
            ]
        elif self.x_labels:
            labels = [
                lbl.text if hasattr(lbl, "text") else str(lbl) for lbl in self.x_labels
            ]
        else:
            labels = None

        label_count = (
            len(labels) if labels else (len(raw_series[0]) if raw_series else 0)
        )

        # Detect negative values across all series
        has_negative = any(val < 0 for series_data in raw_series for val in series_data)

        # Stacked flag: either x_stacked (BarChart) or y_stacked (ColumnChart)
        stacked = bool(
            getattr(self, "x_stacked", False) or getattr(self, "y_stacked", False)
        )

        return {
            "chart_type": self.__class__.__name__,
            "title": self._title.text if self._title else None,
            "dimensions": {"width": self._width, "height": self._height},
            "series": series_info,
            "labels": labels,
            "label_count": label_count,
            "series_count": len(raw_series),
            "theme": "default",
            "has_negative_values": has_negative,
            "stacked": stacked,
        }

    # =========================================================================
    # Reference Lines & Axis Labels
    # =========================================================================

    def _render_reference_lines(self) -> G | None:
        """Render horizontal and vertical reference lines in the plot area."""
        if not self._h_lines and not self._v_lines:
            return None

        g = G(
            transform=f"translate({self.left_padding}, {self.top_padding})",
        )

        ref_color = self.theme.resolved_reference_line_color
        label_font_size = max(8, self.theme.title_font_size - 4)
        label_font_family = self.theme.title_font_family

        # Build a lookup for reference line labels
        ref_labels = {}
        for entry in getattr(self, "_reference_line_labels", []):
            ref_labels[(entry["axis"], entry["value"])] = entry.get("label")

        if self._h_lines:
            for val in self._h_lines:
                y = self.plot_height - self.y_axis.reproject(val)
                g.add_child(
                    Path(
                        d=[f"M0 {y} h{self.plot_width}"],
                        stroke=ref_color,
                        stroke_width=REFERENCE_LINE_WIDTH,
                        stroke_dasharray=REFERENCE_LINE_DASH,
                        fill="none",
                    )
                )
                label = ref_labels.get(("y", val))
                if label:
                    g.add_child(
                        Text(
                            text=label,
                            x=self.plot_width - 4,
                            y=y - 4,
                            fill=ref_color,
                            font_size=label_font_size,
                            font_family=label_font_family,
                            text_anchor="end",
                        )
                    )

        if self._v_lines:
            for val in self._v_lines:
                x = self.x_axis.reproject(val)
                g.add_child(
                    Path(
                        d=[f"M{x} 0 v{self.plot_height}"],
                        stroke=ref_color,
                        stroke_width=REFERENCE_LINE_WIDTH,
                        stroke_dasharray=REFERENCE_LINE_DASH,
                        fill="none",
                    )
                )
                label = ref_labels.get(("x", val))
                if label:
                    g.add_child(
                        Text(
                            text=label,
                            x=x + 4,
                            y=label_font_size,
                            fill=ref_color,
                            font_size=label_font_size,
                            font_family=label_font_family,
                            text_anchor="start",
                        )
                    )

        return g

    def _render_axis_labels(self) -> list:
        """Render x-axis and y-axis title labels."""
        elements = []
        font_size = self.theme.title_font_size - 2
        font_family = self.theme.title_font_family
        font_color = self.theme.resolved_axis_title_color

        if self._x_label:
            # Centered below the x-axis, below the tick labels
            x = self.left_padding + self.plot_width / 2
            y = self._height - 2
            elements.append(
                Text(
                    text=self._x_label,
                    x=x,
                    y=y,
                    fill=font_color,
                    font_size=font_size,
                    font_family=font_family,
                    text_anchor="middle",
                )
            )

        if self._y_label:
            # Centered along the y-axis, rotated -90 degrees
            # Position outside (to the left of) the tick labels
            x = font_size
            y = self.top_padding + self.plot_height / 2
            elements.append(
                Text(
                    text=self._y_label,
                    x=x,
                    y=y,
                    fill=font_color,
                    font_size=font_size,
                    font_family=font_family,
                    text_anchor="middle",
                    transform=f"rotate(-90, {x}, {y})",
                )
            )

        return elements

    # =========================================================================
    # Tooltips (opt-in, HTML-only native <title> hover labels)
    # =========================================================================

    def _tooltip_label(self, series_idx: int, point_idx: int) -> str:
        """Build the tooltip text for one data point.

        Format is ``"<label>: <value>"`` when a category label is available,
        otherwise just the value. The series name is prefixed when there is
        more than one series so multi-series marks stay distinguishable.
        """
        value = self._tooltip_value(series_idx, point_idx)
        label = None
        if self.x_labels and point_idx < len(self.x_labels):
            lbl = self.x_labels[point_idx]
            label = lbl.text if hasattr(lbl, "text") else str(lbl)

        series_name = None
        if self.series_names and series_idx < len(self.series_names):
            series_name = self.series_names[series_idx]

        if label is not None:
            return f"{label}: {value}"
        if series_name is not None:
            return f"{series_name}: {value}"
        return str(value)

    def _tooltip_value(self, series_idx: int, point_idx: int):
        """Return the raw data value for a point (overridable per chart)."""
        data = self.y_data
        if series_idx < len(data) and point_idx < len(data[series_idx]):
            value = data[series_idx][point_idx]
            if isinstance(value, float) and value.is_integer():
                return int(value)
            return value
        return ""

    def _tooltip_title(self, series_idx: int, point_idx: int):
        """Return a ``Title`` element for a mark, or None when tooltips off."""
        if not self._tooltips:
            return None
        from charted.html.element import Title

        return Title(self._tooltip_label(series_idx, point_idx))

    @property
    def _data_label_x_offset(self) -> float:
        return 0

    @property
    def _data_labels_use_contrast(self) -> bool:
        return False

    def _render_data_labels(self) -> G | None:
        """Render data labels on data points.

        Returns a G element with text labels positioned at each data point.
        Subclasses call this from their representation property.
        """
        if not self._data_labels:
            return None

        from charted.utils.colors import get_contrast_color

        labels = self._data_labels
        # Normalize to 2D list
        if labels and not isinstance(labels[0], list):
            labels = [labels]

        g = G()
        font_size = max(8, self.theme.title_font_size - 4)
        font_family = self.theme.title_font_family
        font_color = self.theme.resolved_axis_title_color

        for series_idx, label_row in enumerate(labels):
            if series_idx >= len(self.y_values):
                break
            y_vals = self.y_values[series_idx]
            y_offs = self.y_offsets[series_idx]
            x_vals = self.x_values[series_idx]
            series_color = (
                self.colors[series_idx] if series_idx < len(self.colors) else None
            )

            for i, label_text in enumerate(label_row):
                if i >= len(x_vals) or not label_text:
                    continue
                x = x_vals[i] + self.x_offset + self._data_label_x_offset
                y = self._apply_stacking(y_vals[i], y_offs[i])
                label_offset = font_size + 4
                if y_vals[i] < 0:
                    ty = y + label_offset + font_size
                else:
                    ty = y - label_offset
                anchor = "middle"
                # Clamp labels that would go off-chart vertically
                if ty < font_size:
                    ty = y + label_offset + font_size
                if ty > self.plot_height - font_size:
                    ty = y - label_offset
                # Detect if label is inside the bar/column area
                inside = self._data_labels_use_contrast and (
                    (y_vals[i] >= 0 and 0 < ty < y) or (y_vals[i] < 0 and y < ty < 0)
                )
                # Nudge label away from grid lines for breathing room
                grid_margin = font_size * 0.6
                if hasattr(self, "y_axis"):
                    for tick_y in self.y_axis.coordinates:
                        if abs(ty - tick_y) < grid_margin:
                            ty = (
                                tick_y - grid_margin
                                if ty > tick_y
                                else tick_y + grid_margin
                            )
                            break
                # Use contrast-aware color when label is inside a colored area
                fill = font_color
                if inside and series_color:
                    fill = get_contrast_color(series_color)
                # Clamp labels at horizontal edges
                if x > self.plot_width * 0.85:
                    anchor = "end"
                elif x < self.plot_width * 0.15:
                    anchor = "start"
                g.add_child(
                    Text(
                        text=str(label_text),
                        x=x,
                        y=ty,
                        fill=fill,
                        font_size=font_size,
                        font_family=font_family,
                        text_anchor=anchor,
                        transform=f"translate({x},{ty}) scale(1,-1) translate({-x},{-ty})",
                    )
                )

        return g

    @property
    def svg(self) -> str:
        """Get SVG string representation of the chart.

        Returns:
            SVG string with all chart elements rendered.
        """
        return self.html
