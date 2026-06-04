"""Tests for the opt-in value-label system (issue #59).

Covers the number/percent/currency formatter plus wiring into bar, column,
pie, scatter, bubble, histogram, and box charts. Default-off behaviour is
verified so existing renders are unchanged.
"""

from __future__ import annotations

from charted import (
    BarChart,
    BoxPlot,
    BubbleChart,
    ColumnChart,
    Histogram,
    PieChart,
    ScatterChart,
)
from charted.utils.value_format import format_value


class TestFormatValue:
    def test_number_grouping_and_trim(self):
        assert format_value(1234.0, "number") == "1,234"
        assert format_value(1234.5, "number") == "1,234.5"

    def test_percent_scales_by_default(self):
        assert format_value(0.25, "percent") == "25%"
        assert format_value(25, "percent", percent_scale=False) == "25%"

    def test_currency_symbol_and_decimals(self):
        assert format_value(1234.5, "currency", decimals=2) == "$1,234.50"
        assert format_value(50, "currency", currency_symbol="€") == "€50"

    def test_negative_sign_outside_symbol(self):
        assert format_value(-12.5, "currency") == "-$12.5"
        assert format_value(-0.1, "percent") == "-10%"

    def test_prefix_suffix(self):
        assert format_value(5, "number", prefix="~", suffix=" units") == "~5 units"

    def test_unknown_format_raises(self):
        import pytest

        with pytest.raises(ValueError):
            format_value(1, "binary")


class TestValueLabelsWiring:
    def test_column_value_labels_appear(self):
        chart = ColumnChart(data=[10, 25, 40], value_labels="number")
        svg = chart.svg
        assert ">10<" in svg and ">25<" in svg and ">40<" in svg

    def test_column_off_by_default_unchanged(self):
        plain = ColumnChart(data=[10, 25, 40]).svg
        # No synthesized value text when value_labels is omitted.
        assert ">25<" not in plain

    def test_bar_currency_labels(self):
        chart = BarChart(data=[100, 250], value_labels="currency")
        svg = chart.svg
        assert "$100" in svg and "$250" in svg

    def test_pie_percent_labels(self):
        chart = PieChart(data=[25, 75], value_labels="percent")
        svg = chart.svg
        # 25 of 100 => 25%, shown inside the slice.
        assert "25%" in svg

    def test_scatter_number_labels(self):
        chart = ScatterChart(
            x_data=[1, 2, 3], y_data=[10, 20, 30], value_labels="number"
        )
        svg = chart.svg
        assert ">10<" in svg

    def test_bubble_inherits_value_labels(self):
        chart = BubbleChart(
            x_data=[1, 2],
            y_data=[5, 15],
            sizes=[3, 8],
            value_labels="number",
        )
        svg = chart.svg
        assert ">15<" in svg

    def test_histogram_value_labels(self):
        chart = Histogram(data=[1, 1, 2, 3, 3, 3], bins=3, value_labels="number")
        svg = chart.svg
        # The tallest bin (value 3 appears 3 times) shows a "3" count label.
        assert ">3<" in svg

    def test_box_median_label(self):
        chart = BoxPlot(data=[[1, 2, 3, 4, 5]], value_labels="number")
        svg = chart.svg
        # Median of 1..5 is 3.
        assert ">3<" in svg

    def test_dict_config_decimals(self):
        chart = ColumnChart(
            data=[10.5], value_labels={"format": "currency", "decimals": 2}
        )
        assert "$10.50" in chart.svg

    def test_collision_auto_hide(self):
        # Many near-equal values in a narrow chart force label collisions; the
        # auto-hide drops some so the rendered count is below the data count.
        data = [50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
        chart = ColumnChart(data=data, width=200, height=200, value_labels="number")
        rendered = chart.svg.count(">50<")
        assert 0 < rendered < len(data)
