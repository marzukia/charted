"""Histogram — distribution of data values across bins.

Shows the frequency of values within evenly-spaced intervals.
"""

from __future__ import annotations

import math

from charted.charts.chart import Chart
from charted.constants import DEFAULT_CHART_HEIGHT, DEFAULT_CHART_WIDTH
from charted.html.element import G, Rect
from charted.themes.core import Theme
from charted.utils.types import Vector


def _auto_bins(data: list[float]) -> int:
    """Calculate a reasonable number of bins using Sturges' rule."""
    n = len(data)
    if n == 0:
        return 10
    return max(5, min(50, int(math.log2(n) + 1)))


def _compute_bins(data: list[float], n_bins: int) -> tuple[list[float], list[str]]:
    """Compute bin counts and labels for histogram data."""
    if not data:
        return [0.0] * n_bins, [str(i) for i in range(n_bins + 1)]

    min_v, max_v = min(data), max(data)
    if max_v == min_v:
        return [float(len(data))] + [0.0] * (n_bins - 1), [
            f"{min_v:.1f}" for _ in range(n_bins + 1)
        ]
    bin_w = (max_v - min_v) / n_bins if n_bins > 0 else 1
    counts = [0.0] * n_bins
    for v in data:
        idx = min(n_bins - 1, max(0, int((v - min_v) / bin_w)))
        counts[idx] += 1.0

    labels = [f"{min_v + i * bin_w:.1f}" for i in range(n_bins + 1)]
    return counts, labels


class Histogram(Chart):
    """Histogram showing value distribution across bins.

    Args:
        data: Single list of values to bin.
        bins: Number of bins (auto-calculated if None).
        labels: Optional x-axis labels.
        width, height: Chart dimensions in pixels.
        title: Optional chart title.
        theme: Optional theme configuration.

    Example:
        >>> chart = Histogram(
        ...     data=[1, 2, 2, 3, 3, 3, 4, 4, 5],
        ...     bins=5,
        ... )
    """

    def __init__(
        self,
        data: Vector,
        bins: int | None = None,
        labels: list[str] | None = None,
        width: float = DEFAULT_CHART_WIDTH,
        height: float = DEFAULT_CHART_HEIGHT,
        title: str | None = None,
        theme: Theme | None = None,
    ):
        n_bins = bins if bins is not None else _auto_bins(data)
        bin_counts, bin_labels = _compute_bins(data, n_bins)

        # Store before super().__init__ so representation can access it
        self._bin_counts = bin_counts

        super().__init__(
            y_data=[bin_counts],
            x_labels=labels or bin_labels,
            width=width,
            height=height,
            title=title,
            theme=theme,
            chart_type="histogram",
        )

    @property
    def representation(self) -> G:
        """Render histogram as bars."""
        g = G()
        plot_h = self.plot_height
        x_offset = self.x_offset
        x_vals = self.x_values[0]
        pad_x = self.left_padding
        pad_y = self.top_padding

        bar_w = x_offset

        for i, (y_val, y_off) in enumerate(zip(self.y_values[0], self.y_offsets[0])):
            x = pad_x + x_vals[i] + x_offset
            h = y_val + y_off if self.y_stacked else y_val
            g.add_child(
                Rect(
                    x=x,
                    y=pad_y + plot_h - h,
                    width=bar_w,
                    height=h,
                    fill=self.colors[0],
                    fill_opacity=0.7,
                    stroke=self.colors[0],
                    stroke_width=0.5,
                )
            )

        return g
