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
from charted.utils.series_legend import SeriesLegend
from charted.utils.theme_manager import ThemeManager
from charted.utils.transform import translate
from charted.utils.types import (
    Labels,
    MeasuredText,
    SeriesStyleConfig,
    Vector,
    Vector2D,
)


class Chart(SeriesLegend, Svg):
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
            "x_scale": self.x_scale,
            "y_scale": self.y_scale,
        }
        if self.data_model:
            cfg["x_data"] = self.data_model.x_data
            cfg["y_data"] = self.data_model.y_data
        if self.series_styles:
            cfg["series_styles"] = [
                dataclasses.asdict(s) if dataclasses.is_dataclass(s) else s
                for s in self.series_styles
            ]
        if self._h_lines:
            cfg["h_lines"] = list(self._h_lines)
        if self._v_lines:
            cfg["v_lines"] = list(self._v_lines)
        if self._annotations:
            cfg["annotations"] = [
                self._serialize_annotation(a) for a in self._annotations
            ]
        # Line/area charts carry a curve-interpolation setting.
        if hasattr(self, "curve"):
            cfg["curve"] = self.curve
        return cfg

    @staticmethod
    def _serialize_annotation(a):
        """Serialize one annotation to a JSON-friendly dict.

        Tags the dict with its class name and strips private ``_ref_*`` fields
        (used only for legacy reference-line markup) so they neither leak nor
        break reconstruction in ``from_config``.
        """
        import dataclasses

        if not dataclasses.is_dataclass(a):
            return a
        data = {k: v for k, v in dataclasses.asdict(a).items() if not k.startswith("_")}
        return {"type": a.__class__.__name__, **data}

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

        # Reconstruct annotation objects from their serialized dict form.
        # to_config() emits each annotation as {"type": <ClassName>, **asdict(a)}.
        if "annotations" in merged:
            merged["annotations"] = cls._rebuild_annotations(merged["annotations"])

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

    @staticmethod
    def _rebuild_annotations(annotations: list) -> list:
        """Reconstruct annotation objects from their serialized dict form.

        ``to_config()`` serializes each annotation as
        ``{"type": <ClassName>, **dataclasses.asdict(a)}``. This rebuilds the
        concrete annotation object by dispatching on the ``"type"`` field.

        Handles the round-trip quirks:
        - Private ``_ref_*`` fields are stripped so they neither leak into a
          public reconstruction nor break the dataclass constructor.
        - JSON turns tuples into lists, so point/range fields are coerced back
          to tuples.
        """
        from charted.charts.annotations import (
            BoxAnnotation,
            LabelAnnotation,
            LineAnnotation,
        )

        type_map = {
            "LineAnnotation": LineAnnotation,
            "BoxAnnotation": BoxAnnotation,
            "LabelAnnotation": LabelAnnotation,
        }
        # Fields that are (x, y) / (min, max) pairs and must be tuples.
        tuple_fields = {"start", "end", "x_range", "y_range", "point"}

        rebuilt: list = []
        for a in annotations:
            # Already an annotation object (not a serialized dict): keep as-is.
            if not isinstance(a, dict):
                rebuilt.append(a)
                continue

            data = dict(a)
            type_name = data.pop("type", None)
            ann_cls = type_map.get(type_name)
            if ann_cls is None:
                # Unknown type: leave the raw dict untouched rather than guess.
                rebuilt.append(a)
                continue

            # Strip private fields so they don't leak or break reconstruction.
            data = {k: v for k, v in data.items() if not k.startswith("_")}
            # Coerce JSON lists back to tuples for coordinate pairs.
            for key in tuple_fields:
                if key in data and isinstance(data[key], list):
                    data[key] = tuple(data[key])

            rebuilt.append(ann_cls(**data))
        return rebuilt

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
        theme: Theme | str | dict | None = None,
        chart_type: str | None = None,
        x_label: str | None = None,
        y_label: str | None = None,
        data_labels: list[str] | list[list[str]] | None = None,
        h_lines: list[float] | None = None,
        v_lines: list[float] | None = None,
        annotations: list | None = None,
        x_scale: object | None = None,
        y_scale: object | None = None,
        reference_lines: list[dict] | None = None,
        colors: list[str] | None = None,
        x_range: tuple[float, float] | None = None,
        y_range: tuple[float, float] | None = None,
        domain_padding: float | None = None,
        value_labels: bool | str | dict | None = None,
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
        self._x_range = tuple(x_range) if x_range is not None else None
        self._y_range = tuple(y_range) if y_range is not None else None
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

        # Initialize DataModel for data validation and normalization
        self.data_model = DataModel(
            x_data=x_data,
            y_data=y_data,
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
        self._h_lines = h_lines or []
        self._v_lines = v_lines or []

        # Parse reference_lines convenience API into h_lines/v_lines + labels
        self._reference_line_labels: list[dict] = []
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
        value_axis = self._BAR_VALUE_AXIS.get(chart_type)
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

        # Initialize axes
        self.x_axis = XAxis(
            parent=self,
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
            parent=self,
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
    # Colourblind-safe redundancy: contrasting outlines + pattern fills
    # =========================================================================

    def _pattern_color_count(self) -> int:
        """Number of distinct category colours that may need a pattern tile."""
        colors = getattr(self, "colors", None) or []
        return len(colors)

    def _pattern_defs(self) -> list:
        """Build one ``<pattern>`` def per (category, pattern) the chart uses.

        Returns an empty list unless ``category_patterns`` was enabled, so the
        default ``<defs>`` block is byte-for-byte unchanged. One pattern is
        emitted per colour index, drawn in that index's fill colour, so a hatch
        keeps the underlying category colour while adding a texture channel.
        """
        cycle = getattr(self, "_category_patterns", None)
        if not cycle:
            return []
        from charted.utils.patterns import build_pattern

        colors = getattr(self, "colors", None) or []
        defs: list = []
        for idx, color in enumerate(colors):
            name = cycle[idx % len(cycle)]
            defs.append(build_pattern(self._pattern_id(idx), name, color))
        return defs

    def _pattern_id(self, index: int) -> str:
        """Stable id for the pattern tile of category ``index``."""
        return f"chart-pattern-{id(self) & 0xFFFFFF:x}-{index}"

    def _category_fill(self, index: int, color: str) -> str:
        """Return the fill for category ``index``: a pattern url or the colour.

        With patterns disabled (the default) this returns ``color`` unchanged,
        preserving existing renders. With patterns enabled it returns a
        ``url(#...)`` reference to the matching pattern tile.
        """
        if not getattr(self, "_category_patterns", None):
            return color
        return f"url(#{self._pattern_id(index)})"

    def _filled_outline_attrs(self) -> dict:
        """Stroke attributes to apply to a filled shape, or ``{}`` when off.

        Reads the theme's ``filled_shape_outline``; when no outline colour is
        configured (the default and the light/dark presets) this returns an
        empty dict so filled shapes stay unstroked exactly as before. The
        high-contrast preset returns a 1px black outline.
        """
        theme = getattr(self, "theme", None)
        if theme is None:
            return {}
        stroke, width = theme.filled_shape_outline
        if stroke is None:
            return {}
        return {"stroke": stroke, "stroke_width": width}

    # =========================================================================
    # Scale Helpers
    # =========================================================================

    # Chart types whose value axis fills from a zero baseline (bars/columns).
    # log/time scales are unsupported on that axis.
    _BAR_VALUE_AXIS = {
        "column": "y",
        "area": "y",
        "histogram": "y",
        "bar": "x",
    }

    @classmethod
    def _reject_unsupported_scales(cls, chart_type, x_scale_inst, y_scale_inst) -> None:
        """Raise ValueError for log/time scales on a bar/column value axis."""
        value_axis = cls._BAR_VALUE_AXIS.get(chart_type)
        if value_axis is None:
            return
        scale = x_scale_inst if value_axis == "x" else y_scale_inst
        if scale is None:
            return
        name = getattr(scale, "name", "linear")
        if name in ("log", "time"):
            raise ValueError(
                f"{name!r} scale is not supported on the value axis "
                f"({value_axis}) of a {chart_type} chart. Bar/column geometry "
                f"fills from a zero baseline, which a log or time scale has no "
                f"meaning for. Use a linear value axis, or switch to a line or "
                f"scatter chart, which plot points instead of filled bars."
            )

    @staticmethod
    def _is_time_scale(spec: object | None) -> bool:
        from charted.charts.scales import TimeScale

        return spec == "time" or isinstance(spec, TimeScale)

    @staticmethod
    def _normalize_time_data(x_data: Vector | Vector2D) -> Vector | Vector2D:
        """Convert date/datetime/ISO-string x-data into epoch seconds."""
        from charted.charts.scales import _to_epoch

        def conv(seq):
            return [_to_epoch(v) for v in seq]

        if x_data and isinstance(x_data[0], list):
            return [conv(row) for row in x_data]
        return conv(x_data)

    def _anchor_axis_data(
        self,
        data: Vector2D,
        fixed_range: tuple[float, float] | None,
        zero_baseline: bool = False,
        stacked: bool = False,
    ) -> Vector2D:
        """Return axis data anchored to a fixed range or padded domain.

        The linear axes derive their domain (min/max) from the flattened data
        they are given. To let callers control the visible span without adding
        invisible data points, this appends synthetic anchor values so the
        derived domain reaches the requested bounds:

        - ``fixed_range`` (``x_range``/``y_range``): anchor to its exact
          (min, max), replacing the data-derived domain.
        - ``domain_padding``: a fractional pad applied to the data-derived
          (min, max) on each side, e.g. ``0.1`` adds 10% of the data span as
          headroom above and below.

        ``zero_baseline`` marks a value axis whose geometry fills from zero
        (bar/column/area/histogram). For these, padding the side that holds the
        baseline would push the baseline off zero and distort every bar, so the
        pad is only applied away from zero: above the tallest positive value,
        below the lowest negative value, or both when the data straddles zero.
        The zero baseline itself never moves.

        When neither range nor padding is set the original data is returned
        unchanged, so the historical auto-fit domain is byte-for-byte preserved.
        """
        if fixed_range is None and self._domain_padding is None:
            return data
        if not data or not any(row for row in data):
            return data

        # Determine the data-derived extent the axis will see. A stacked value
        # axis aggregates per category (sum of positive series for the top, sum
        # of negative series for the bottom), so the extent must be measured the
        # same way or the headroom is computed against the wrong magnitude.
        count = len(data[0])
        if stacked:
            tops = [0.0] * count
            bottoms = [0.0] * count
            for row in data:
                for i in range(min(count, len(row))):
                    v = row[i]
                    if v < 0:
                        bottoms[i] += v
                    else:
                        tops[i] += v
            d_min, d_max = min(bottoms), max(tops)
        else:
            flat = [v for row in data for v in row]
            d_min, d_max = min(flat), max(flat)

        if fixed_range is not None:
            lo, hi = min(fixed_range), max(fixed_range)
        else:
            span = d_max - d_min
            # A zero span (single distinct value) has no fraction to pad; leave
            # the data alone so the axis keeps its own degenerate-domain logic.
            if span == 0:
                return data
            pad = span * self._domain_padding
            if zero_baseline:
                # Keep the zero baseline pinned: only add headroom on the side
                # away from zero. Positive-only data pads the top, negative-only
                # pads the bottom, straddling data pads both.
                lo = d_min - pad if d_min < 0 else d_min
                hi = d_max + pad if d_max > 0 else d_max
            else:
                lo, hi = d_min - pad, d_max + pad

        if stacked:
            # The axis sums each category, so a short [lo, hi] anchor row would
            # both crash the per-category loop and be summed into a column. Add
            # full-width anchor rows whose top/bottom extremes already account
            # for the existing stacked totals, so the aggregated max reaches hi
            # and min reaches lo without inflating any real category.
            top_row = [0.0] * count
            bot_row = [0.0] * count
            top_i = max(range(count), key=lambda i: tops[i])
            bot_i = min(range(count), key=lambda i: bottoms[i])
            if hi > tops[top_i]:
                top_row[top_i] = hi - tops[top_i]
            if lo < bottoms[bot_i]:
                bot_row[bot_i] = lo - bottoms[bot_i]
            return [*[list(row) for row in data], top_row, bot_row]

        # Append the bounds as an extra series so min()/max() over the flattened
        # data reach lo/hi without altering the plotted points themselves.
        return [*[list(row) for row in data], [lo, hi]]

    def _build_grid_config(self):
        """Assemble the gridline config passed to each axis.

        Returns the plain grid colour string when the theme requests no
        gridline-hierarchy features, keeping existing renders unchanged. When a
        dash pattern, an explicit major width, or minor subdivisions are set,
        returns a dict carrying the major-line attributes plus the minor-grid
        parameters (consumed by the axis grid_lines renderer).
        """
        theme = self.theme
        color = theme.resolved_grid_color
        width = theme.resolved_grid_width
        dasharray = theme.grid_dasharray
        divisions = theme.minor_grid_divisions

        if width is None and dasharray is None and divisions <= 0:
            return color

        config = {
            "stroke": color,
            "stroke_dasharray": dasharray if dasharray is not None else "None",
        }
        if width is not None:
            config["stroke_width"] = width
        if divisions > 0:
            config["minor_divisions"] = divisions
            config["minor_stroke"] = theme.resolved_minor_grid_color
            config["minor_stroke_width"] = theme.resolved_minor_grid_width
        return config

    def _build_scale(self, spec: object | None, data: Vector2D):
        """Construct a Scale instance for an axis from its data domain.

        Returns None for the default linear case so the axis keeps its
        original tick math untouched.
        """
        from charted.charts.scales import Scale, make_scale

        if spec is None or spec == "linear":
            return None
        flat = [v for row in data for v in row] if data else []
        if not flat:
            domain_min, domain_max = 0.0, 1.0
        else:
            domain_min, domain_max = min(flat), max(flat)
        if isinstance(spec, Scale):
            return spec
        return make_scale(spec, domain_min, domain_max)

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

    def _default_legend(self) -> G | None:
        """Create the historical in-plot legend element.

        This is the pre-issue-#60 legend: an in-plot box positioned by the
        theme's ``legend_position``. It is used as the fallback when the new
        placement-aware legend is off (``legend='none'``), so charts that
        previously rendered an in-plot legend keep doing so unchanged.
        """
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
            "scales": {"x": self.x_scale, "y": self.y_scale},
        }

    # =========================================================================
    # Reference Lines & Axis Labels
    # =========================================================================

    def _collect_legacy_reference_lines(self) -> list:
        """Build the legacy ``h_lines`` / ``v_lines`` reference-line layer.

        These are expressed as dashed full-span ``LineAnnotation`` objects so
        there is a single rendering path. They are kept separate from
        user-supplied annotations because reference lines span the full plot
        and are intentionally not clipped, and their markup must stay
        byte-for-byte identical to historical output.
        """
        from charted.charts.annotations import LineAnnotation

        annotations: list = []
        if self._h_lines:
            annotations.extend(LineAnnotation._h_line(v) for v in self._h_lines)
        if self._v_lines:
            annotations.extend(LineAnnotation._v_line(v) for v in self._v_lines)
        return annotations

    def _collect_annotations(self) -> list:
        """Build the full annotation list for this chart.

        Legacy reference lines (``h_lines`` / ``v_lines``) come first, in their
        historical order, followed by any user-supplied annotations.
        """
        return self._collect_legacy_reference_lines() + list(self._annotations)

    def _render_reference_lines(self) -> G | None:
        """Render the annotation layer (reference lines, boxes, labels).

        Annotations are positioned in data coordinates and reprojected through
        the axes, drawn inside the plot-area group. Legacy full-span reference
        lines are drawn directly in the group; user annotations are drawn in a
        nested group clipped to the plot area so out-of-domain boxes/labels
        cannot bleed over the axes or off-canvas.
        """
        legacy = self._collect_legacy_reference_lines()
        user_annotations = list(self._annotations)
        if (
            not legacy
            and not user_annotations
            and not getattr(self, "_reference_line_labels", [])
        ):
            return None

        g = G(
            transform=f"translate({self.left_padding}, {self.top_padding})",
        )
        # Full-span legacy h/v reference lines are drawn directly (unclipped),
        # preserving byte-for-byte historical output.
        for annotation in legacy:
            g.add_child(annotation.render(self))

        # User annotations (boxes, lines, labels) are clipped to the plot area
        # using the same clip path as the scatter point group.
        if user_annotations:
            clipped = G(clip_path="url(#plot-clip)")
            for annotation in user_annotations:
                clipped.add_child(annotation.render(self))
            g.add_child(clipped)

        # Render any reference-line labels supplied via the reference_lines API.
        # The lines themselves are already drawn above (as LineAnnotations); this
        # adds the text callouts next to them.
        ref_labels = {}
        for entry in getattr(self, "_reference_line_labels", []):
            ref_labels[(entry["axis"], entry["value"])] = entry.get("label")

        if ref_labels:
            from charted.utils.helpers import calculate_text_dimensions

            ref_color = self.theme.resolved_reference_line_color
            label_font_size = max(8, self.theme.title_font_size - 4)
            label_font_family = self.theme.title_font_family

            for (axis, value), label in ref_labels.items():
                if not label:
                    continue
                text_w = calculate_text_dimensions(
                    str(label), font=label_font_family, font_size=label_font_size
                ).width
                if axis == "y":
                    # The dashed line spans the full plot width. Anchor the label
                    # to the line's right end, inside the plot, so it reads as a
                    # callout on a continuous line rather than a floating tag next
                    # to a clipped one. Sit it just below the line by default
                    # (there is usually more clear space below a target line than
                    # above it) and nudge it off any gridline it would touch.
                    y = self.plot_height - self.y_axis.reproject(value)
                    label_x = self.plot_width - 4
                    gap = label_font_size * 0.5
                    # Candidate baseline below the line; flip above if that pushes
                    # the text off the bottom of the plot.
                    label_y = y + label_font_size + gap
                    if label_y > self.plot_height - 2:
                        label_y = y - gap
                    # Keep the text band clear of horizontal gridlines.
                    gridlines = [self.plot_height - c for c in self.y_axis.coordinates]
                    text_top = label_y - label_font_size
                    for tick_y in gridlines:
                        if text_top - 2 <= tick_y <= label_y + 2:
                            # Gridline cuts through the text: shift the whole label
                            # below that gridline (or above the line if no room).
                            shifted = tick_y + label_font_size + gap
                            label_y = (
                                shifted if shifted < self.plot_height - 2 else y - gap
                            )
                            break
                    g.add_child(
                        Text(
                            text=label,
                            x=label_x,
                            y=label_y,
                            fill=ref_color,
                            font_size=label_font_size,
                            font_family=label_font_family,
                            text_anchor="end",
                        )
                    )
                else:
                    x = self.x_axis.reproject(value)
                    # Keep the label fully on-canvas: anchor it to the left of the
                    # line when it would otherwise overflow the right edge.
                    if x + 4 + text_w > self.plot_width:
                        label_x = x - 4
                        anchor = "end"
                    else:
                        label_x = x + 4
                        anchor = "start"
                    g.add_child(
                        Text(
                            text=label,
                            x=label_x,
                            y=label_font_size,
                            fill=ref_color,
                            font_size=label_font_size,
                            font_family=label_font_family,
                            text_anchor=anchor,
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

        multi_series = len(self.y_data) > 1

        if label is not None:
            if multi_series:
                prefix = (
                    series_name
                    if series_name is not None
                    else f"Series {series_idx + 1}"
                )
                return f"{prefix} - {label}: {value}"
            return f"{label}: {value}"
        if series_name is not None:
            return f"{series_name}: {value}"
        if multi_series:
            return f"Series {series_idx + 1}: {value}"
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

    # =========================================================================
    # Value labels (opt-in, formatted on-element data annotations)
    # =========================================================================

    @staticmethod
    def _normalize_value_labels(spec: bool | str | dict | None) -> dict | None:
        """Coerce the ``value_labels`` argument into a config dict or None.

        Accepted forms:
        - ``None`` / ``False``: feature off (returns None).
        - ``True``: on with the default ``"number"`` format.
        - a format string (``"number"`` / ``"percent"`` / ``"currency"``).
        - a dict, e.g. ``{"format": "currency", "decimals": 2, "prefix": "US"}``.
          A ``"format"`` key chooses the format; all other keys are passed
          straight through to ``format_value`` as keyword options.

        Foot-gun: the ``"percent"`` shorthand (and the dict form without an
        explicit ``percent_scale``) defaults to ``percent_scale=True``, which
        multiplies the raw value by 100 (``0.4`` -> ``"40%"``). That default
        suits fractional data. If your data is *already* expressed in percent
        units (``40`` meaning 40%), pass the dict form
        ``{"format": "percent", "percent_scale": False}`` so the value renders
        as ``"40%"`` rather than ``"4000%"``. The library cannot infer the
        scale of arbitrary numbers, so the caller must say which one applies.
        """
        if spec is None or spec is False:
            return None
        if spec is True:
            return {"format": "number"}
        if isinstance(spec, str):
            return {"format": spec}
        if isinstance(spec, dict):
            cfg = dict(spec)
            cfg.setdefault("format", "number")
            return cfg
        raise TypeError(
            "value_labels must be None, a bool, a format string, or a dict; "
            f"got {type(spec).__name__}"
        )

    def _value_label_data(self) -> Vector2D:
        """Return the raw per-series values that value labels annotate.

        Defaults to ``y_data``. Charts whose value axis is X (horizontal bars)
        or whose data lives elsewhere (pie) override this.
        """
        return self.y_data

    def _build_value_labels(self) -> list[list[str]] | None:
        """Synthesize formatted label strings from the chart's raw values.

        Returns a 2D list mirroring the value-data shape, or None when value
        labels are disabled. Used by ``_render_data_labels`` as the label source
        when no explicit ``data_labels`` were supplied.
        """
        cfg = self._value_label_config
        if not cfg:
            return None
        from charted.utils.value_format import format_value

        opts = {k: v for k, v in cfg.items() if k != "format"}
        fmt = cfg["format"]
        data = self._value_label_data()
        return [[format_value(v, fmt, **opts) for v in row] for row in data]

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

        When no explicit ``data_labels`` are supplied but ``value_labels`` is
        enabled, the labels are synthesized from the raw data with the requested
        number/percent/currency formatting, and any label whose box would
        collide with an already-placed one is hidden.
        """
        from charted.utils.colors import get_contrast_color

        labels = self._data_labels
        auto_hide = False
        if not labels:
            labels = self._build_value_labels()
            auto_hide = labels is not None
        if not labels:
            return None

        # Normalize to 2D list
        if labels and not isinstance(labels[0], list):
            labels = [labels]

        g = G()
        font_size = max(8, self.theme.title_font_size - 4)
        font_family = self.theme.title_font_family
        font_color = self.theme.resolved_data_label_color

        # Track placed label boxes (in plot coordinates) so value labels can be
        # auto-hidden when they would collide with an already-placed label.
        placed_boxes: list[tuple[float, float, float, float]] = []

        from charted.utils.helpers import calculate_text_dimensions

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
                # Auto-hide synthesized value labels that would overlap an
                # already-placed one. Explicit data_labels are left untouched so
                # historical renders stay byte-for-byte identical.
                if auto_hide:
                    tw = calculate_text_dimensions(
                        str(label_text), font=font_family, font_size=font_size
                    ).width
                    box = (
                        x - tw / 2,
                        ty - font_size / 2,
                        x + tw / 2,
                        ty + font_size / 2,
                    )
                    if any(
                        box[0] < pb[2]
                        and box[2] > pb[0]
                        and box[1] < pb[3]
                        and box[3] > pb[1]
                        for pb in placed_boxes
                    ):
                        continue
                    placed_boxes.append(box)
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
