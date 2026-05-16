"""Configuration objects for chart constructors.

This module provides dataclass-based configuration objects to reduce
excessive constructor parameters across all chart classes. It addresses
Issue #70 (Long functions & excessive parameters) and Issue #76
(Design config object pattern).

Example:
    >>> from charted import BarChart
    >>> from charted.chart_config import BarChartConfig
    >>>
    >>> config = BarChartConfig(
    ...     width=600,
    ...     height=400,
    ...     title="Sales by Quarter",
    ...     bar_gap=0.3
    ... )
    >>> chart = BarChart(data=[120, 180, 210], config=config, labels=['Q1', 'Q2', 'Q3'])
"""

from __future__ import annotations

import dataclasses
from typing import Self

from charted.utils.themes import Theme
from charted.utils.types import Labels, SeriesStyleConfig, Vector


@dataclasses.dataclass
class ChartConfig:
    """Base configuration for all chart types.

    Provides common settings for chart appearance and behavior.
    All chart-specific configs inherit from this class.

    Attributes:
        width: Chart width in pixels (default: 500)
        height: Chart height in pixels (default: 500)
        title: Optional chart title
        theme: Theme name or Theme instance
        series_names: Names for each series (shown in legend)
        series_styles: Per-series style overrides
        render_axes: Whether to draw axes and grid lines
        zero_index: Whether to include zero in data range

    Example:
        >>> config = ChartConfig(width=800, height=600, title="My Chart")
    """

    # Appearance settings
    width: float = 500
    height: float = 500
    title: str | None = None
    theme: Theme | str | None = None

    # Data styling
    series_names: list[str] | None = None
    series_styles: list[SeriesStyleConfig] | None = None

    # Behavior flags
    render_axes: bool = True
    zero_index: bool = True

    def to_dict(self) -> dict:
        """Convert config to dictionary for serialization.

        Returns:
            Dictionary representation of the config.

        Example:
            >>> config = ChartConfig(width=600, title="Test")
            >>> config.to_dict()
            {'width': 600, 'height': 500, 'title': 'Test', ...}
        """
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create config from dictionary.

        Args:
            data: Dictionary with config values.

        Returns:
            New config instance.

        Example:
            >>> config = ChartConfig.from_dict({'width': 600, 'title': 'Test'})
        """
        valid_fields = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in valid_fields})

    def update(self, **kwargs) -> Self:
        """Update config with new values and return self.

        Args:
            **kwargs: Field names and values to update.

        Returns:
            Self for method chaining.

        Example:
            >>> config = ChartConfig().update(width=600, title="Test")
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

    def copy(self) -> Self:
        """Create a shallow copy of the config.

        Returns:
            New config instance with same values.

        Example:
            >>> config1 = ChartConfig(width=600)
            >>> config2 = config1.copy()
            >>> config2.width = 800  # Doesn't affect config1
        """
        return dataclasses.replace(self)


@dataclasses.dataclass
class BarChartConfig(ChartConfig):
    """Configuration for horizontal bar charts.

    Extends ChartConfig with bar-specific settings.

    Attributes:
        bar_gap: Gap between bars as ratio of bar height (default: 0.50)
        x_stacked: If True, stack bars horizontally (default: False)
        labels: Category labels for the y-axis

    Example:
        >>> config = BarChartConfig(
        ...     width=600,
        ...     bar_gap=0.3,
        ...     labels=['Q1', 'Q2', 'Q3'],
        ...     x_stacked=True
        ... )
    """

    # Bar-specific settings
    bar_gap: float = 0.50
    x_stacked: bool = False

    # Labels (bar charts use y-axis for categories)
    labels: Labels | None = None


@dataclasses.dataclass
class ColumnChartConfig(ChartConfig):
    """Configuration for vertical column charts.

    Extends ChartConfig with column-specific settings.

    Attributes:
        column_gap: Gap between columns as ratio of column width (default: 0.20)
        y_stacked: If True, stack columns vertically (default: True)
        labels: Category labels for the x-axis

    Example:
        >>> config = ColumnChartConfig(
        ...     width=600,
        ...     column_gap=0.15,
        ...     labels=['Jan', 'Feb', 'Mar'],
        ...     y_stacked=False
        ... )
    """

    # Column-specific settings
    column_gap: float = 0.20
    y_stacked: bool = True

    # Labels
    labels: Labels | None = None


