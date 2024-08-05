from __future__ import annotations

from charted.charts.chart import Chart
from charted.constants import (
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
)
from charted.html.element import G
from charted.themes.core import Theme
from charted.utils.defaults import DEFAULT_COLORS
from charted.utils.radar_renderer import RadarRenderer
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
        width: float = DEFAULT_CHART_WIDTH,
        height: float = DEFAULT_CHART_HEIGHT,
        title: str | None = None,
        theme: Theme | None = None,
        series_names: list[str] | None = None,
        series_styles: list[SeriesStyleConfig] | None = None,
        radius: float = 0.45,
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

        if not data or (isinstance(data, list) and len(data) == 0):
            raise ValueError("Data cannot be empty")

        # Normalize data to list of lists (multi-series format)
        # Handle tuples and other sequence types, not just lists
        if isinstance(data, (list, tuple)) and len(data) > 0:
            if isinstance(data[0], (list, tuple)):
                # Multi-series: convert all inner sequences to lists
                data = [list(s) for s in data]
            else:
                # Single series: wrap in list
                data = [list(data)]
        else:
            raise ValueError("Data cannot be empty")

        # axis_count must match len(labels) for consistency
        if axis_count is not None and axis_count != len(labels):
            raise ValueError(
                f"axis_count ({axis_count}) must match len(labels) ({len(labels)})"
            )
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
        self._series_data = (
            data  # Must set before super().__init__ calls representation
        )
        self.colors = data  # Must set before super().__init__ calls representation

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
        # Set colors after super().__init__() to override base class default
        self.colors = data

    @property
    def colors(self) -> list[str]:
        return self._colors

    @colors.setter
    def colors(self, data: Vector | Vector2D) -> None:
        """Generate colors for series."""
        if not data or (isinstance(data, list) and len(data) == 0):
            self._colors = []
            return
        n_series = len(data) if isinstance(data[0], list) else 1
        self._colors = list(DEFAULT_COLORS[:n_series])
        while len(self._colors) < n_series:
            self._colors.append(DEFAULT_COLORS[len(self._colors) % len(DEFAULT_COLORS)])

    def get_base_transform(self) -> list:
        """Radar charts use polar coordinates — no base transform needed."""
        return []

    @property
    def representation(self) -> G:
        """Generate radar chart SVG elements using RadarRenderer."""
        renderer = RadarRenderer(self)
        return renderer.render()
