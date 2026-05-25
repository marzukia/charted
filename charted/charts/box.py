"""Box plot — statistical chart showing distribution quartiles.

Displays median, quartiles, and outliers for one or more data series.
"""

from __future__ import annotations

from charted.charts.chart import Chart
from charted.constants import DEFAULT_CHART_HEIGHT, DEFAULT_CHART_WIDTH
from charted.html.element import G, Path, Rect
from charted.themes.core import Theme
from charted.utils.types import Labels, Vector2D


def _quartiles(data: list[float]) -> tuple[float, float, float, float, float]:
    """Calculate min, Q1, median, Q3, max for a dataset."""
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n == 0:
        return (0, 0, 0, 0, 0)

    def median(arr) -> float:
        if not arr:
            return 0
        mid = len(arr) // 2
        if len(arr) % 2 == 0:
            return (arr[mid - 1] + arr[mid]) / 2
        return arr[mid]

    q1 = median(sorted_data[: max(n // 2, 1)])
    q3 = median(sorted_data[n - max(n // 2, 1) :])
    med = median(sorted_data)
    return sorted_data[0], q1, med, q3, sorted_data[-1]


class BoxPlot(Chart):
    """Box plot showing distribution quartiles for data series.

    Args:
        data: List of series, each series is a list of values.
        labels: Labels for each box (categories).
        width, height: Chart dimensions in pixels.
        title: Optional chart title.
        theme: Optional theme configuration.
        series_names: Names for each series.

    Example:
        >>> chart = BoxPlot(
        ...     data=[[1, 2, 3, 4, 5], [2, 3, 4, 5, 6]],
        ...     labels=['Group A', 'Group B'],
        ... )
    """

    def __init__(
        self,
        data: Vector2D,
        labels: Labels | None = None,
        width: float = DEFAULT_CHART_WIDTH,
        height: float = DEFAULT_CHART_HEIGHT,
        title: str | None = None,
        theme: Theme | None = None,
        series_names: list[str] | None = None,
    ):
        self._raw_data = data
        super().__init__(
            y_data=data,
            x_labels=labels,
            width=width,
            height=height,
            title=title,
            theme=theme,
            series_names=series_names,
            chart_type="box",
        )

    @property
    def representation(self) -> G:
        """Render box plot elements."""
        g = G()
        plot_h = self.plot_height
        plot_w = self.plot_width

        n_boxes = len(self._raw_data)
        box_w = plot_w / n_boxes * 0.6

        for i, series in enumerate(self._raw_data):
            if not series:
                continue
            min_v, q1, med, q3, max_v = _quartiles(series)
            color = self.colors[i]

            cx = self.left_padding + self.x_axis.coordinates[i + 1]

            def map_y(v: float) -> float:
                return self.top_padding + plot_h - self.y_axis.reproject(v)

            y_min = map_y(min_v)
            y_q1 = map_y(q1)
            y_med = map_y(med)
            y_q3 = map_y(q3)
            y_max = map_y(max_v)

            # Whisker line (min to max)
            g.add_child(
                Path(
                    d=f"M{cx} {y_min} L{cx} {y_max}",
                    stroke=color,
                    stroke_width=2,
                )
            )
            # Whisker caps
            cap_w = box_w * 0.3
            g.add_child(
                Path(
                    d=f"M{cx - cap_w} {y_min} L{cx + cap_w} {y_min}",
                    stroke=color,
                    stroke_width=2,
                )
            )
            g.add_child(
                Path(
                    d=f"M{cx - cap_w} {y_max} L{cx + cap_w} {y_max}",
                    stroke=color,
                    stroke_width=2,
                )
            )

            # Box (Q1 to Q3) — prominent IQR rectangle
            g.add_child(
                Rect(
                    x=cx - box_w / 2,
                    y=y_q1,
                    width=box_w,
                    height=y_q3 - y_q1,
                    fill=color,
                    fill_opacity=0.6,
                    stroke=color,
                    stroke_width=2.5,
                )
            )
            # Median line — thicker to stand out inside the box
            g.add_child(
                Path(
                    d=f"M{cx - box_w / 2} {y_med} L{cx + box_w / 2} {y_med}",
                    stroke="#333333",
                    stroke_width=3,
                )
            )

        return g
