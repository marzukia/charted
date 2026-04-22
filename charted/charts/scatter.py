from charted.charts.chart import Chart
from charted.html.element import Circle, G, Path, Rect
from charted.utils.themes import Theme
from charted.utils.types import SeriesStyleConfig, Vector, Vector2D


class ScatterChart(Chart):
    """Scatter plot for displaying relationships between two variables.

    Plots individual data points at (x, y) coordinates to show
    correlations, clusters, or distributions. Supports multi-series
    data with custom marker shapes and sizes.

    Args:
        data: Single series (list of y-values with x=indices) or
              multi-series (list of lists) or list of (x, y) tuples
        x_data: Optional x-coordinates for each point
        labels: Optional series names
        width, height: Chart dimensions in pixels
        zero_index: Whether to include zero in both axes
        title: Optional chart title
        theme: Optional theme configuration
        series_names: Names for each series (shown in legend)
        series_styles: Per-series style overrides (marker_shape, marker_size)

    Example:
        >>> from charted import ScatterChart
        >>> # Basic scatter plot
        >>> chart = ScatterChart(data=[5, 8, 12, 15], x_data=[1, 2, 3, 4])
        >>> chart.save('correlation.svg')
        >>>
        >>> # Multi-series with custom markers
        >>> chart = ScatterChart(
        ...     data=[[5, 8, 12], [7, 10, 14]],
        ...     x_data=[1, 2, 3],
        ...     series_styles=[{'marker_shape': 'circle'}, {'marker_shape': 'square'}]
        ... )
    """

    def __init__(
        self,
        x_data: Vector | Vector2D,
        y_data: Vector | Vector2D,
        width: float = 500,
        height: float = 500,
        title: str | None = None,
        theme: Theme | None = None,
        series_names: list[str] | None = None,
        series_styles: list[SeriesStyleConfig] | None = None,
    ):
        super().__init__(
            y_data=y_data,
            x_data=x_data,
            width=width,
            height=height,
            title=title,
            theme=theme,
            series_names=series_names,
            chart_type="scatter",
            series_styles=series_styles,
        )

    @property
    def representation(self) -> G:
        g = G(
            opacity=0.8,
            transform=[*self.get_base_transform()],
        )
        for series_idx, (y_values, y_offsets, x_values, color) in enumerate(
            zip(self.y_values, self.y_offsets, self.x_values, self.colors),
        ):
            # Apply style overrides from series_styles
            fill = color
            marker_size = 4  # default
            marker_shape = "circle"  # default
            if self.series_styles and series_idx < len(self.series_styles):
                style = self.series_styles[series_idx] or {}
                if style.get("fill"):
                    fill = style["fill"]
                if style.get("marker_size"):
                    marker_size = style["marker_size"]
                if style.get("marker_shape"):
                    marker_shape = style["marker_shape"]

            series = G(fill=fill)
            x_offset = self.x_offset

            for x, y, y_offset in zip(x_values, y_values, y_offsets):
                x += x_offset
                y = self._apply_stacking(y, y_offset)
                # Render marker based on shape
                if marker_shape == "square":
                    half = marker_size / 2
                    series.add_child(
                        Rect(
                            x=x - half,
                            y=y - half,
                            width=marker_size,
                            height=marker_size,
                        )
                    )
                elif marker_shape == "diamond":
                    points_str = (
                        f"{x},{y - marker_size} "
                        f"{x + marker_size},{y} "
                        f"{x},{y + marker_size} "
                        f"{x - marker_size},{y}"
                    )
                    series.add_child(Path(d=f"M{points_str} Z", fill=fill))
                elif marker_shape != "none":  # circle
                    series.add_child(Circle(cx=x, cy=y, r=marker_size))
            g.add_children(series)

        return g
