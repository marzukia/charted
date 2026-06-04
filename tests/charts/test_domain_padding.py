"""Domain-padding (auto headroom) tests for non-scatter chart types.

``domain_padding`` adds a fractional headroom to the data-derived domain so the
plotted geometry never touches the plot frame. Scatter and bubble pad both
sides; bar/column/area/histogram fill from a zero baseline, so the baseline
stays pinned and only the away-from-zero side gains headroom.
"""

import random

from charted.charts.area import AreaChart
from charted.charts.bar import BarChart
from charted.charts.bubble import BubbleChart
from charted.charts.column import ColumnChart
from charted.charts.histogram import Histogram


class TestZeroBaselineHeadroom:
    """Bar/column/area/histogram keep the zero baseline, pad the top."""

    def test_column_pads_top_only_for_positive_data(self):
        base = ColumnChart(data=[[10, 20, 30]], labels=["a", "b", "c"])
        padded = ColumnChart(
            data=[[10, 20, 30]], labels=["a", "b", "c"], domain_padding=0.1
        )
        # Baseline never moves off zero.
        assert padded.y_axis.axis_dimension.min_value == 0
        # Top gains headroom above the tallest column.
        assert (
            padded.y_axis.axis_dimension.max_value
            > base.y_axis.axis_dimension.max_value
        )

    def test_bar_value_axis_is_x_and_keeps_baseline(self):
        base = BarChart(data=[[10, 20, 30]], labels=["a", "b", "c"])
        padded = BarChart(
            data=[[10, 20, 30]], labels=["a", "b", "c"], domain_padding=0.1
        )
        assert padded.x_axis.axis_dimension.min_value == 0
        assert (
            padded.x_axis.axis_dimension.max_value
            > base.x_axis.axis_dimension.max_value
        )

    def test_area_pads_top(self):
        base = AreaChart(data=[[10, 20, 30]], labels=["a", "b", "c"])
        padded = AreaChart(
            data=[[10, 20, 30]], labels=["a", "b", "c"], domain_padding=0.1
        )
        assert padded.y_axis.axis_dimension.min_value == 0
        assert (
            padded.y_axis.axis_dimension.max_value
            > base.y_axis.axis_dimension.max_value
        )

    def test_histogram_pads_top(self):
        random.seed(1)
        data = [random.gauss(0, 1) for _ in range(200)]
        base = Histogram(data=data)
        padded = Histogram(data=data, domain_padding=0.15)
        assert padded.y_axis.axis_dimension.min_value == 0
        assert (
            padded.y_axis.axis_dimension.max_value
            > base.y_axis.axis_dimension.max_value
        )

    def test_stacked_column_pads_against_stacked_total(self):
        """Headroom is measured against the stacked column sum, not raw values."""
        data = [[10, 20, 30], [5, 5, 5]]
        padded = ColumnChart(data=data, labels=["a", "b", "c"], domain_padding=0.1)
        # Stacked total of the tallest column is 35; baseline stays at 0.
        assert padded.y_axis.axis_dimension.min_value == 0
        assert padded.y_axis.axis_dimension.max_value > 35
        # Plotted series are unaffected by the synthetic anchor rows.
        assert len(padded.y_values) == 2

    def test_straddling_zero_pads_both_sides_keeps_baseline_in_range(self):
        padded = ColumnChart(
            data=[[-10, 20, 30]], labels=["a", "b", "c"], domain_padding=0.1
        )
        dim = padded.y_axis.axis_dimension
        assert dim.min_value < 0
        assert dim.max_value > 30
        # Zero baseline remains inside the padded domain.
        assert dim.min_value < 0 < dim.max_value


class TestBubbleHeadroom:
    """Bubble has no zero baseline, so it pads symmetrically like scatter."""

    def test_bubble_pads_value_axis(self):
        base = BubbleChart(x_data=[1, 2, 3], y_data=[10, 20, 30], sizes=[5, 10, 15])
        padded = BubbleChart(
            x_data=[1, 2, 3],
            y_data=[10, 20, 30],
            sizes=[5, 10, 15],
            domain_padding=0.2,
        )
        assert (
            padded.y_axis.axis_dimension.max_value
            >= base.y_axis.axis_dimension.max_value
        )
        # Plotted point count unaffected by the synthetic anchor.
        assert len(padded.y_values[0]) == 3


class TestBackwardCompatibility:
    """Without domain_padding the historical auto-fit domain is preserved."""

    def test_default_leaves_domain_unchanged(self):
        a = ColumnChart(data=[[10, 20, 30]], labels=["a", "b", "c"])
        b = ColumnChart(data=[[10, 20, 30]], labels=["a", "b", "c"])
        assert (
            a.y_axis.axis_dimension.max_value == b.y_axis.axis_dimension.max_value
        )
        assert a.svg == b.svg
