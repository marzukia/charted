"""LineChart unit tests - Happy Path and Sad Path testing.

This module contains dedicated tests for LineChart functionality.
"""

import pytest

from charted.charts.line import LineChart


class TestLineChartHappyPath:
    """Happy path tests for LineChart."""

    def test_basic_line_chart(self):
        """Test basic line chart with simple data."""
        chart = LineChart(data=[10, 20, 30], labels=["a", "b", "c"])
        html = chart.html
        assert "svg" in html.lower()
        assert "<circle" in html.lower()  # LineChart uses circles for points

    def test_multi_series_line_chart(self):
        """Test line chart with multiple series."""
        chart = LineChart(
            data=[[10, 20, 30], [15, 25, 35]],
            labels=["a", "b", "c"],
            series_names=["Series 1", "Series 2"],
        )
        html = chart.html
        assert "svg" in html.lower()

    def test_line_chart_single_point(self):
        """Test line chart with single data point."""
        chart = LineChart(data=[42], labels=["only"])
        html = chart.html
        assert "svg" in html.lower()

    def test_line_chart_negative_values(self):
        """Test line chart with negative values."""
        chart = LineChart(data=[-10, -20, -30], labels=["a", "b", "c"])
        html = chart.html
        assert "svg" in html.lower()

    def test_line_chart_large_values(self):
        """Test line chart with very large values."""
        chart = LineChart(data=[1e6, 2e6, 3e6], labels=["a", "b", "c"])
        html = chart.html
        assert "NaN" not in html
        assert "Infinity" not in html
        assert "-Infinity" not in html


class TestLineChartSadPath:
    """Sad path tests for LineChart edge cases and error conditions."""

    def test_line_chart_empty_data(self):
        """Test that empty data raises ValueError."""
        with pytest.raises(Exception, match="No data was provided"):
            LineChart(data=[], labels=[])


class TestLineChartMarkerRendering:
    """Tests for marker rendering logic."""

    def test_markers_with_explicit_show_true(self):
        """Test markers render when show_markers=True."""
        chart = LineChart(
            data=[10, 20, 30],
            labels=["a", "b", "c"],
            series_styles=[
                {"marker_shape": "circle", "marker_size": 5, "show_markers": True}
            ],
        )
        html = chart.html
        # Should have markers (circles)
        assert "<circle" in html.lower()

    def test_no_markers_with_explicit_show_false(self):
        """Test markers don't render when show_markers=False."""
        chart = LineChart(
            data=[10, 20, 30],
            labels=["a", "b", "c"],
            series_styles=[
                {"marker_shape": "circle", "marker_size": 5, "show_markers": False}
            ],
        )
        html = chart.html
        # Should NOT have markers
        assert "<circle" not in html.lower()

    def test_markers_default_behavior(self):
        """Test default marker behavior (shape and size provided)."""
        chart = LineChart(
            data=[10, 20, 30],
            labels=["a", "b", "c"],
            series_styles=[{"marker_shape": "circle", "marker_size": 5}],
        )
        html = chart.html
        # Should have markers by default
        assert "<circle" in html.lower()
