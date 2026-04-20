from __future__ import annotations

from charted.charts.chart import Chart
from charted.html.element import G, Path
from charted.utils.themes import Theme
from charted.utils.transform import translate
from charted.utils.types import Labels, Vector, Vector2D


class ColumnChart(Chart):
    y_stacked: bool = False

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
        y_stacked: bool = False,
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
            y_stacked=y_stacked,
        )

    @property
    def x_width(self) -> float:
        return self.plot_width / (self.x_count + (self.x_count + 1) * self.column_gap)

    @property
    def representation(self) -> G:
        slot_width = self.x_width
        gap = slot_width * self.column_gap
        start_x = gap

        num_series = len(self.y_values) if self.y_values else 1
        series_thickness = (
            slot_width / num_series
            if (num_series > 0 and not self.y_stacked)
            else slot_width
        )

        dy = 0
        if self.y_axis.axis_dimension.min_value < 0 and not self.y_stacked:
            dy = self.y_axis.reproject(abs(self.y_axis.axis_dimension.min_value))

        bars_g = G(
            opacity="0.8",
            transform=[
                *self.get_base_transform(),
                translate(start_x - slot_width / 2, dy),
            ],
        )
        if self.y_stacked:
            # Stacked mode: iterate series, accumulate offsets along the y axis
            for y_values_series, y_offsets_series, color in zip(
                self.y_values, self.y_offsets, self.colors
            ):
                paths = []
                for col_idx, (y, y_offset_val) in enumerate(
                    zip(y_values_series, y_offsets_series)
                ):
                    slot_x = start_x + col_idx * (slot_width + gap)
                    # For stacked mode with mixed +/- values, render from offset
                    # Positive y extends down (larger y in SVG), negative extends up
                    if y >= 0:
                        bottom_y = y_offset_val
                        height = y
                    else:
                        bottom_y = y_offset_val + y
                        height = abs(y)
                    paths.append(
                        Path.get_path(slot_x, bottom_y, series_thickness, height)
                    )
                bars_g.add_child(Path(d=paths, fill=color))
        else:
            # Side-by-side mode: draw from zero line (like BarChart)
            zero_y = self.y_axis.zero
            for series_idx, (y_values_series, color) in enumerate(
                zip(self.y_values, self.colors)
            ):
                paths = []
                for col_idx, y in enumerate(y_values_series):
                    slot_x = start_x + col_idx * (slot_width + gap)
                    bar_x = slot_x + series_idx * series_thickness
                    if y >= zero_y:
                        paths.append(
                            Path.get_path(bar_x, zero_y, series_thickness, y - zero_y)
                        )
                    else:
                        paths.append(
                            Path.get_path(bar_x, y, series_thickness, zero_y - y)
                        )
                bars_g.add_child(Path(d=paths, fill=color))

        return bars_g
