"""Regression test for histogram bar-alignment bug.

Before the fix: bars used ordinal division (i * plot_w / n) while the x-axis
ticks used ordinal-index coordinates for n labels (i * plot_w / (n-1)).  The
two systems disagreed: tick spacing was plot_w/(n-1), bar width was plot_w/n.

After the fix: the x-axis carries n+1 edge labels (indices 0..n), so tick i
lands at i * plot_w / n.  Bars span coords[i] to coords[i+1], so bar width
== tick spacing == plot_w / n.  Bar left edges sit exactly on the edge ticks.
"""

import re

from charted.charts.histogram import Histogram


def _parse_bars(svg: str) -> list[tuple[float, float]]:
    """Extract (x, width) of histogram bar rects (skip the background rect)."""
    rects = re.findall(r"<rect[^>]+>", svg)
    bars = []
    for r in rects[1:]:  # first rect is the background
        xm = re.search(r' x="([^"]+)"', r)
        wm = re.search(r' width="([^"]+)"', r)
        if xm and wm:
            bars.append((float(xm.group(1)), float(wm.group(1))))
    return bars


class TestHistogramBarAlignment:
    """Bar geometry must match tick geometry on the continuous bin-edge axis."""

    def test_bar_width_equals_tick_spacing(self):
        """Bar width must equal the x-axis tick spacing (bin width in pixels)."""
        chart = Histogram(data=list(range(0, 100, 3)), bins=10)
        coords = chart.x_axis.coordinates
        # n+1 edge ticks → n intervals, each of width plot_w/n
        assert len(coords) == 11, f"Expected 11 edge ticks, got {len(coords)}"
        tick_spacing = coords[1] - coords[0]

        bars = _parse_bars(chart.to_svg())
        assert len(bars) == 10

        for i, (x, bar_w) in enumerate(bars):
            assert abs(bar_w - tick_spacing) < 0.5, (
                f"Bar {i}: width={bar_w:.3f} != tick_spacing={tick_spacing:.3f}"
            )

    def test_bar_left_edges_align_with_edge_ticks(self):
        """Bar left edges must land on the bin-edge tick x positions."""
        chart = Histogram(data=list(range(0, 100, 3)), bins=10)
        coords = chart.x_axis.coordinates
        pad_x = chart.left_padding

        bars = _parse_bars(chart.to_svg())
        for i, (bar_x, _) in enumerate(bars):
            expected_x = pad_x + coords[i]
            assert abs(bar_x - expected_x) < 0.5, (
                f"Bar {i}: x={bar_x:.3f} != expected {expected_x:.3f} "
                f"(pad_x={pad_x:.3f} + coords[{i}]={coords[i]:.3f})"
            )

    def test_n_plus_one_edge_labels(self):
        """The x-axis must expose n+1 tick coordinates for n bins."""
        for n_bins in (5, 8, 10, 15):
            chart = Histogram(data=list(range(100)), bins=n_bins)
            coords = chart.x_axis.coordinates
            assert len(coords) == n_bins + 1, (
                f"bins={n_bins}: expected {n_bins + 1} coords, got {len(coords)}"
            )

    def test_last_tick_at_plot_right_edge(self):
        """The final tick (right edge of last bar) must sit at plot_width."""
        chart = Histogram(data=list(range(50)), bins=8)
        coords = chart.x_axis.coordinates
        assert abs(coords[-1] - chart.plot_width) < 0.5, (
            f"Last coord {coords[-1]:.3f} != plot_width {chart.plot_width:.3f}"
        )

    def test_custom_edge_labels_respected(self):
        """Custom labels (n+1 strings) are passed through to the axis."""
        custom = ["0", "10", "20", "30", "40", "50"]
        chart = Histogram(data=list(range(50)), bins=5, labels=custom)
        label_texts = [lbl.text for lbl in (chart.x_labels or [])]
        assert label_texts == custom
