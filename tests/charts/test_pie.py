"""PieChart unit tests - Happy Path and Sad Path testing.

This module contains dedicated tests for PieChart functionality.
"""

import pytest
from charted.charts.pie import PieChart


class TestPieChartHappyPath:
    """Happy path tests for PieChart."""

    def test_basic_pie_chart(self):
        """Test basic pie chart with simple data."""
        chart = PieChart(values=[10, 20, 30], labels=["a", "b", "c"])
        html = chart.html
        assert "svg" in html.lower()

    def test_pie_chart_with_labels(self):
        """Test pie chart with category labels."""
        chart = PieChart(
            values=[25, 35, 20, 20], labels=["Electronics", "Clothing", "Food", "Other"]
        )
        html = chart.html
        assert "svg" in html.lower()

    def test_pie_chart_single_value(self):
        """Test pie chart with single data point (100% slice)."""
        chart = PieChart(values=[100], labels=["Only"])
        html = chart.html
        assert "svg" in html.lower()

    def test_pie_chart_two_equal_values(self):
        """Test pie chart with two equal values (50/50 split)."""
        chart = PieChart(values=[50, 50], labels=["A", "B"])
        html = chart.html
        assert "svg" in html.lower()

    def test_pie_chart_with_custom_colors(self):
        """Test pie chart with custom colors."""
        chart = PieChart(
            values=[10, 20, 30],
            labels=["a", "b", "c"],
            colors=["#FF0000", "#00FF00", "#0000FF"],
        )
        html = chart.html
        assert "svg" in html.lower()

    def test_pie_chart_with_custom_title(self):
        """Test pie chart with custom title."""
        chart = PieChart(
            values=[10, 20, 30], labels=["a", "b", "c"], title="Sales Distribution"
        )
        html = chart.html
        assert "Sales Distribution" in html


class TestPieChartDoughnutMode:
    """Tests for doughnut mode (inner_radius parameter)."""

    def test_doughnut_chart(self):
        """Test doughnut chart with inner_radius > 0."""
        chart = PieChart(values=[10, 20, 30], labels=["a", "b", "c"], inner_radius=0.3)
        html = chart.html
        assert "svg" in html.lower()

    def test_doughnut_chart_hollow(self):
        """Test doughnut chart with inner_radius close to 1."""
        chart = PieChart(
            values=[25, 25, 25, 25], labels=["a", "b", "c", "d"], inner_radius=0.8
        )
        html = chart.html
        assert "svg" in html.lower()


class TestPieChartSadPath:
    """Sad path tests for PieChart edge cases and error conditions."""

    def test_pie_chart_empty_data(self):
        """Test that empty data raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            PieChart(values=[])

    def test_pie_chart_all_zeros(self):
        """Test that all zero values raises ValueError."""
        with pytest.raises(ValueError, match="greater than 0"):
            PieChart(values=[0, 0, 0])

    def test_pie_chart_negative_value(self):
        """Test that negative values raise ValueError."""
        with pytest.raises(ValueError, match="not allowed"):
            PieChart(values=[10, -5, 20])

    def test_pie_chart_nan_value(self):
        """Test that NaN values raise ValueError."""
        with pytest.raises(ValueError, match="not allowed"):
            PieChart(values=[10, float("nan"), 20])

    def test_pie_chart_zero_values(self):
        """Test that zero values are handled (skipped in rendering)."""
        # Zero values should be allowed but contribute nothing
        chart = PieChart(values=[0, 10, 20], labels=["zero", "a", "b"])
        html = chart.html
        assert "svg" in html.lower()

    def test_pie_chart_inner_radius_too_small(self):
        """Test that inner_radius < 0 raises ValueError."""
        with pytest.raises(ValueError, match="inner_radius"):
            PieChart(values=[10, 20], inner_radius=-0.1)

    def test_pie_chart_inner_radius_too_large(self):
        """Test that inner_radius > 1 raises ValueError."""
        with pytest.raises(ValueError, match="inner_radius"):
            PieChart(values=[10, 20], inner_radius=1.5)

    def test_pie_chart_mixed_types(self):
        """Test that non-numeric values raise TypeError."""
        with pytest.raises(TypeError):
            PieChart(values=[10, "twenty", 30])


class TestPieChartAngleCalculations:
    """Tests for angle calculation accuracy."""

    def test_angles_sum_to_360(self):
        """Test that all slice angles sum to approximately 360 degrees."""
        values = [10, 20, 30, 40]  # Total = 100
        chart = PieChart(values=values)

        total_angle = sum(end - start for start, end in chart._angles)
        assert abs(total_angle - 360) < 0.01

    def test_single_value_full_circle(self):
        """Test that a single value creates a full 360-degree slice."""
        chart = PieChart(values=[100])
        assert len(chart._angles) == 1
        start, end = chart._angles[0]
        # Single value creates a full circle (0 to 360)
        assert start == 0
        assert abs(end - 360) < 0.01

    def test_proportional_angles(self):
        """Test that angles are proportional to values."""
        values = [10, 20, 30, 40]  # 100 total, so 10% = 36 degrees each
        chart = PieChart(values=values)

        expected_angles = [36, 72, 108, 144]  # Cumulative
        for i, (start, end) in enumerate(chart._angles):
            expected_end = expected_angles[i]
            assert abs(end - expected_end) < 0.01
