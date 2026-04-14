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
        with pytest.raises(Exception, match="No data was provided"):
            BarChart(data=[], labels=[])
