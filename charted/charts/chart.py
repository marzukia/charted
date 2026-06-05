"""Base chart class with reduced responsibilities.

Refactored to extract validation, layout, and rendering utilities into
separate modules to address God Class architectural debt (Issue #64).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, cast

from charted.charts._chart_config import ChartConfigMixin
from charted.charts._chart_introspection import ChartIntrospectionMixin
from charted.charts._chart_output import ChartOutputMixin
from charted.charts._chart_patterns import ChartPatternMixin
from charted.charts._chart_references import ChartReferenceLayerMixin
from charted.charts._chart_scales import ChartScaleMixin
from charted.charts._chart_tooltips import ChartTooltipMixin
from charted.charts._chart_value_labels import ChartValueLabelMixin
from charted.charts.axes import XAxis, YAxis
from charted.constants import (
    AXIS_BORDER_COLOR,
    AXIS_BORDER_WIDTH,
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
)
from charted.html.element import Child, ClipPath, Defs, G, Path, Rect, Svg, Text
from charted.themes.core import Theme
from charted.utils.color_manager import ColorManager
from charted.utils.data_model import DataModel
from charted.utils.layout_engine import LayoutEngine
from charted.utils.series_legend import SeriesLegend
from charted.utils.theme_manager import ThemeManager
from charted.utils.transform import translate
from charted.utils.types import (
    Labels,
    MeasuredText,
    ReferenceLineDict,
    SeriesStyleConfig,
    Vector,
    Vector2D,
)

if TYPE_CHECKING:
    from charted.charts.axes import _AxisParent
    from charted.html.element import Element


class _Annotation(Protocol):
    """Structural type for a chart annotation.

    The three concrete annotation dataclasses (line, box, label) all expose a
    ``render`` method that draws the annotation against a chart; this Protocol
    captures that single contract without importing the concrete classes.
    """

    def render(self, chart: Chart) -> Element: ...


class Chart(
    ChartScaleMixin,
    ChartValueLabelMixin,
    ChartReferenceLayerMixin,
    ChartIntrospectionMixin,
    ChartPatternMixin,
    ChartConfigMixin,
    ChartTooltipMixin,
    ChartOutputMixin,
    SeriesLegend,
    Svg,
):
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

    # Subclasses whose data is not category-aligned (e.g. Gantt stores N tasks
    # as N start/end coordinate pairs, so x_data holds 2N values rather than
    # one per label) set this True to opt out of the generic label-length
    # cross-check in DataModel and validate their own labels instead.
    _skip_label_length_validation: bool = False

    x_stacked: bool = False
    y_stacked: bool = False
    render_axes: bool = True
    pad_x_labels: bool = True

    # Instance attributes assigned in __init__ (declared here so mypy can infer
    # their type at every read site; conditional assignment otherwise leaves the
    # type undeterminable).
    theme: Theme
    _title: MeasuredText | None
    _subtitle: MeasuredText | None

    def style(self, **kwargs: object) -> "Chart":
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

        # Build an override Theme from kwargs. Theme's runtime ``__init__`` takes
        # arbitrary keyword overrides (it replaces the dataclass-synthesised one),
        # so the heterogeneous override mapping is splatted in directly.
        overrides = {k: v for k, v in kwargs.items() if hasattr(Theme, k)}
        override = Theme(**overrides)  # type: ignore[arg-type]
        self.theme = self.theme.compose(override)
        return self

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
        subtitle_leading: float = 8.0,
        theme: Theme | str | dict[str, object] | None = None,
        chart_type: str | None = None,
        x_label: str | None = None,
        y_label: str | None = None,
        data_labels: list[str] | list[list[str]] | None = None,
        h_lines: list[float] | None = None,
        v_lines: list[float] | None = None,
        annotations: list[_Annotation] | None = None,
        x_scale: object | None = None,
        y_scale: object | None = None,
        reference_lines: list[ReferenceLineDict] | None = None,
        colors: list[str] | None = None,
        x_range: tuple[float, float] | None = None,
        y_range: tuple[float, float] | None = None,
        domain_padding: float | None = None,
        value_labels: bool | str | dict[str, object] | None = None,
        legend: str = "none",
        category_label_max_width: float | None = None,
        category_patterns: list[str] | bool | None = None,
    ):
        # Maximum pixel width a category (y-axis) label may occupy before it is
        # wrapped onto multiple lines. ``None`` (the default) keeps the
        # historical single-line behaviour where the left padding grows to fit
        # the longest label. Set this to cap the label gutter and wrap instead
        # of letting long category names eat the plot area.
        self._category_label_max_width = (
            float(category_label_max_width)
            if category_label_max_width is not None
            else None
        )
        # Placement for the shared series legend. ``'none'`` (the default)
        # reserves no layout space and leaves any historical in-plot legend
        # untouched, so existing renders are byte-for-byte preserved.
        self._init_legend(legend)
        # Optional per-category hatch/pattern fills. ``None``/``False`` (the
        # default) keeps flat colour fills so existing renders are unchanged.
        # ``True`` selects the built-in cycle; a list cycles custom patterns.
        # Patterns add a redundant texture channel on top of colour so
        # categories stay distinguishable without relying on hue.
        from charted.utils.patterns import resolve_pattern_cycle

        self._category_patterns = resolve_pattern_cycle(category_patterns)
        super().__init__(
            width=width,
            height=height,
            viewBox=f"0 0 {width} {height}",
        )

        # Optional fixed scale domains / data-domain padding. All default to
        # None, which preserves the historical auto-fit-from-data behaviour.
        self._x_range: tuple[float, float] | None = (
            cast("tuple[float, float]", tuple(x_range)) if x_range is not None else None
        )
        self._y_range: tuple[float, float] | None = (
            cast("tuple[float, float]", tuple(y_range)) if y_range is not None else None
        )
        self._domain_padding = domain_padding

        # Record the requested scale specs (string or Scale instance) for
        # to_config()/describe(); default is linear so existing charts are
        # unchanged.
        self._x_scale_spec = x_scale
        self._y_scale_spec = y_scale

        # Time scales accept dates/datetimes/ISO strings. DataModel only
        # handles numeric data, so convert time x_data to epoch seconds here
        # while remembering the original domain for the scale.
        if self._is_time_scale(x_scale) and x_data is not None:
            x_data = self._normalize_time_data(x_data)

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

        # Initialize DataModel for data validation and normalization. DataModel
        # accepts and normalizes 1D Vector input at runtime; its declared type is
        # Vector2D, so cast the possibly-1D locals to satisfy the checker.
        self.data_model = DataModel(
            x_data=cast("Vector2D | None", x_data),
            y_data=cast("Vector2D | None", y_data),
            x_labels=x_labels,
            y_labels=y_labels,
            zero_index=zero_index,
            skip_label_length_validation=self._skip_label_length_validation,
        )

        self.series_names = series_names
        self.series_styles = series_styles
        self.x_stacked = x_stacked
        self.zero_index = zero_index
        self._x_label = x_label
        self._y_label = y_label
        self._data_labels = data_labels
        self._value_label_config = self._normalize_value_labels(value_labels)
        self._annotations = list(annotations) if annotations else []
        self._h_lines: list[float] | None = h_lines or []
        self._v_lines: list[float] | None = v_lines or []

        # Parse reference_lines convenience API into h_lines/v_lines + labels
        self._reference_line_labels: list[ReferenceLineDict] = []
        if reference_lines:
            from charted.utils.exceptions import ValidationError

            for index, ref in enumerate(reference_lines):
                if "value" not in ref:
                    raise ValidationError(
                        f"reference_lines[{index}] is missing required key "
                        "'value'; each reference line must be a dict with a "
                        "'value' key (and optional 'axis' and 'label')."
                    )
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

        # Extra vertical gap (leading) inserted between the title and the
        # subtitle so the subtitle is not cramped directly under the title.
        self._subtitle_leading = max(0.0, float(subtitle_leading))

        # Set subtitle
        if subtitle:
            self._subtitle = calculate_text_dimensions(
                subtitle,
                font=self.theme.title_font_family,
                font_size=self.theme.title_font_size - 4,
            )
        else:
            self._subtitle = None

        # Subclasses (e.g. ScatterChart) may reserve a band outside the plot
        # for a legend. The defaults leave the layout unchanged.
        legend_layout_position = self._legend_layout_position()
        legend_layout_extent = self._legend_layout_extent()

        # Initialize LayoutEngine for layout calculations
        self.layout = LayoutEngine(
            width=width,
            height=height,
            h_padding=self.h_padding,
            v_padding=self.v_padding,
            x_labels=self.data_model.x_labels,
            y_labels=self.data_model.y_labels,
            title=self._title,
            subtitle=self._subtitle,
            subtitle_leading=self._subtitle_leading,
            has_x_axis_label=bool(x_label),
            has_y_axis_label=bool(y_label),
            legend_position=legend_layout_position,
            legend_extent=legend_layout_extent,
        )

        # Build scale instances from the data domain. None/linear leaves the
        # axis on its default LinearScale path (behaviour unchanged).
        x_scale_inst = self._build_scale(x_scale, self.x_data)
        y_scale_inst = self._build_scale(y_scale, self.y_data)
        self._x_scale = x_scale_inst
        self._y_scale = y_scale_inst

        # Bar/column geometry fills from a zero baseline, which has no meaning
        # on a log scale (no zero) or a time scale. Applying one to the value
        # axis renders garbage (bars collapse to uniform height), so reject it
        # up front. The value axis is Y for column/area/histogram and X for
        # horizontal bar charts.
        self._reject_unsupported_scales(chart_type, x_scale_inst, y_scale_inst)

        # Apply fixed-domain (x_range/y_range) or fractional domain_padding by
        # anchoring the data the axes derive their min/max from. None leaves the
        # axis data untouched, so the auto-fit domain is unchanged.
        value_axis = self._BAR_VALUE_AXIS.get(cast("str", chart_type))
        x_axis_data = self._anchor_axis_data(
            self.x_data,
            self._x_range,
            zero_baseline=(value_axis == "x"),
            stacked=(value_axis == "x" and self.x_stacked),
        )
        y_axis_data = self._anchor_axis_data(
            self.y_data,
            self._y_range,
            zero_baseline=(value_axis == "y"),
            stacked=(value_axis == "y" and self.y_stacked),
        )

        # Build the gridline config. When the theme requests no extra weight,
        # dash pattern, or minor lines, fall back to the plain colour string so
        # existing single-weight renders are unchanged byte-for-byte.
        grid_config = self._build_grid_config()

        # Initialize axes. Chart satisfies the _AxisParent layout contract
        # structurally; the cast bridges its read-only property accessors to the
        # protocol's plain-attribute declarations.
        self.x_axis = XAxis(
            parent=cast("_AxisParent", self),
            data=x_axis_data,
            labels=x_labels,
            stacked=self.x_stacked,
            zero_index=(
                False
                if (x_data is not None and x_labels is not None)
                else self.zero_index
            ),
            config=grid_config,
            pad_labels=self.pad_x_labels,
            scale=x_scale_inst,
        )

        self.y_axis = YAxis(
            parent=cast("_AxisParent", self),
            data=y_axis_data,
            labels=y_labels,
            stacked=self.y_stacked,
            zero_index=self.zero_index,
            config=grid_config,
            scale=y_scale_inst,
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

        # Transform offsets through y_axis. Stacking is undefined on log/time
        # scales (no meaningful zero), so offsets collapse to zero pixels.
        if self._y_scale is not None and self._y_scale.name != "linear":
            self._y_offsets = [[0.0] * len(arr) for arr in offsets]
        else:
            self._y_offsets = [
                [self.y_axis.reproject(y) for y in arr] for arr in offsets
            ]

        # Initialize ColorManager for automatic color cycling. Use the theme's
        # contrast-floor-adjusted palette so washed-out hues are darkened in
        # the high-contrast theme; identical to theme.colors otherwise.
        self._color_manager = ColorManager(colors=self.theme.resolved_colors)

        # Initialize colors (set internal variable directly since property is read-only)
        if not hasattr(self, "_colors"):
            self._colors = self.theme.resolved_colors

        # Whether data marks should carry native <title> tooltips. Off for
        # file output (to_svg/save); toggled on only by to_html(tooltips=True).
        self._tooltips = False

        # Wrap long category (y-axis) labels onto multiple lines so the label
        # gutter stays bounded instead of consuming the plot. No-op unless
        # category_label_max_width was set and a label actually overflows.
        self._apply_category_label_wrapping()

        self._build_children()

    def _apply_category_label_wrapping(self) -> None:
        """Wrap y-axis category labels to ``category_label_max_width``.

        Replaces the measured y-axis labels (used for left-padding) and the
        y-axis' own render labels with wrapped MeasuredText so the full text is
        shown across multiple lines instead of truncated or allowed to expand
        the gutter without bound. Does nothing when no cap is set, there are no
        y-axis labels, or nothing overflows.
        """
        cap = self._category_label_max_width
        if cap is None or not self.data_model.y_labels:
            return

        from charted.utils.helpers import wrap_text_to_width

        wrapped = [
            wrap_text_to_width(label.text, cap) for label in self.data_model.y_labels
        ]
        if not any(w.lines for w in wrapped):
            return

        self.data_model._y_labels = wrapped
        self.layout.y_labels = wrapped
        if getattr(self, "y_axis", None) is not None:
            self.y_axis._labels = wrapped

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
        for pattern in self._pattern_defs():
            defs.add_child(pattern)

        children: list[Child | None] = [
            self.container,
            self.title,
            self.subtitle_element,
            defs,
        ]
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
    # Scale Helpers
    # =========================================================================

    @property
    def x_scale(self) -> str:
        """Name of the x-axis scale ('linear', 'log', or 'time')."""
        return self._x_scale.name if self._x_scale is not None else "linear"

    @property
    def y_scale(self) -> str:
        """Name of the y-axis scale ('linear', 'log', or 'time')."""
        return self._y_scale.name if self._y_scale is not None else "linear"

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

    def get_base_transform(self) -> list[str]:
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
    def title(self) -> Text | None:
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
        # Position below the title (or at top if no title). The configurable
        # leading adds breathing room so the subtitle reads as secondary
        # instead of sitting cramped against the title.
        if self._title:
            y_pos = (
                self.v_pad / 2
                + self._title.height
                + subtitle_font_size
                + self._subtitle_leading
            )
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
    def zero_line(self) -> Path | None:
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

    def _default_legend(self) -> G | None:
        """Create the historical in-plot legend element.

        This is the pre-issue-#60 legend: an in-plot box positioned by the
        theme's ``legend_position``. It is used as the fallback when the new
        placement-aware legend is off (``legend='none'``), so charts that
        previously rendered an in-plot legend keep doing so unchanged.
        """
        from charted.utils.rendering import create_legend

        # Pass legend config as dict or Theme object
        legend_config: dict[str, object] = {
            "font_size": self.theme.legend_font_size,
            "position": self.theme.legend_position,
            "font_family": self.theme.legend_font_family,
            "font_color": self.theme.legend_font_color,
            "background_color": self.theme.background_color,
        }

        return create_legend(
            series_names=cast("list[str]", self.series_names),
            colors=self.colors,
            theme_config=legend_config,
            plot_left=self.left_padding,
            plot_right=self.left_padding + self.plot_width,
            top_padding=self.top_padding,
            plot_height=self.plot_height,
        )

    @property
    def svg(self) -> str:
        """Get SVG string representation of the chart.

        Returns:
            SVG string with all chart elements rendered.
        """
        return self.html
