from __future__ import annotations

from charted.charts.chart import Chart
from charted.html.element import G, Path
from charted.utils.themes import Theme
from charted.utils.transform import translate
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
        return self.plot_height / (self.y_count + (self.y_count + 1) * self.bar_gap)

    def get_base_transform(self):
        return []

    @property
    def representation(self) -> G:
        dx = 0
        if self.x_axis.axis_dimension.min_value < 0:
            dx = self.x_axis.reproject(abs(self.x_axis.axis_dimension.min_value))

        # Starting X for all bars accounts for number of series
        num_series = len(self.x_values) if self.x_values else 1
        start_x = self.plot_width / (self.y_count + num_series - 1)

        g = G(
            opacity="0.8",
        )
        for x_values_series, y_values_series, color in zip(
            self.x_values,
            self.y_values,
            self.colors,
        ):
            paths = []
            for x, y in zip(x_values_series, y_values_series):
                paths.append(Path.get_path(start_x + dx, y, x, self.y_height))
            g.add_child(Path(d=paths, fill=color))

        return g