@dataclasses.dataclass
class LineChartConfig(ChartConfig):
    """Configuration for line charts.

    Extends ChartConfig with line-specific settings.

    Attributes:
        line_style: Line style - 'solid', 'dashed', or 'dotted' (default: 'solid')
        marker_shape: Marker shape - 'circle', 'square', 'diamond', or 'none' (default: 'circle')
        marker_size: Size of markers in pixels (default: 4.0)
        area_fill: Whether to fill area under line (default: False)
        area_fill_opacity: Opacity of area fill (default: 0.3)
        x_data: Optional x-axis values
        labels: Optional x-axis labels

    Example:
        >>> config = LineChartConfig(
        ...     marker_shape='square',
        ...     area_fill=True,
        ...     area_fill_opacity=0.2,
        ...     labels=['Jan', 'Feb', 'Mar']
        ... )
    """

    # Line-specific settings
    line_style: str = "solid"
    marker_shape: str = "circle"
    marker_size: float = 4.0
    area_fill: bool = False
    area_fill_opacity: float = 0.3

    # Data
    x_data: Vector | None = None
    labels: Labels | None = None


@dataclasses.dataclass
class PieChartConfig(ChartConfig):
    """Configuration for pie/doughnut charts.

    Extends ChartConfig with pie-specific settings.

    Attributes:
        inner_radius: Ratio (0.0-1.0) for doughnut hole; 0 = regular pie (default: 0.0)
        explode: Single value or list to offset slices from center in pixels (default: 0.0)
        start_angle: Starting angle in degrees, 0 = top, clockwise (default: 0.0)
        labels: Optional labels for each slice

    Example:
        >>> # Doughnut chart with exploded slice
        >>> config = PieChartConfig(
        ...     inner_radius=0.5,
        ...     explode=[10, 0, 0, 0],
        ...     start_angle=45
        ... )
    """

    def __post_init__(self):
        """Validate pie-specific settings."""
        if not 0 <= self.inner_radius < 1:
            raise ValueError("inner_radius must be between 0 (inclusive) and 1 (exclusive)")

    # Pie-specific settings
    inner_radius: float = 0.0
    explode: float | list[float] = 0.0
    start_angle: float = 0.0

    # Labels
    labels: Labels | None = None


@dataclasses.dataclass
class ScatterChartConfig(ChartConfig):
    """Configuration for scatter plots.

    Extends ChartConfig with scatter-specific settings.

    Attributes:
        marker_shape: Marker shape - 'circle', 'square', 'diamond', or 'none' (default: 'circle')
        marker_size: Size of markers in pixels (default: 4.0)
        x_data: Optional x-coordinates for each point

    Example:
        >>> config = ScatterChartConfig(
        ...     marker_shape='square',
        ...     marker_size=6.0
        ... )
    """

    # Scatter-specific settings
    marker_shape: str = "circle"
    marker_size: float = 4.0

    # Data
    x_data: Vector | None = None


@dataclasses.dataclass
class RadarChartConfig(ChartConfig):
    """Configuration for radar/spider charts.

    Extends ChartConfig with radar-specific settings.

    Attributes:
        radius: Chart radius as ratio of min(width, height) (default: 0.45)
        grid_levels: Number of concentric grid circles (default: 5)
        show_axis_labels: Whether to display axis labels (default: True)
        label_offset: Distance from grid edge for labels in pixels (default: 20.0)
        labels: Labels for each axis (required)

    Example:
        >>> config = RadarChartConfig(
        ...     radius=0.5,
        ...     grid_levels=4,
        ...     labels=['Speed', 'Power', 'Endurance']
        ... )
    """

    def __post_init__(self):
        """Validate radar-specific settings."""
        if not 0 < self.radius <= 1:
            raise ValueError("radius must be between 0 (exclusive) and 1 (inclusive)")
        if self.grid_levels < 1:
            raise ValueError("grid_levels must be at least 1")
        if not self.labels:
            raise ValueError("labels are required for RadarChartConfig")

    # Radar-specific settings
    radius: float = 0.45
    grid_levels: int = 5
    show_axis_labels: bool = True
    label_offset: float = 20.0

    # Labels (required for radar)
    labels: Labels


# Type alias for any chart config
ChartConfigType = (
    BarChartConfig
    | ColumnChartConfig
    | LineChartConfig
    | PieChartConfig
    | ScatterChartConfig
    | RadarChartConfig
    | ChartConfig
)
