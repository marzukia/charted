from __future__ import annotations

from charted.charts.chart import Chart
from charted.html.element import G, Path
from charted.utils.themes import Theme
from charted.utils.transform import translate
from charted.utils.types import Labels, Vector, Vector2D


class ColumnChart(Chart):
    y_stacked: bool = True

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
        y_stacked: bool = True,
    ):
        self.column_gap = column_gap
        self.y_stacked = y_stacked
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

        num_series = len(self.y_values) if self.y_values else 1
        series_width = (
            self.x_width / num_series
            if (num_series > 0 and not self.y_stacked)
            else self.x_width
        )

        g = G(
            opacity="0.8",
            transform=[
                *self.get_base_transform(),
                translate(-self.x_width / 2, dy),
            ],
        )

        if self.y_stacked:
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
        else:
            zero_y = self.y_axis.zero
            for series_idx, (y_values_series, color) in enumerate(
                zip(self.y_values, self.colors)
            ):
                paths = []
                for x_idx, y in enumerate(y_values_series):
                    slot_x = self.x_offset + x_idx * (
                        self.x_width + self.column_gap * self.x_width
                    )
                    bar_x = slot_x + series_idx * series_width
                    if y >= zero_y:
                        paths.append(
                            Path.get_path(bar_x, zero_y, series_width, -y + zero_y)
                        )
                    else:
                        paths.append(Path.get_path(bar_x, y, series_width, zero_y - y))
                g.add_child(Path(d=paths, fill=color))

        return g
