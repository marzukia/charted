from __future__ import annotations

from charted.charts.chart import Chart
from charted.constants import DEFAULT_CHART_HEIGHT, DEFAULT_CHART_WIDTH
from charted.html.element import G, Text
from charted.themes.core import Theme
from charted.utils.line_renderer import LineRenderer
from charted.utils.series_style import SeriesStyleConfig
from charted.utils.types import Labels, Vector, Vector2D


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

    def __init__(
        self,
        data: Vector | Vector2D,
        x_data: Vector | Vector2D | None = None,
        labels: Labels | None = None,
        width: float = DEFAULT_CHART_WIDTH,
        height: float = DEFAULT_CHART_HEIGHT,
        zero_index: bool = True,
        title: str | None = None,
        theme: Theme | None = None,
        series_names: list[str] | None = None,
        series_styles: list[SeriesStyleConfig] | None = None,
        markers: bool = False,
        data_labels: list[str] | list[list[str]] | None = None,
        x_label: str | None = None,
        y_label: str | None = None,
        h_lines: list[float] | None = None,
        v_lines: list[float] | None = None,
    ):
        self.markers = markers
        super().__init__(
            y_data=data,
            x_data=x_data,
            x_labels=labels,
            width=width,
            height=height,
            title=title,
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
        )

    @property
    def x_offset(self) -> float:
        """Line charts use direct x positions, no label-padding offset."""
        return 0.0

    @property
    def representation(self) -> G:
        """Generate line chart SVG elements using LineRenderer."""
        renderer = LineRenderer(self)
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
                    if hasattr(self, 'y_axis'):
                        for tick_y in self.y_axis.coordinates:
                            if abs(ty - tick_y) < grid_margin:
                                ty = tick_y - grid_margin if ty > tick_y else tick_y + grid_margin
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
