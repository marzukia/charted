from __future__ import annotations

from charted.charts.chart import Chart
from charted.html.element import G, Path
from charted.utils.themes import Theme
from charted.utils.types import Labels, Vector, Vector2D


class BarChart(Chart):

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
        series_names: list[str] | None = None,
        x_stacked: bool = False,
    ):
        self.bar_gap = bar_gap
        self.x_stacked = x_stacked

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
            series_names=series_names,
            x_stacked=x_stacked,
        )

    @property
    def y_height(self) -> float:
        return self.plot_height / (self.y_count + (self.y_count + 1) * self.bar_gap)

    def get_base_transform(self):
        return []

    @property
    def representation(self) -> G:
        slot_height = self.y_height
        gap = slot_height * self.bar_gap
        start_y = gap

        num_series = len(self.x_values) if self.x_values else 1
        series_thickness = (
            slot_height / num_series if (num_series > 0 and not self.x_stacked) else slot_height
        )

        # Mirror of ColumnChart's dy: for stacked charts with negative values,
        # shift the drawing group right so negative-magnitude bars (which draw
        # leftward from x_offset) land at the correct zero-relative position.
        # Non-stacked uses absolute zero_x from the reprojection and doesn't
        # need this compensation.
        dx = 0
        if self.x_stacked and self.x_axis.axis_dimension.min_value < 0:
            dx = self.x_axis.reproject(abs(self.x_axis.axis_dimension.min_value))

        bars_g = G(
            opacity="0.8",
            transform=f"translate({self.left_padding + dx}, {self.top_padding})",
        )

        if self.x_stacked:
            # Mirror ColumnChart: iterate series, accumulate offsets along the
            # value axis (x here, y in ColumnChart). x_offsets is pre-computed
            # and already reprojected by Chart.x_offsets setter.
            for x_values_series, x_offsets_series, color in zip(
                self.x_values, self.x_offsets, self.colors
            ):
                paths = []
                for bar_idx, (x, x_offset_val) in enumerate(
                    zip(x_values_series, x_offsets_series)
                ):
                    slot_y = start_y + bar_idx * (slot_height + gap)
                    if x >= 0:
                        paths.append(
                            Path.get_path(x_offset_val, slot_y, x, series_thickness)
                        )
                    else:
                        # Negative segment: x_offset_val is the accumulated
                        # start (already negative for subsequent negative
                        # contributions). Draw leftward from that offset.
                        paths.append(
                            Path.get_path(x_offset_val + x, slot_y, -x, series_thickness)
                        )
                bars_g.add_child(Path(d=paths, fill=color))
        else:
            zero_x = self.x_axis.zero
            for series_idx, (x_values_series, color) in enumerate(
                zip(self.x_values, self.colors)
            ):
                paths = []
                for bar_idx, x in enumerate(x_values_series):
                    slot_y = start_y + bar_idx * (slot_height + gap)
                    bar_y = slot_y + series_idx * series_thickness
                    if x >= zero_x:
                        paths.append(
                            Path.get_path(zero_x, bar_y, x - zero_x, series_thickness)
                        )
                    else:
                        paths.append(
                            Path.get_path(x, bar_y, zero_x - x, series_thickness)
                        )
                bars_g.add_child(Path(d=paths, fill=color))

        # Plot borders — all four sides.
        grid_color = "#CCCCCC"
        if isinstance(self.theme, dict):
            grid_color = self.theme.get("h_grid", {}).get("stroke", "#CCCCCC")

        border_transform = f"translate({self.left_padding}, {self.top_padding})"
        borders = [
            Path(
                stroke=grid_color,
                stroke_dasharray="None",
                d=[f"M0 {self.plot_height} h{self.plot_width}"],
                transform=border_transform,
            ),
            Path(
                stroke=grid_color,
                stroke_dasharray="None",
                d=[f"M0 0 h{self.plot_width}"],
                transform=border_transform,
            ),
            Path(
                stroke=grid_color,
                stroke_dasharray="None",
                d=[f"M0 0 v{self.plot_height}"],
                transform=border_transform,
            ),
            Path(
                stroke=grid_color,
                stroke_dasharray="None",
                d=[f"M{self.plot_width} 0 v{self.plot_height}"],
                transform=border_transform,
            ),
        ]

        result = G()
        result.add_children(bars_g, *borders)
        return result
