"""Tests for the shared, placement-aware series legend (issue #60).

The scatter chart's reserved-band legend was generalized into a mixin that
every multi-series chart can use. These tests cover the generalized behaviour
across line, column, box and pie, plus the backward-compatibility guarantees.
"""

import pytest

from charted.charts.box import BoxPlot
from charted.charts.column import ColumnChart
from charted.charts.line import LineChart
from charted.charts.pie import PieChart


def _two_series_line(**kwargs):
    return LineChart(
        data=[[1, 2, 3], [3, 2, 1]],
        labels=["a", "b", "c"],
        series_names=["Alpha", "Beta"],
        **kwargs,
    )


class TestSharedLegendLayout:
    """Reserved-band placement for axis charts."""

    def test_default_none_reserves_no_space(self):
        plain = _two_series_line()
        assert plain.layout.legend_position == "none"
        assert plain.layout.legend_extent == 0.0
        assert plain.right_padding == plain.h_padding * plain.width

    def test_right_legend_reserves_horizontal_space(self):
        with_legend = _two_series_line(legend="right")
        without = _two_series_line()
        assert with_legend.layout.legend_position == "right"
        assert with_legend.layout.legend_extent > 0
        assert with_legend.plot_width < without.plot_width
        html = with_legend.html
        assert "Alpha" in html and "Beta" in html

    def test_bottom_legend_reserves_vertical_space(self):
        with_legend = _two_series_line(legend="bottom")
        without = _two_series_line()
        assert with_legend.layout.legend_position == "bottom"
        assert with_legend.plot_height < without.plot_height

    def test_top_legend_reserves_vertical_space(self):
        with_legend = _two_series_line(legend="top")
        without = _two_series_line()
        assert with_legend.layout.legend_position == "top"
        assert with_legend.plot_height < without.plot_height

    def test_invalid_placement_raises(self):
        with pytest.raises(ValueError, match="Invalid legend placement"):
            _two_series_line(legend="sideways")

    def test_no_series_names_reserves_nothing(self):
        chart = LineChart(data=[[1, 2, 3]], legend="right")
        assert chart.layout.legend_position == "none"
        assert chart.layout.legend_extent == 0.0


class TestSharedLegendSwatches:
    """The default swatch is a coloured square chip."""

    def test_column_legend_draws_square_swatches(self):
        chart = ColumnChart(
            data=[[1, 2, 3], [3, 2, 1]],
            labels=["a", "b", "c"],
            series_names=["One", "Two"],
            colors=["#112233", "#445566"],
            legend="right",
        )
        html = chart.legend.html
        assert "One" in html and "Two" in html
        assert "#112233" in html and "#445566" in html
        assert "<rect" in html.lower()

    def test_box_chart_accepts_legend(self):
        chart = BoxPlot(
            data=[[1, 2, 3, 4], [2, 4, 6, 8]],
            labels=["x", "y"],
            series_names=["P", "Q"],
            legend="bottom",
        )
        assert chart.layout.legend_position == "bottom"
        assert "P" in chart.legend.html


class TestPieLegend:
    """Pie generalizes the legend and fixes the split box (opt-in)."""

    def test_pie_default_keeps_split_legend(self):
        """legend='none' leaves the historical split legend in place."""
        chart = PieChart(data=[25, 35, 40], labels=["A", "B", "C"])
        assert chart.layout.legend_position == "none"
        # The slice labels still render somewhere in the SVG.
        html = chart.html
        assert "A" in html and "B" in html and "C" in html

    def test_pie_single_box_reserves_band(self):
        """An explicit placement reserves a single consistent band."""
        chart = PieChart(
            data=[25, 35, 40],
            labels=["A", "B", "C"],
            legend="right",
        )
        assert chart.layout.legend_position == "right"
        assert chart.layout.legend_extent > 0
        legend = chart.legend
        assert legend is not None
        html = legend.html
        assert "A" in html and "B" in html and "C" in html
        # Single box: one swatch per slice (three squares).
        assert html.lower().count("<rect") == 3

    def test_pie_single_box_skips_split_legend(self):
        """With a placement legend, the dual-column split box is not drawn."""
        # A dense pie overspills (the tiny slices can't be labelled on-chart),
        # so the default no-placement case draws the legacy split legend; the
        # placement legend moves it out of representation entirely.
        labels = [f"Cat {i}" for i in range(12)]
        data = [30, 20, 15, 10, 8, 5, 4, 3, 2, 1, 1, 1]
        split = PieChart(data=data, labels=labels)
        single = PieChart(data=data, labels=labels, legend="right")
        # The legacy split legend lives inside representation(); the shared box
        # moves the legend out of representation entirely.
        assert split.representation.html.lower().count("<rect") > 0
        assert single.representation.html.lower().count("<rect") == 0
        # The single shared box draws exactly one swatch per slice.
        assert single.legend.html.lower().count("<rect") == 12
