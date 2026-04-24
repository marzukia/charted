from __future__ import annotations

import math

from charted.charts.chart import Chart
from charted.html.element import Circle, G, Path, Text

from charted.utils.defaults import DEFAULT_COLORS
from charted.utils.themes import Theme
from charted.utils.types import Labels, SeriesStyleConfig, Vector, Vector2D


class RadarChart(Chart):
    """Radar chart (spider chart) for displaying multivariate data.

    Renders data on a two-dimensional chart in the form of a polygon
    with vertices on axes radiating from a central point. Each axis
    represents a variable, with concentric grid lines showing scale.
    Supports multi-series data with customizable axis count and labels.

    Args:
        data: Single series (list of values) or multi-series (list of lists)
        labels: Labels for each axis (one per data point in series)
        width, height: Chart dimensions in pixels
        title: Optional chart title
        theme: Optional theme configuration
        series_names: Names for each series (shown in legend)
        series_styles: Per-series style overrides (stroke, fill, etc.)
        radius: Chart radius as ratio of min(width, height) (default 0.35)
        axis_count: Number of axes (defaults to len(labels))
        grid_levels: Number of concentric grid circles (default 5)
        show_axis_labels: Whether to display axis labels (default True)
        label_offset: Distance from grid edge for labels (default 20)

    Example:
        >>> from charted import RadarChart
        >>> # Basic radar chart
        >>> chart = RadarChart(
        ...     data=[20, 35, 30, 45, 25],
        ...     labels=['Speed', 'Power', 'Endurance', 'Defense', 'Skill']
        ... )
        >>> chart.save('character_stats.svg')
        >>>
        >>> # Multi-series comparison
        >>> chart = RadarChart(
        ...     data=[[20, 35, 30, 45, 25], [30, 25, 40, 35, 30]],
        ...     labels=['Speed', 'Power', 'Endurance', 'Defense', 'Skill'],
        ...     series_names=['Player A', 'Player B']
        ... )
    """

    render_axes = False  # Radar charts use polar grid, not Cartesian axes

    def __init__(
        self,
        data: Vector | Vector2D,
        labels: Labels,
        width: float = 500,
        height: float = 500,
        title: str | None = None,
        theme: Theme | None = None,
        series_names: list[str] | None = None,
        series_styles: list[SeriesStyleConfig] | None = None,
        radius: float = 0.35,
        axis_count: int | None = None,
        grid_levels: int = 5,
        show_axis_labels: bool = True,
        label_offset: float = 20,
    ):
        """Initialize radar chart.

        Args:
            data: Single series (list of values) or multi-series (list of lists)
            labels: Labels for each axis (one per data point in series)
            width, height: Chart dimensions in pixels
            title: Optional chart title
            theme: Optional theme configuration
            series_names: Names for each series (shown in legend)
            series_styles: Per-series style overrides (stroke, fill, etc.)
            radius: Chart radius as ratio of min(width, height) (default 0.35)
            axis_count: Number of axes (defaults to len(labels))
            grid_levels: Number of concentric grid circles (default 5)
            show_axis_labels: Whether to display axis labels (default True)
            label_offset: Distance from grid edge for labels (default 20)
        """
        # Validate inputs
        if not labels or len(labels) == 0:
            raise ValueError("Labels cannot be empty")

        # Normalize data to list of lists (multi-series format)
        if not isinstance(data[0], list):
            data = [data]  # Single series

        if axis_count is None:
            axis_count = len(labels)

        if any(len(series) != axis_count for series in data):
            raise ValueError(
                f"All series must have {axis_count} values matching labels"
            )

        self._radar_labels = list(labels)
        self.radius = radius
        self.grid_levels = grid_levels
        self.show_axis_labels = show_axis_labels
        self.label_offset = label_offset

        # Create synthetic x_data and y_data for Chart base class compatibility
        x_data = [[i for i in range(axis_count)] for _ in data]
        y_data = data

        super().__init__(
            width=width,
            height=height,
            x_data=x_data,
            y_data=y_data,
            x_labels=labels,
            title=title,
            zero_index=True,
            theme=theme,
            chart_type="radar",
            series_styles=series_styles,
            series_names=series_names,
        )

    @property
    def colors(self) -> list[str]:
        return self._colors

    @colors.setter
    def colors(self, data: Vector | Vector2D) -> None:
        """Generate colors for series."""
        n_series = len(data) if isinstance(data[0], list) else 1
        self._colors = list(DEFAULT_COLORS[:n_series])
        while len(self._colors) < n_series:
            self._colors.append(DEFAULT_COLORS[len(self._colors) % len(DEFAULT_COLORS)])

    def _get_angle(self, index: int) -> float:
        """Get angle in degrees for axis index (0 = top, clockwise)."""
        return (index * 360 / len(self._radar_labels)) - 90

    def _polar_to_cartesian(
        self, cx: float, cy: float, radius: float, angle_deg: float
    ) -> tuple[float, float]:
        """Convert polar coordinates to Cartesian."""
        angle_rad = math.radians(angle_deg)
        x = cx + radius * math.cos(angle_rad)
        y = cy - radius * math.sin(angle_rad)  # negate y for SVG coordinate system
        return x, y

    def _get_grid_radius(self, level: int) -> float:
        """Get radius for grid level (0 = center, max = outer)."""
        return (level + 1) * (self._max_radius / self.grid_levels)

    def _get_data_point(
        self, cx: float, cy: float, axis_index: int, value: float, max_value: float
    ) -> tuple[float, float]:
        """Get cartesian coordinates for a data point."""
        if max_value == 0:
            radius = 0
        else:
            radius = (value / max_value) * self._max_radius
        angle = self._get_angle(axis_index)
        return self._polar_to_cartesian(cx, cy, radius, angle)

    @property
    def representation(self) -> G:
        """Generate radar chart SVG elements."""
        g = G(
            opacity=0.8,
            transform=[*self.get_base_transform()],
        )

        # Calculate chart center and max radius
        cx = self.width / 2
        cy = self.height / 2
        min_dim = min(self.width, self.height)
        self._max_radius = (min_dim / 2 - 40) * self.radius

        # Render concentric grid circles
        grid_color = self.theme.get("grid_color", "#e0e0e0")
        grid_width = self.theme.get("grid_width", 1)
        for level in range(self.grid_levels):
            radius = self._get_grid_radius(level)
            circle = Circle(
                cx=cx,
                cy=cy,
                r=radius,
                fill="none",
                stroke=grid_color,
                stroke_width=grid_width,
            )
            g.add_child(circle)

        # Render axis spokes
        for i, label in enumerate(self._radar_labels):
            angle = self._get_angle(i)
            end_x, end_y = self._polar_to_cartesian(cx, cy, self._max_radius, angle)
            # Render axis spokes using Path
            spoke = Path(
                d=f"M{cx} {cy} L{end_x} {end_y}",
                stroke=grid_color,
                stroke_width=grid_width,
            )
            g.add_child(spoke)

            # Render axis labels
            if self.show_axis_labels:
                label_radius = self._max_radius + self.label_offset
                label_x, label_y = self._polar_to_cartesian(cx, cy, label_radius, angle)

                # Adjust text anchor based on angle
                if -90 <= angle <= 90:  # Right side: start anchor
                    text_anchor = "start"
                    x_align = label_x + 5
                else:  # Left side: end anchor
                    text_anchor = "end"
                    x_align = label_x - 5

                label_text = Text(
                    x=x_align,
                    y=label_y + 4,  # Small y offset for baseline
                    text=label,
                    fill=self.theme.get("text_color", "#333"),
                    font_size=self.theme.get("font_size", 12),
                    text_anchor=text_anchor,
                )
                g.add_child(label_text)

        # Render data series
        for series_idx, (y_values, color) in enumerate(zip(self.y_values, self.colors)):
            # Get effective style for this series
            style = {}
            if self.series_styles and series_idx < len(self.series_styles):
                style = self.series_styles[series_idx] or {}

            stroke = style.get("stroke") or color
            stroke_width = style.get("stroke_width", 2)
            fill = style.get("fill")
            fill_opacity = style.get("fill_opacity", 0.2)
            marker_shape = style.get("marker_shape", "circle")
            marker_size = style.get("marker_size", 4)

            # Calculate max value for scaling
            max_value = max(max(abs(v) for v in series) for series in self.y_values)
            if max_value == 0:
                max_value = 1

            # Build polygon path
            points = []
            for i, value in enumerate(y_values):
                x, y = self._get_data_point(cx, cy, i, value, max_value)
                points.append((x, y))

            # Create polygon
            if points:
                points_str = " ".join(f"{x},{y}" for x, y in points)
                polygon = Path(
                    d=f"M{points_str} Z",
                    fill=fill or stroke,
                    fill_opacity=fill_opacity,
                    stroke=stroke,
                    stroke_width=stroke_width,
                )
                g.add_child(polygon)

                # Render markers
                for i, (x, y) in enumerate(points):
                    if marker_shape == "circle":
                        marker = Circle(
                            cx=x,
                            cy=y,
                            r=marker_size,
                            fill=stroke,
                            stroke="white",
                            stroke_width=1,
                        )
                    elif marker_shape == "square":
                        from charted.html.element import Rect

                        half = marker_size
                        marker = Rect(
                            x=x - half,
                            y=y - half,
                            width=marker_size * 2,
                            height=marker_size * 2,
                            fill=stroke,
                            stroke="white",
                            stroke_width=1,
                        )
                    else:  # diamond
                        points_str = (
                            f"{x},{y - marker_size} "
                            f"{x + marker_size},{y} "
                            f"{x},{y + marker_size} "
                            f"{x - marker_size},{y}"
                        )
                        marker = Path(
                            d=f"M{points_str} Z",
                            fill=stroke,
                            stroke="white",
                            stroke_width=1,
                        )
                    g.add_child(marker)

        return g
