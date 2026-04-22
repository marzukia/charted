from charted.charts.chart import Chart
from charted.html.element import Circle, G, Path
from charted.utils.themes import Theme
from charted.utils.types import Labels, SeriesStyleConfig, Vector, Vector2D


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
        width: float = 500,
        height: float = 500,
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

    def _get_series_style(self, index: int) -> dict:
        """Get effective style for a series, merging theme defaults with overrides."""
        # Start with theme series_style as base
        base_style = self.theme.get("series_style") or {}

        # Apply per-series override if available
        if self.series_styles and index < len(self.series_styles):
            override = self.series_styles[index] or {}
            return {**base_style, **override}

        return base_style

    @property
    def representation(self) -> G:
        g = G(
            opacity=0.8,
            transform=[*self.get_base_transform()],
        )
        for series_idx, (y_values, y_offsets, x_values, color) in enumerate(
            zip(self.y_values, self.y_offsets, self.x_values, self.colors)
        ):
            # Get effective style for this series
            style = self._get_series_style(series_idx)

            # Apply style overrides
            stroke = style.get("stroke") or color
            stroke_width = style.get("stroke_width") or 2
            stroke_dasharray = style.get("stroke_dasharray")
            area_fill = style.get("area_fill", False)
            stroke_opacity = style.get("stroke_opacity")
            area_fill = style.get("area_fill", False)
            area_fill_opacity = style.get("area_fill_opacity", 0.3)
            marker_shape = style.get("marker_shape", "circle")
            marker_size = (
                style.get("marker_size") or self.theme["marker"]["marker_size"]
            )
            series = G(fill="white", stroke=stroke, stroke_width=stroke_width)
            if stroke_dasharray:
                series.attributes["stroke_dasharray"] = stroke_dasharray
            if stroke_opacity:
                series.attributes["stroke_opacity"] = stroke_opacity

            points = []
            path = []

            for i, (x, y, y_offset) in enumerate(zip(x_values, y_values, y_offsets)):
                x += self.x_offset
                y = self._apply_stacking(y, y_offset)
                if i == 0:
                    path.append(f"M{x} {y}")
                else:
                    path.append(f"L{x} {y}")

                # Render marker based on shape
                if marker_shape != "none" and marker_size:
                    if marker_shape == "square":
                        from charted.html.element import Rect

                        half = marker_size / 2
                        marker = Rect(
                            x=x - half,
                            y=y - half,
                            width=marker_size,
                            height=marker_size,
                        )
                    elif marker_shape == "diamond":
                        points_str = (
                            f"{x},{y - marker_size} "
                            f"{x + marker_size},{y} "
                            f"{x},{y + marker_size} "
                            f"{x - marker_size},{y}"
                        )
                        marker = Path(d=f"M{points_str} Z", fill=stroke)
                    else:  # circle
                        marker = Circle(cx=x, cy=y, r=marker_size)
                    points.append(marker)

            line = Path(d=path, fill="none")
            series.add_children(line, *points)

            # Add area fill if enabled
            if area_fill:
                area_path = path.copy()
                if area_path:
                    # Close path to create filled area
                    last_x = x_values[-1] + self.x_offset
                    last_y = y_values[-1] if y_values else 0
                    first_x = x_values[0] + self.x_offset
                    area_path.append(f"L{last_x} {last_y}")
                    area_path.append(f"L{first_x} {last_y}")
                    area_path.append("Z")
                    area = Path(
                        d=" ".join(area_path),
                        fill=stroke,
                        fill_opacity=area_fill_opacity,
                    )
                    g.add_child(area)

            g.add_children(series)

        return g
