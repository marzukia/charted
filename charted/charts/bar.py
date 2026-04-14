from __future__ import annotations

from charted.charts.chart import Chart
from charted.html.element import G, Path
from charted.utils.themes import Theme
from charted.utils.types import Labels, Vector, Vector2D


class BarChart(Chart):
    x_stacked: bool = True

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
        # For BarChart: data values on x-axis (horizontal bars), labels on y-axis
        # Convert 1D data to 2D
        if not isinstance(data, list) or not data or isinstance(data[0], (int, float)):
            x_data = [data]
        else:
            x_data = data

        # Check for empty data
        if not x_data or not x_data[0]:
            raise ValueError("No data was provided to the BarChart element.")

        # y_data needs to have same number of series as x_data, with len(labels)
        # or len(x_data[0]) values
        num_bars = len(x_data[0]) if x_data else 0
        num_series = len(x_data) if x_data else 0
        # Use 0-indexed positions for y (categories), starting from 0
        # Ensure at least 2 values for y_axis to work (avoid div by zero)
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
        return self.plot_height / (self.y_count + (self.y_count + 1) * self.bar_gap)

    @property
    def representation(self) -> G:
        # Calculate offset from y-axis for labels
        x_offset = self.x_axis.reproject(1) if self.y_labels else 0

        g = G(opacity="0.8")
        for x_values_arr, y_offsets_arr, color in zip(
            self.x_values,
            self.y_offsets,
            self.colors,
        ):
            paths = []
            for x, y in zip(x_values_arr, self.y_values[0]):
                # y is already the pixel position from y_values
                # Horizontal bars: start at x_offset, extend right by x (data value),
                # positioned at y vertically, with y_height thickness
                paths.append(Path.get_path(x_offset, y, x, self.y_height))
            g.add_child(Path(d=paths, fill=color))

        return g
