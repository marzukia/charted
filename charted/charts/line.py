from __future__ import annotations

from charted.charts.chart import Chart
from charted.constants import DEFAULT_CHART_HEIGHT, DEFAULT_CHART_WIDTH
from charted.html.element import G
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
    ):
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
        )

    @property
    def representation(self) -> G:
        """Generate line chart SVG elements using LineRenderer."""
        renderer = LineRenderer(self)
        return renderer.render()
