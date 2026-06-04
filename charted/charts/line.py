from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from charted.charts.chart import Chart
from charted.constants import DEFAULT_CHART_HEIGHT, DEFAULT_CHART_WIDTH
from charted.html.element import G, Text
from charted.themes.core import Theme
from charted.utils.curves import VALID_CURVES
from charted.utils.line_renderer import LineRenderer
from charted.utils.types import Labels, SeriesStyleConfig, Vector, Vector2D

if TYPE_CHECKING:
    from charted.utils.line_renderer import _LineHost


class LineChart(Chart):
    """Line chart for displaying trends over continuous data.

    Connects data points with straight lines to show changes
    across categories or time. Supports multi-series data with
    optional area fills, markers, and custom styling.

    Args:
        data: Single series (list of values) or multi-series (list of lists)
        x_data: Optional x-axis values (defaults to indices 0, 1, 2, ...)
        labels: Optional x-axis labels
        width, height: Chart dimensions in pixels
        zero_index: Whether to include zero in the data range
        title: Optional chart title
        theme: Optional theme configuration
        series_names: Names for each series (shown in legend)
        series_styles: Per-series style overrides (stroke, marker_shape, etc.)

    Example:
        >>> from charted import LineChart
        >>> # Basic line chart
        >>> chart = LineChart(
        ...     data=[10, 25, 18, 32],
        ...     labels=['Jan', 'Feb', 'Mar', 'Apr']
        ... )
        >>> chart.save('trends.svg')
        >>>
        >>> # Multi-series with area fill
        >>> chart = LineChart(
        ...     data=[[10, 25, 18], [15, 20, 28]],
        ...     labels=['2023', '2024'],
        ...     series_styles=[{'area_fill': True, 'area_fill_opacity': 0.2}]
        ... )
    """

    pad_x_labels: bool = False
    markers: bool = False
    curve: str = "linear"

    # Built-in dash patterns cycled for redundant (dash + colour) encoding when
    # ``dash_cycle=True``. A solid line leads so the first series is unchanged.
    DEFAULT_DASH_CYCLE = ["none", "6,4", "2,3", "8,3,2,3", "1,3"]

    @staticmethod
    def _resolve_dash_cycle(spec: list[str] | bool | None) -> list[str] | None:
        """Normalise the ``dash_cycle`` argument to a list of dashes or None.

        ``None`` / ``False`` disable dash cycling (every series is solid). ``True``
        selects the built-in cycle. A non-empty list is used verbatim. The token
        ``"none"`` means a solid line for that slot.
        """
        if spec is None or spec is False:
            return None
        if spec is True:
            return list(LineChart.DEFAULT_DASH_CYCLE)
        if isinstance(spec, list) and spec:
            return list(spec)
        return None

    def __init__(
        self,
        data: Vector | Vector2D,
        x_data: Vector | Vector2D | None = None,
        labels: Labels | None = None,
        width: float = DEFAULT_CHART_WIDTH,
        height: float = DEFAULT_CHART_HEIGHT,
        zero_index: bool = True,
        title: str | None = None,
        subtitle: str | None = None,
        subtitle_leading: float = 8.0,
        theme: Theme | None = None,
        series_names: list[str] | None = None,
        series_styles: list[SeriesStyleConfig] | None = None,
        markers: bool = False,
        data_labels: list[str] | list[list[str]] | None = None,
        x_label: str | None = None,
        y_label: str | None = None,
        h_lines: list[float] | None = None,
        v_lines: list[float] | None = None,
        annotations: list[Any] | None = None,
        curve: str = "linear",
        x_scale: object | None = None,
        y_scale: object | None = None,
        reference_lines: list[dict[str, Any]] | None = None,
        colors: list[str] | None = None,
        legend: str = "none",
        dash_cycle: list[str] | bool | None = None,
    ):
        if curve not in VALID_CURVES:
            raise ValueError(
                f"Unknown curve {curve!r}. Valid options: {', '.join(VALID_CURVES)}"
            )
        self.markers = markers
        self.curve = curve
        # Redundant dash encoding so series differ by line pattern as well as
        # colour. None (default) keeps every line solid, preserving existing
        # renders. A per-series stroke_dasharray in series_styles always wins.
        self._dash_cycle = self._resolve_dash_cycle(dash_cycle)
        super().__init__(
            y_data=data,
            x_data=x_data,
            x_labels=labels,
            width=width,
            height=height,
            title=title,
            subtitle=subtitle,
            subtitle_leading=subtitle_leading,
            zero_index=zero_index,
            theme=theme,
            series_names=series_names,
            series_styles=series_styles,
            chart_type="line",
            data_labels=data_labels,
            x_label=x_label,
            y_label=y_label,
            h_lines=h_lines,
            v_lines=v_lines,
            annotations=annotations,
            x_scale=x_scale,
            y_scale=y_scale,
            reference_lines=reference_lines,
            colors=colors,
            legend=legend,
        )

    @property
    def x_offset(self) -> float:
        """Line charts use direct x positions, no label-padding offset."""
        return 0.0

    def _series_dasharray(self, series_idx: int) -> str | None:
        """Dash pattern for a series from the cycle, or None for solid.

        Only consulted by the renderer when the series has no explicit
        ``stroke_dasharray`` of its own. Returns None when dash cycling is off
        or the cycle slot is the solid (``"none"``) token.
        """
        cycle = cast("list[str] | None", getattr(self, "_dash_cycle", None))
        if not cycle:
            return None
        dash = cycle[series_idx % len(cycle)]
        if not dash or dash == "none":
            return None
        return dash

    @property
    def representation(self) -> G:
        """Generate line chart SVG elements using LineRenderer."""
        renderer = LineRenderer(cast("_LineHost", self))
        g = renderer.render()

        # Render data labels using the same x positions as the line renderer
        if self._data_labels:
            labels = self._data_labels
            if labels and not isinstance(labels[0], list):
                labels = [labels]

            n = self.x_count
            plot_w = self.plot_width
            if n > 1:
                x_positions = [i / (n - 1) * plot_w for i in range(n)]
            else:
                x_positions = [plot_w / 2]

            font_size = max(8, self.theme.title_font_size - 4)
            font_family = self.theme.title_font_family
            font_color = self.theme.resolved_axis_title_color

            for series_idx, label_row in enumerate(labels):
                if series_idx >= len(self.y_values):
                    break
                y_vals = self.y_values[series_idx]
                y_offs = self.y_offsets[series_idx]

                for i, label_text in enumerate(label_row):
                    if i >= len(x_positions) or not label_text:
                        continue
                    x = x_positions[i] + self.x_offset
                    y = self._apply_stacking(y_vals[i], y_offs[i])
                    label_offset = font_size + 4
                    ty = y - label_offset
                    anchor = "middle"
                    # If label would go below chart or clash with axis at bottom
                    if ty < font_size:
                        ty = y + label_offset + font_size
                    # If label would go above chart
                    if ty > self.plot_height - font_size:
                        ty = y - label_offset
                    # Nudge label away from grid lines
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
                    # Shift labels at left edge rightward to avoid axis clash
                    if x < font_size * 2:
                        anchor = "start"
                    g.add_child(
                        Text(
                            text=str(label_text),
                            x=x,
                            y=ty,
                            fill=font_color,
                            font_size=font_size,
                            font_family=font_family,
                            text_anchor=anchor,
                            transform=f"translate({x},{ty}) scale(1,-1) translate({-x},{-ty})",
                        )
                    )

        return g
