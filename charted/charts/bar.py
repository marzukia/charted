from __future__ import annotations

from charted.charts.axes import _round_coord
from charted.charts.chart import Chart
from charted.config import get_bar_gap
from charted.constants import DEFAULT_CHART_HEIGHT, DEFAULT_CHART_WIDTH
from charted.html.element import G, Path
from charted.utils.themes import Theme
from charted.utils.types import Labels, SeriesStyleConfig, Vector, Vector2D


class BarChart(Chart):
    """Horizontal bar chart for comparing categorical data.

    Displays data as horizontal bars where the length of each bar
    represents the value. Supports single and multi-series data,
    with optional stacking and side-by-side layouts.

    Args:
        data: Single series (list of values) or multi-series (list of lists)
        labels: Category labels for the y-axis
        bar_gap: Gap between bars as ratio of bar height (default from config)
        width, height: Chart dimensions in pixels
        zero_index: Whether to include zero on the x-axis
        title: Optional chart title
        theme: Optional theme configuration
        series_names: Names for each series (shown in legend)
        series_styles: Per-series style overrides
        x_stacked: If True, stack bars horizontally instead of side-by-side

    Example:
        >>> from charted import BarChart
        >>> chart = BarChart(data=[120, 180, 210], labels=['Q1', 'Q2', 'Q3'])
        >>> chart.save('sales.svg')
    """

    def __init__(
        self,
        data: Vector | Vector2D,
        labels: Labels = None,
        bar_gap: float = None,
        width: float = DEFAULT_CHART_WIDTH,
        height: float = DEFAULT_CHART_HEIGHT,
        zero_index: bool = True,
        title: str | None = None,
        theme: Theme | None = None,
        series_names: list[str] | None = None,
        series_styles: list[SeriesStyleConfig] | None = None,
        x_stacked: bool = False,
        axis_tick_interval: int | None = None,
    ):
        if bar_gap is None:
            bar_gap = get_bar_gap()
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
            chart_type="bar",
            series_styles=series_styles,
            axis_tick_interval=axis_tick_interval,
        )

        # Refresh axes grid_lines after parent is fully initialized.
        # During Chart.__init__, left_padding returns h_pad (25.0) because
        # y_axis doesn't exist yet. After initialization, it correctly
        # calculates from labels (32.0). We need to recreate the grid Path
        # with correct values.
        if self.y_axis and self.y_axis.config:
            self.y_axis.children[0] = self.y_axis.grid_lines
            self.y_axis.children[1] = self.y_axis.axis_labels

        if self.x_axis and self.x_axis.config:
            self.x_axis.children[0] = self.x_axis.grid_lines
            self.x_axis.children[1] = self.x_axis.axis_labels

    @property
    def y_height(self) -> float:
        return _round_coord(
            self.plot_height / (self.y_count + (self.y_count + 1) * self.bar_gap), 1
        )

    def get_base_transform(self):
        return []

    @property
    def representation(self) -> G:
        slot_height = self.y_height
        gap = _round_coord(slot_height * self.bar_gap, 1)
        start_y = gap

        num_series = len(self.x_values) if self.x_values else 1
        series_thickness = (
            _round_coord(slot_height / num_series, 1)
            if (num_series > 0 and not self.x_stacked)
            else slot_height
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
            transform=f"translate({_round_coord(self.left_padding + dx, 1)}, {_round_coord(self.top_padding, 1)})",
        )

        if self.x_stacked:
            # Mirror ColumnChart: iterate series, accumulate offsets along the
            # value axis (x here, y in ColumnChart). x_offsets is pre-computed
            # and already reprojected by Chart.x_offsets setter.
            for series_idx, (x_values_series, x_offsets_series, color) in enumerate(
                zip(self.x_values, self.x_offsets, self.colors)
            ):
                # Apply fill override from series_styles
                fill = color
                if self.series_styles and series_idx < len(self.series_styles):
                    style = self.series_styles[series_idx] or {}
                    if style.get("fill"):
                        fill = style["fill"]

                paths = []
                for bar_idx, (x, x_offset_val) in enumerate(
                    zip(x_values_series, x_offsets_series)
                ):
                    slot_y = _round_coord(start_y + bar_idx * (slot_height + gap), 1)
                    # x_offset_val is the reprojected cumulative start position
                    # and x is the reprojected signed value. Use the leftmost
                    # point and positive width regardless of sign so that a
                    # positive value stacked on top of a negative cumulative
                    # offset (or vice versa) renders correctly.
                    left_x = _round_coord(min(x_offset_val, x_offset_val + x), 1)
                    width = _round_coord(abs(x), 1)
                    paths.append(Path.get_path(left_x, slot_y, width, series_thickness))
                bars_g.add_child(Path(d=paths, fill=fill))
        else:
            zero_x = self.x_axis.zero
            for series_idx, (x_values_series, color) in enumerate(
                zip(self.x_values, self.colors)
            ):
                # Apply fill override from series_styles
                fill = color
                if self.series_styles and series_idx < len(self.series_styles):
                    style = self.series_styles[series_idx] or {}
                    if style.get("fill"):
                        fill = style["fill"]

                paths = []
                for bar_idx, x in enumerate(x_values_series):
                    slot_y = _round_coord(start_y + bar_idx * (slot_height + gap), 1)
                    bar_y = _round_coord(slot_y + series_idx * series_thickness, 1)
                    if x >= zero_x:
                        paths.append(
                            Path.get_path(
                                _round_coord(zero_x, 1),
                                bar_y,
                                _round_coord(x - zero_x, 1),
                                series_thickness,
                            )
                        )
                    else:
                        paths.append(
                            Path.get_path(
                                _round_coord(x, 1),
                                bar_y,
                                _round_coord(zero_x - x, 1),
                                series_thickness,
                            )
                        )
                bars_g.add_child(Path(d=paths, fill=fill))

        # Plot borders — all four sides.
        grid_color = "#CCCCCC"
        if isinstance(self.theme, dict):
            grid_color = self.theme.get("h_grid", {}).get("stroke", "#CCCCCC")

        border_transform = f"translate({_round_coord(self.left_padding, 1)}, {_round_coord(self.top_padding, 1)})"
        borders = [
            Path(
                stroke=grid_color,
                stroke_dasharray="None",
                d=[
                    f"M0 {_round_coord(self.plot_height, 1)} h{_round_coord(self.plot_width, 1)}"
                ],
                transform=border_transform,
            ),
            Path(
                stroke=grid_color,
                stroke_dasharray="None",
                d=[f"M0 0 h{_round_coord(self.plot_width, 1)}"],
                transform=border_transform,
            ),
            Path(
                stroke=grid_color,
                stroke_dasharray="None",
                d=[f"M0 0 v{_round_coord(self.plot_height, 1)}"],
                transform=border_transform,
            ),
            Path(
                stroke=grid_color,
                stroke_dasharray="None",
                d=[
                    f"M{_round_coord(self.plot_width, 1)} 0 v{_round_coord(self.plot_height, 1)}"
                ],
                transform=border_transform,
            ),
        ]

        result = G()
        result.add_children(bars_g, *borders)
        return result
