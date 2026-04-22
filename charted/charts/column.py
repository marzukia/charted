from __future__ import annotations

from charted.charts.chart import Chart
from charted.config import get_column_gap
from charted.html.element import G, Path
from charted.utils.themes import Theme
from charted.utils.transform import translate
from charted.utils.types import Labels, SeriesStyleConfig, Vector, Vector2D


class ColumnChart(Chart):
    """Vertical column chart for comparing categorical data.

    Displays data as vertical columns where the height of each column
    represents the value. Supports single and multi-series data,
    with optional stacking and side-by-side layouts.

    Args:
        data: Single series (list of values) or multi-series (list of lists)
        labels: Category labels for the x-axis
        column_gap: Gap between columns as ratio of column width (default 0.2)
        width, height: Chart dimensions in pixels
        zero_index: Whether to include zero on the y-axis
        title: Optional chart title
        theme: Optional theme configuration
        series_names: Names for each series (shown in legend)
        y_stacked: If True, stack columns vertically instead of side-by-side
        series_styles: Per-series style overrides

    Example:
        >>> from charted import ColumnChart
        >>> chart = ColumnChart(data=[120, 180, 210], labels=['Q1', 'Q2', 'Q3'])
        >>> chart.save('sales.svg')
    """

    y_stacked: bool = True

    def __init__(
        self,
        data: Vector | Vector2D,
        labels: Labels = None,
        column_gap: float = None,
        width: float = 500,
        height: float = 500,
        zero_index: bool = True,
        title: str | None = None,
        theme: Theme | None = None,
        series_names: list[str] | None = None,
        y_stacked: bool = True,
        series_styles: list[SeriesStyleConfig] | None = None,
    ):
        if column_gap is None:
            column_gap = get_column_gap()
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
            chart_type="column",
            series_styles=series_styles,
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

        g = G(
            opacity="0.8",
            transform=[
                *self.get_base_transform(),
                translate(-self.x_width / 2, dy),
            ],
        )

        if self.y_stacked:
            for series_idx, (y_values, y_offsets, x_values, color) in enumerate(
                zip(self.y_values, self.y_offsets, self.x_values, self.colors)
            ):
                # Apply fill override from series_styles
                fill = color
                if self.series_styles and series_idx < len(self.series_styles):
                    style = self.series_styles[series_idx] or {}
                    if style.get("fill"):
                        fill = style["fill"]

                paths = []
                for x, y, y_offset in zip(x_values, y_values, y_offsets):
                    x += self.x_offset
                    paths.append(Path.get_path(x, y_offset, self.x_width, y))
                g.add_child(Path(d=paths, fill=fill))
        else:
            # side-by-side mode
            num_series = len(self.y_values) if self.y_values else 1
            bar_width = self.x_width / num_series if num_series > 0 else self.x_width
            series_offset = (bar_width * (num_series - 1)) / 2 if num_series > 0 else 0

            for series_idx, (y_values_series, color) in enumerate(
                zip(self.y_values, self.colors)
            ):
                # Apply fill override from series_styles
                fill = color
                if self.series_styles and series_idx < len(self.series_styles):
                    style = self.series_styles[series_idx] or {}
                    if style.get("fill"):
                        fill = style["fill"]

                paths = []
                for x_idx, y in enumerate(y_values_series):
                    x = self.x_offset + x_idx * (
                        self.x_width + self.column_gap * self.x_width
                    )
                    # center bar within its slot, offset from group center
                    bar_x = x - series_offset + series_idx * bar_width
                    if y >= 0:
                        paths.append(Path.get_path(bar_x, 0, bar_width, y))
                    else:
                        paths.append(Path.get_path(bar_x, y, bar_width, -y))
                g.add_child(Path(d=paths, fill=fill))

        return g
