"""ScatterChart unit tests - Happy Path and Sad Path testing.

This module contains dedicated tests for ScatterChart functionality.
"""

import pytest

from charted.charts.scatter import ScatterChart


class TestScatterChartHappyPath:
    """Happy path tests for ScatterChart."""

    def test_basic_scatter_chart(self):
        """Test basic scatter chart with simple data."""
        chart = ScatterChart(x_data=[0, 1, 2], y_data=[10, 20, 30])
        html = chart.html
        assert "<circle" in html.lower()

    def test_multi_series_scatter_chart(self):
        """Test scatter chart with multiple series."""
        chart = ScatterChart(x_data=[[0, 1], [0, 1]], y_data=[[10, 20], [15, 25]])
        html = chart.html
        assert "<circle" in html.lower()

    def test_scatter_chart_single_point(self):
        """Test scatter chart with single data point."""
        chart = ScatterChart(x_data=[0, 1], y_data=[42, 50])
        html = chart.html
        assert "svg" in html.lower()

    def test_scatter_chart_negative_values(self):
        """Test scatter chart with negative values."""
        chart = ScatterChart(x_data=[0, 1, 2], y_data=[-10, -20, -30])
        html = chart.html
        assert "<circle" in html.lower()

    def test_scatter_chart_large_values(self):
        """Test scatter chart with very large values."""
        chart = ScatterChart(x_data=[0, 1, 2], y_data=[1e6, 2e6, 3e6])
        html = chart.html
        assert "NaN" not in html
        assert "Infinity" not in html
        assert "-Infinity" not in html


class TestScatterChartSadPath:
    """Sad path tests for ScatterChart edge cases and error conditions."""

    def test_scatter_chart_empty_data(self):
        """Test that empty data raises ValueError."""
        with pytest.raises(Exception, match="No data was provided"):
            ScatterChart(x_data=[], y_data=[])


class TestScatterChartScales:
    """Tests for log and time scales on ScatterChart."""

    def test_scatter_log_x_scale(self):
        """x_scale='log' renders and tick labels are decade values."""
        chart = ScatterChart(
            x_data=[1, 10, 100, 1000],
            y_data=[5, 8, 12, 15],
            x_scale="log",
        )
        html = chart.html
        assert "<circle" in html.lower()
        assert ">10<" in html
        assert ">100<" in html
        assert ">1000<" in html
        assert chart.to_config()["x_scale"] == "log"
        assert chart.describe()["scales"]["x"] == "log"

    def test_scatter_log_x_scale_rejects_nonpositive(self):
        with pytest.raises(ValueError):
            ScatterChart(x_data=[0, 10, 100], y_data=[1, 2, 3], x_scale="log").html
