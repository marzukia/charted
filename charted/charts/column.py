from __future__ import annotations

from charted.charts.chart import Chart
from charted.html.element import G, Path
from charted.utils.themes import Theme
from charted.utils.transform import translate
from charted.utils.types import Labels, Vector, Vector2D


class ColumnChart(Chart):
    y_stacked: bool = False
    side_by_side: bool = False

    def __init__(
        self,
        data: Vector | Vector2D,
        labels: Labels = None,
        column_gap: float = 0.50,
        width: float = 500,
        height: float = 500,
        zero_index: bool = True,
        title: str | None = None,
        theme: Theme | None = None,
        series_names: list[str] | None = None,
    ):
        self.column_gap = column_gap
        super().__init__(
            width=width,
            height=height,
            y_data=data,
            x_labels=labels,
            title=title,
            zero_index=zero_index,
            theme=theme,
            series_names=series_names,
        )

    @property
    def x_width(self) -> float:
        return self.plot_width / (self.x_count + (self.x_count + 1) * self.column_gap)

    @property
    def representation(self) -> G:
        dy = 0
        if self.y_axis.axis_dimension.min_value < 0:
            dy = self.y_axis.reproject(abs(self.y_axis.axis_dimension.min_value))

        g = G(
            opacity="0.8",
            transform=[
                *self.get_base_transform(),
                translate(-self.x_width / 2, dy),
            ],
        )

        num_series = len(self.y_values)

        if not self.y_stacked:
            # side-by-side mode
            bar_width = self.x_width / num_series if num_series > 0 else self.x_width
            series_offset = (bar_width * (num_series - 1)) / 2 if num_series > 0 else 0

            for series_idx in range(num_series):
                y_values = self.y_values[series_idx]
                x_values = self.x_values[series_idx]
                color = (
                    self.colors[series_idx]
                    if series_idx < len(self.colors)
                    else self.colors[series_idx % len(self.colors)]
                )

                paths = []
                for x_idx, (x, y) in enumerate(zip(x_values, y_values)):
                    x += self.x_offset
                    # center bar within its slot, offset from group center
                    bar_x = x - series_offset + series_idx * bar_width
                    paths.append(
                        Path.get_path(
                            bar_x, min(0, y), bar_width, max(y, 0) - min(0, y)
                        )
                    )
                g.add_child(Path(d=paths, fill=color))
        else:
            # stacked mode
            running_y = [0.0] * len(self.y_values[0]) if self.y_values else []

            for y_values, x_values, color in zip(
                self.y_values,
                self.x_values,
                self.colors,
            ):
                paths = []
                for x_idx, (x, y) in enumerate(zip(x_values, y_values)):
                    x += self.x_offset
                    y_offset = running_y[x_idx]
                    y_start = min(y_offset, y_offset + y)
                    y_height = abs(y)
                    running_y[x_idx] += y
                    paths.append(Path.get_path(x, y_start, self.x_width, y_height))

                g.add_child(Path(d=paths, fill=color))

        return g

        if self.y_axis.axis_dimension.min_value < 0:
            dy = self.y_axis.reproject(abs(self.y_axis.axis_dimension.min_value))

        g = G(
            opacity="0.8",
            transform=[
                *self.get_base_transform(),
                translate(-self.x_width / 2, dy),
            ],
        )
        for y_values, y_offsets, x_values, color in zip(
            self.y_values,
            self.y_offsets,
            self.x_values,
            self.colors,
        ):
            paths = []
            for x, y, y_offset in zip(x_values, y_values, y_offsets):
                x += self.x_offset
                paths.append(Path.get_path(x, y_offset, self.x_width, y))
            g.add_child(Path(d=paths, fill=color))

        return g
