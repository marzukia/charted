"""PieChart unit tests - Happy Path and Sad Path testing.

This module contains dedicated tests for PieChart functionality.
"""

import pytest
from charted.charts.pie import PieChart


class TestPieChartHappyPath:
    """Happy path tests for PieChart."""

    def test_basic_pie_chart(self):
        """Test basic pie chart with simple data."""
        chart = PieChart(data=[10, 20, 30], width=400, height=400)
        svg = chart.to_string()
        assert "<path" in svg.lower()
        assert "svg" in svg.lower()

    def test_donut_chart(self):
        """Test donut chart mode with inner hole."""
        chart = PieChart(
            data=[10, 20, 30],
            width=400,
            height=400,
            donut=True,
            donut_radius=0.5,
        )
        svg = chart.to_string()
        assert "<path" in svg.lower()
        assert "svg" in svg.lower()

    def test_pie_chart_with_title(self):
        """Test pie chart with title."""
        chart = PieChart(
            data=[10, 20, 30],
            width=400,
            height=400,
            title="My Pie Chart",
        )
        svg = chart.to_string()
        assert "My Pie Chart" in svg

    def test_pie_chart_single_slice(self):
        """Test pie chart with single data point."""
        chart = PieChart(data=[100], width=400, height=400)
        svg = chart.to_string()
        assert "<path" in svg.lower()

    def test_pie_chart_to_file(self):
        """Test saving pie chart to file."""
        chart = PieChart(data=[10, 20, 30], width=400, height=400)
        chart.to_file("/tmp/test_pie_chart.svg")
        with open("/tmp/test_pie_chart.svg") as f:
            content = f.read()
        assert "<path" in content.lower()

    def test_pie_chart_custom_colors(self):
        """Test pie chart with many slices (cycles through colors)."""
        chart = PieChart(
            data=[10] * 10,
            width=500,
            height=500,
        )
        svg = chart.to_string()
        assert svg.count("<path") == 10

    def test_pie_chart_custom_start_angle(self):
        """Test pie chart with custom start angle."""
        chart = PieChart(
            data=[50, 50],
            width=400,
            height=400,
            start_angle=180,
        )
        svg = chart.to_string()
        assert "<path" in svg.lower()

    def test_pie_chart_custom_dimensions(self):
        """Test pie chart with custom dimensions."""
        chart = PieChart(
            data=[25, 75],
            width=800,
            height=600,
        )
        svg = chart.to_string()
        assert 'width="800"' in svg
        assert 'height="600"' in svg


class TestPieChartSadPath:
    """Sad path tests for PieChart edge cases and error conditions."""

    def test_pie_chart_zero_values(self):
        """Test pie chart handles zero values gracefully."""
        chart = PieChart(data=[0, 0, 0], width=400, height=400)
        svg = chart.to_string()
        assert "svg" in svg.lower()

    def test_pie_chart_mixed_zero_and_positive(self):
        """Test pie chart with mix of zero and positive values."""
        chart = PieChart(data=[0, 50, 0, 50], width=400, height=400)
        svg = chart.to_string()
        assert "<path" in svg.lower()

    def test_pie_chart_empty_data(self):
        """Test that empty data creates valid (empty) SVG."""
        chart = PieChart(data=[], width=400, height=400)
        svg = chart.to_string()
        assert "svg" in svg.lower()

    def test_pie_chart_donut_radius_clamped(self):
        """Test that donut_radius is clamped to valid range."""
        chart = PieChart(
            data=[50, 50],
            width=400,
            height=400,
            donut=True,
            donut_radius=2.0,
        )
        assert chart.donut_radius == 1.0

        chart2 = PieChart(
            data=[50, 50],
            width=400,
            height=400,
            donut=True,
            donut_radius=-1.0,
        )
        assert chart2.donut_radius == 0.0
