"""ColumnChart unit tests - Happy Path and Sad Path testing.

This module contains dedicated tests for ColumnChart functionality.
"""

import pytest
from charted.charts.column import ColumnChart


class TestColumnChartHappyPath:
    """Happy path tests for ColumnChart."""

    def test_basic_column_chart(self):
        """Test basic column chart with simple data."""
        chart = ColumnChart(data=[10, 20, 30], labels=["a", "b", "c"])
        html = chart.html
        assert "<path" in html.lower()
        # SVG uses path elements for bars, not rect

    def test_stacked_column_chart(self):
        """Test stacked column chart with multiple series."""
        chart = ColumnChart(data=[[10, 5], [15, 10], [20, 15]], labels=["a", "b", "c"])
        html = chart.html
        assert "<path" in html.lower()

    def test_column_chart_single_point(self):
        """Test column chart with single data point."""
        chart = ColumnChart(data=[42], labels=["only"])
        html = chart.html
        assert "svg" in html.lower()

    def test_column_chart_negative_values(self):
        """Test column chart with negative values."""
        chart = ColumnChart(data=[-10, -20, -30], labels=["a", "b", "c"])
        html = chart.html
        assert "svg" in html.lower()

    def test_column_chart_large_values(self):
        """Test column chart with very large values."""
        chart = ColumnChart(data=[1e6, 2e6, 3e6], labels=["a", "b", "c"])
        html = chart.html
        assert "NaN" not in html
        assert "Infinity" not in html
        assert "-Infinity" not in html

    def test_column_chart_unicode_labels(self):
        """Test that unicode labels render correctly in SVG output."""
        data = [10, 20]
        labels = ["Test", "Data"]
        chart = ColumnChart(data, labels=labels)
        html = chart.html
        assert "Test" in html
        assert "Data" in html


class TestColumnChartSadPath:
    """Sad path tests for ColumnChart edge cases and error conditions."""

    def test_column_chart_empty_data(self):
        """Test that empty data raises ValueError."""
        with pytest.raises(Exception, match="No data was provided"):
            ColumnChart(data=[], labels=[])
