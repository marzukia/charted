"""Histogram: distribution of data values across bins.

Shows the frequency of values within evenly-spaced intervals.
"""

from __future__ import annotations

import math

from charted.charts.chart import Chart
from charted.constants import DEFAULT_CHART_HEIGHT, DEFAULT_CHART_WIDTH
from charted.html.element import G, Rect
from charted.themes.core import Theme
from charted.utils.types import ReferenceLineDict, Vector


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
    # Category-axis padding adds blank labels that fool the overlap filter into
    # keeping only the blank endpoints. Disable it so real bin labels render.
    pad_x_labels: bool = False

    # The x-axis carries n+1 bin-edge labels but y_data has only n counts.
    # Skip the generic label-length cross-check so DataModel does not raise
    # LabelMismatchError; the histogram validates its own label geometry.
    _skip_label_length_validation: bool = True

    """Histogram showing value distribution across bins.

    Args:
        data: Single list of values to bin.
        bins: Number of bins (auto-calculated if None).
        labels: Optional x-axis labels (n+1 edge labels).
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
        subtitle: str | None = None,
        subtitle_leading: float = 8.0,
        theme: Theme | None = None,
        x_label: str | None = None,
        y_label: str | None = None,
        h_lines: list[float] | None = None,
        v_lines: list[float] | None = None,
        reference_lines: list[ReferenceLineDict] | None = None,
        colors: list[str] | None = None,
        value_labels: bool | str | dict[str, object] | None = None,
        domain_padding: float | None = None,
    ):
        n_bins = bins if bins is not None else _auto_bins(data)
        bin_counts, bin_labels = _compute_bins(data, n_bins)

        # _compute_bins returns n_bins+1 edge labels: the left edge of every
        # bin plus the final right edge.  All n+1 labels are passed to the
        # x-axis so the axis has n+1 ordinal positions (indices 0..n_bins).
        # The tick at index i lands at i/n_bins * plot_width, which equals the
        # left edge of bar i.  The tick at index n_bins lands at plot_width,
        # which equals the right edge of the last bar.  Bar width is therefore
        # coords[i+1] - coords[i] == plot_width/n_bins, identical to tick
        # spacing.  This is the continuous-axis alignment contract.
        edge_labels = labels if labels is not None else bin_labels

        # Store before super().__init__ so representation can access it
        self._bin_counts = bin_counts
        self._n_bins = n_bins

        super().__init__(
            y_data=[bin_counts],
            x_labels=edge_labels,
            width=width,
            height=height,
            title=title,
            subtitle=subtitle,
            subtitle_leading=subtitle_leading,
            theme=theme,
            chart_type="histogram",
            x_label=x_label,
            y_label=y_label,
            h_lines=h_lines,
            v_lines=v_lines,
            reference_lines=reference_lines,
            colors=colors,
            value_labels=value_labels,
            domain_padding=domain_padding,
        )

    @property
    def representation(self) -> G:
        """Render histogram bars aligned to the continuous bin-edge x-axis.

        Each bar spans from x_axis.coordinates[i] to x_axis.coordinates[i+1],
        so bar left edges sit on the bin-edge ticks and bar width equals the
        tick spacing.
        """
        from charted.html.element import Text

        g = G()
        plot_h = self.plot_height
        pad_x = self.left_padding
        pad_y = self.top_padding

        # x_axis has n+1 coordinates (one per edge tick).  Bar i spans the
        # pixel interval [coords[i], coords[i+1]].
        coords = self.x_axis.coordinates
        n = len(self._bin_counts)

        value_labels = self._build_value_labels()
        label_row = value_labels[0] if value_labels else None
        font_size = max(8, self.theme.title_font_size - 4)
        font_color = self.theme.resolved_data_label_color
        # Track placed label boxes so colliding bin labels are auto-hidden.
        placed: list[tuple[float, float]] = []

        for i, (y_val, y_off) in enumerate(zip(self.y_values[0], self.y_offsets[0])):
            # Guard: if we somehow have fewer coords than expected, fall back to
            # even division so the chart never crashes on degenerate input.
            if i + 1 < len(coords):
                x = pad_x + coords[i]
                bar_w = coords[i + 1] - coords[i]
            else:
                bar_w = self.plot_width / n if n > 0 else 0
                x = pad_x + i * bar_w

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
            if label_row and i < len(label_row) and label_row[i]:
                cx = x + bar_w / 2
                # Auto-hide if too close to a previously-placed label.
                if any(abs(cx - px) < font_size * 1.6 for px, _ in placed):
                    continue
                placed.append((cx, 0))
                g.add_child(
                    Text(
                        text=str(label_row[i]),
                        x=cx,
                        y=pad_y + plot_h - h - 4,
                        fill=font_color,
                        font_size=font_size,
                        font_family=self.theme.title_font_family,
                        text_anchor="middle",
                    )
                )

        return g
