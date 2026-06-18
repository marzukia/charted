"""Regression tests for x-axis tick-label bottom-clipping bug.

X-axis tick labels were positioned with their baseline too close to the SVG
viewBox bottom edge: on small canvases the baseline landed exactly at the
viewBox height, clipping descenders.  On the standard 500 px canvas there was
only 7 px of margin, which browsers rendered as visually tight / partially
clipped when the SVG is embedded.

The fix: ``bottom_padding`` now guarantees at least
  ``DEFAULT_PADDING + max_x_label_height``
of clearance below the plot, so the full label band (baseline + descenders)
always sits inside the viewBox with breathing room.
"""

from __future__ import annotations

import random
from datetime import date

from charted import ColumnChart, Histogram
from charted.charts.gantt import GanttChart
from charted.constants import DEFAULT_PADDING

_BREATHING_ROOM = 6  # minimum pixels of clearance expected below label descenders


def _label_band_clearance(chart) -> float:
    """Return pixels between the estimated label bottom and the viewBox edge.

    Label baseline absolute y = top_padding + DEFAULT_PADDING + plot_height.
    Estimated label bottom = baseline + descent_px (approx 30% of label height).
    Clearance = viewBox height - label bottom.
    """
    baseline_abs_y = chart.top_padding + DEFAULT_PADDING + chart.plot_height
    if chart.layout.x_labels:
        max_h = max(lab.height for lab in chart.layout.x_labels)
    else:
        from charted.utils.defaults import DEFAULT_FONT_SIZE
        max_h = DEFAULT_FONT_SIZE
    descent_px = max_h * 0.3  # conservative descent estimate
    label_bottom = baseline_abs_y + descent_px
    return chart.height - label_bottom


class TestXTickLabelBottomClipping:
    """Labels must clear the viewBox bottom with breathing room."""

    def test_standard_canvas_column_has_clearance(self):
        c = ColumnChart(data=[1, 2, 3], labels=["a", "b", "c"])
        assert _label_band_clearance(c) >= _BREATHING_ROOM, (
            f"ColumnChart 500px: only {_label_band_clearance(c):.1f}px below label bottom"
        )

    def test_small_canvas_column_has_clearance(self):
        c = ColumnChart(data=[1, 2, 3], labels=["abc", "def", "ghi"], height=300)
        assert _label_band_clearance(c) >= _BREATHING_ROOM, (
            f"ColumnChart 300px: {_label_band_clearance(c):.1f}px below label bottom (clips!)"
        )

    def test_histogram_standard_canvas_has_clearance(self):
        rng = random.Random(42)
        h = Histogram(data=[rng.gauss(50, 15) for _ in range(200)])
        assert _label_band_clearance(h) >= _BREATHING_ROOM, (
            f"Histogram 500px: {_label_band_clearance(h):.1f}px below label bottom"
        )

    def test_gantt_standard_canvas_has_clearance(self):
        g = GanttChart(
            data=[(date(2024, 1, 1), date(2024, 4, 1)), (date(2024, 3, 1), date(2024, 7, 1))],
            labels=["Design", "Dev"],
        )
        assert _label_band_clearance(g) >= _BREATHING_ROOM, (
            f"GanttChart 500px: {_label_band_clearance(g):.1f}px below label bottom"
        )

    def test_baseline_never_at_viewbox_edge(self):
        """Baseline should never equal viewBox height (prevents total clipping)."""
        c = ColumnChart(data=[1, 2, 3], labels=["a", "b", "c"], height=300)
        baseline_abs_y = c.top_padding + DEFAULT_PADDING + c.plot_height
        assert baseline_abs_y < c.height, (
            f"Baseline ({baseline_abs_y}) == viewBox height ({c.height}): labels fully clipped"
        )
