from __future__ import annotations

from charted.charts.chart import Chart
from charted.html.element import G, Path
from charted.utils.themes import Theme
from charted.utils.types import Labels, Vector, Vector2D


class BarChart(Chart):
    """Horizontal bar chart with support for multiple series and negative values.

    Args:
        data: Single or multiple series of bar values.
        labels: Optional labels for y-axis (categories).
        bar_gap: Gap between bars as a fraction of bar height (default 0.50).
        width: Total chart width in pixels.
        height: Total chart height in pixels.
        zero_index: Whether to start index at 0 for automatic label generation.
        title: Optional chart title.
        theme: Optional custom theme.
    """

    def __init__(
        self,
        data: Vector | Vector2D,
        labels: Labels = None,
        bar_gap: float = 0.50,
        width: float = 500,
        height: float = 500,
        zero_index: bool = True,
        title: str | None = None,
        theme: Theme | None = None,
    ):
        self.bar_gap = bar_gap
        if not isinstance(data, list) or not data or isinstance(data[0], (int, float)):
            x_data = [data]
        else:
            x_data = data

        if not x_data or not x_data[0]:
            raise ValueError("No data was provided to the BarChart element.")

        num_bars = len(x_data[0]) if x_data else 0
        num_series = len(x_data) if x_data else 0
        if num_bars <= 1:
            y_data = [[0, 1] for _ in range(num_series)] if num_series > 0 else [[0, 1]]
        else:
            y_data = [[i for i in range(num_bars)] for _ in range(num_series)]

        super().__init__(
            width=width,
            height=height,
            x_data=x_data,
            y_data=y_data,
            y_labels=labels,
            title=title,
            zero_index=zero_index,
            theme=theme,
        )

    @property
    def y_height(self) -> float:
        """Calculate bar height based on available space and gap settings.

        For n bars with gaps between them, the total space is:
        n * bar_height + (n-1) * gap = plot_height
        """
        return self.plot_height / (self.y_count + (self.y_count + 1) * self.bar_gap)

    def get_base_transform(self):
        """Return base transform for the chart."""
        return []

    @property
    def representation(self) -> G:
        """Generate SVG representation of the bar chart.

        Returns:
            G element containing all bar paths with proper transforms.
        """
        # Bar thickness (vertical dimension of each horizontal bar)
        bar_thickness = self.y_height
        gap = bar_thickness * self.bar_gap

        # Start with gap offset at top for centering
        start_y = gap

        # Bars start at x=0 (left edge of plot area)
        x_offset = self.left_padding

        g = G(
            opacity="0.8",
            transform=f"translate({x_offset}, {self.top_padding})",
        )
        for x_values_series, y_values_series, color in zip(
            self.x_values, self.y_values, self.colors
        ):
            paths = []
            for bar_idx, (x, y) in enumerate(zip(x_values_series, y_values_series)):
                # Calculate vertical position for this bar
                bar_y = start_y + bar_idx * (bar_thickness + gap)
                bar_width = x
                paths.append(Path.get_path(0, bar_y, bar_width, bar_thickness))
            g.add_child(Path(d=paths, fill=color))

        return g
