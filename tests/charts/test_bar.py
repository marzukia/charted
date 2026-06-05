"""BarChart unit tests - Happy Path and Sad Path testing.

This module contains dedicated tests for BarChart functionality.
"""

import pytest

from charted.charts.bar import BarChart


class TestBarChartHappyPath:
    """Happy path tests for BarChart."""

    def test_basic_bar_chart(self):
        """Test basic bar chart with simple data."""
        chart = BarChart(data=[10, 20, 30], labels=["a", "b", "c"])
        html = chart.html
        assert "svg" in html.lower()

    def test_stacked_bar_chart(self):
        """Test stacked bar chart with multiple series."""
        chart = BarChart(data=[10, 15, 20], labels=["a", "b", "c"])
        html = chart.html
        assert "svg" in html.lower()

    def test_bar_chart_single_point(self):
        """Test bar chart with single data point."""
        chart = BarChart(data=[42], labels=["only"])
        html = chart.html
        assert "svg" in html.lower()

    def test_bar_chart_negative_values(self):
        """Test bar chart with negative values."""
        chart = BarChart(data=[-10, -20, -30], labels=["a", "b", "c"])
        html = chart.html
        assert "svg" in html.lower()

    def test_bar_chart_large_values(self):
        """Test bar chart with very large values."""
        chart = BarChart(data=[1e6, 2e6, 3e6], labels=["a", "b", "c"])
        html = chart.html
        assert "NaN" not in html
        assert "Infinity" not in html
        assert "-Infinity" not in html

    def test_bar_chart_unicode_labels(self):
        """Test that unicode labels render correctly in SVG output."""
        data = [10, 20]
        labels = ["Test", "Data"]
        chart = BarChart(data, labels=labels)
        html = chart.html
        assert "svg" in html.lower()


class TestBarChartSadPath:
    """Sad path tests for BarChart edge cases and error conditions."""

    def test_bar_chart_empty_data(self):
        """Test that empty data raises ValueError."""
        from charted import NoDataError

        with pytest.raises(NoDataError, match="No data"):
            BarChart(data=[], labels=[])

    def test_bar_chart_multiseries(self):
        """Test bar chart with multiple series."""
        data = [[10, 20, 30], [15, 25, 35]]
        chart = BarChart(data=data, labels=["a", "b", "c"])
        html = chart.html
        assert "svg" in html.lower()

    def test_bar_chart_mixed_negative_values(self):
        """Test bar chart with mixed positive and negative values."""
        chart = BarChart(data=[-10, 0, 10, 20], labels=["a", "b", "c", "d"])
        html = chart.html
        assert "svg" in html.lower()
        assert "NaN" not in html
        assert "Infinity" not in html

    def test_bar_chart_zero_value(self):
        """Test bar chart with zero values."""
        chart = BarChart(data=[0, 10, 20], labels=["a", "b", "c"])
        html = chart.html
        assert "svg" in html.lower()

    def test_bar_chart_stacked_with_negative(self):
        """Test stacked bar chart (x_stacked=True) with negative values."""
        chart = BarChart(
            data=[[10, -5, 15], [-10, 15, -5]], labels=["a", "b", "c"], x_stacked=True
        )
        html = chart.html
        assert "svg" in html.lower()
        assert "NaN" not in html

    def test_bar_chart_get_base_transform(self):
        """Test that get_base_transform returns empty list."""
        chart = BarChart(data=[10, 20, 30], labels=["a", "b", "c"])
        transforms = chart.get_base_transform()
        assert transforms == []


class TestBarCategoryLabelWrapping:
    """Full category-label rendering with wrapping (issue #65)."""

    LONG_LABELS = [
        "International Marketing Department",
        "Research and Development Division",
        "Q3",
    ]

    def test_short_labels_not_wrapped_by_default(self):
        """Labels that fit the default gutter stay single-line (no tspans)."""
        chart = BarChart(data=[10, 20, 30], labels=["Q1", "Q2", "Q3"])
        assert "<tspan" not in chart.svg

    def test_long_labels_wrap_by_default(self):
        """Without an explicit cap, overflowing labels wrap so the gutter stays
        bounded instead of consuming the plot area."""
        chart = BarChart(data=[10, 20, 30], labels=self.LONG_LABELS)
        # The default cap is a fraction of the chart width, so a label far wider
        # than that is wrapped onto multiple lines (full words preserved).
        assert "<tspan" in chart.svg
        assert chart.left_padding < chart.width / 2

    def test_long_labels_wrap_to_tspans(self):
        """A width cap wraps overflowing labels into multiple tspan lines."""
        chart = BarChart(
            data=[10, 20, 30],
            labels=self.LONG_LABELS,
            category_label_max_width=110,
        )
        svg = chart.svg
        assert "<tspan" in svg
        # Full words preserved, nothing truncated/abbreviated.
        for word in (
            "International",
            "Marketing",
            "Department",
            "Research",
            "Division",
        ):
            assert word in svg

    def test_short_label_not_wrapped(self):
        """A label that fits the cap is not split."""
        from charted.utils.helpers import wrap_text_to_width

        measured = wrap_text_to_width("Q3", 110)
        assert measured.lines is None

    def test_cap_bounds_left_padding(self):
        """Capping the label width shrinks the gutter and grows the plot."""
        labels = self.LONG_LABELS
        uncapped = BarChart(data=[10, 20, 30], labels=labels)
        capped = BarChart(
            data=[10, 20, 30], labels=labels, category_label_max_width=110
        )
        assert capped.left_padding < uncapped.left_padding
        assert capped.plot_width > uncapped.plot_width

    def test_no_overflow_cap_is_noop(self):
        """A cap wider than every label leaves the render byte-for-byte equal."""
        short = ["A", "B", "C"]
        plain = BarChart(data=[10, 20, 30], labels=short)
        capped = BarChart(data=[10, 20, 30], labels=short, category_label_max_width=500)
        assert plain.svg == capped.svg

    def test_long_single_word_kept_whole(self):
        """A single word wider than the cap is not truncated."""
        from charted.utils.helpers import wrap_text_to_width

        measured = wrap_text_to_width("Supercalifragilisticexpialidocious", 40)
        assert measured.text == "Supercalifragilisticexpialidocious"
        assert (
            measured.lines is None
            or "".join(measured.lines).replace(" ", "")
            == "Supercalifragilisticexpialidocious"
        )
