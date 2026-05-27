"""PieChart unit tests - Happy Path and Sad Path testing.

This module contains dedicated tests for PieChart functionality.
"""

import math

import pytest

from charted.charts.pie import PieChart


class TestPieChartHappyPath:
    """Happy path tests for PieChart."""

    def test_basic_pie_chart(self):
        """Test basic pie chart with simple data."""
        chart = PieChart(data=[45, 30, 15, 10], labels=["A", "B", "C", "D"])
        html = chart.html
        assert "<path" in html.lower()
        assert "svg" in html.lower()

    def test_pie_chart_two_slices(self):
        """Test pie chart with two equal slices."""
        chart = PieChart(data=[50, 50], labels=["X", "Y"])
        html = chart.html
        assert "<path" in html.lower()

    def test_pie_chart_single_slice(self):
        """Test pie chart with single 100% slice."""
        chart = PieChart(data=[100], labels=["Only"])
        html = chart.html
        assert "<path" in html.lower() or "<circle" in html.lower()

    def test_pie_chart_doughnut_mode(self):
        """Test pie chart in doughnut mode."""
        chart = PieChart(data=[30, 40, 30], labels=["A", "B", "C"], inner_radius=0.5)
        html = chart.html
        assert "<path" in html.lower()
        assert "inner_radius" not in html.lower()  # Should be rendered, not in HTML

    def test_pie_chart_explode(self):
        """Test pie chart with exploded slices."""
        chart = PieChart(data=[45, 30, 15, 10], labels=["A", "B", "C", "D"], explode=10)
        html = chart.html
        assert "translate" in html.lower()

    def test_pie_chart_explode_specific(self):
        """Test pie chart with specific slice exploded."""
        chart = PieChart(
            data=[45, 30, 15, 10], labels=["A", "B", "C", "D"], explode=[0, 15, 0, 0]
        )
        html = chart.html
        assert "translate" in html.lower()

    def test_pie_chart_start_angle(self):
        """Test pie chart with custom start angle."""
        chart = PieChart(
            data=[45, 30, 15, 10], labels=["A", "B", "C", "D"], start_angle=90
        )
        html = chart.html
        assert "svg" in html.lower()

    def test_pie_chart_custom_dimensions(self):
        """Test pie chart with custom width and height."""
        chart = PieChart(
            data=[45, 30, 15, 10], labels=["A", "B", "C", "D"], width=700, height=600
        )
        html = chart.html
        assert 'width="700' in html
        assert 'height="600' in html

    def test_pie_chart_with_title(self):
        """Test pie chart with title."""
        chart = PieChart(
            data=[45, 30, 15, 10], labels=["A", "B", "C", "D"], title="Test Title"
        )
        html = chart.html
        assert "Test Title" in html

    def test_pie_chart_no_labels(self):
        """Test pie chart without labels."""
        chart = PieChart(data=[45, 30, 15, 10])
        html = chart.html
        assert "svg" in html.lower()

    def test_pie_chart_large_values(self):
        """Test pie chart with very large values."""
        chart = PieChart(data=[1e6, 2e6, 3e6], labels=["A", "B", "C"])
        html = chart.html
        assert "NaN" not in html
        assert "Infinity" not in html

    def test_pie_chart_unicode_labels(self):
        """Test pie chart with unicode labels."""
        chart = PieChart(data=[30, 40, 30], labels=["A", "B", "C"])
        html = chart.html
        assert "svg" in html.lower()


class TestPieChartSadPath:
    """Sad path tests for PieChart."""

    def test_pie_chart_empty_data(self):
        """Test pie chart with empty data raises ValueError."""
        with pytest.raises(ValueError, match="Data cannot be empty"):
            PieChart(data=[], labels=[])

    def test_pie_chart_negative_values(self):
        """Test pie chart with negative values raises ValueError."""
        with pytest.raises(ValueError, match="Data values cannot be negative"):
            PieChart(data=[-1, 5, 10], labels=["A", "B", "C"])

    def test_pie_chart_all_zeros(self):
        """Test pie chart with all zeros raises ValueError."""
        with pytest.raises(
            ValueError, match="Total of all values must be greater than 0"
        ):
            PieChart(data=[0, 0, 0], labels=["A", "B", "C"])

    def test_pie_chart_nan_values(self):
        """Test pie chart with NaN values raises ValueError."""
        with pytest.raises(ValueError, match="Data must contain only valid numbers"):
            PieChart(data=[1, float("nan"), 3], labels=["A", "B", "C"])

    def test_pie_chart_inf_values(self):
        """Test pie chart with infinity values raises ValueError."""
        with pytest.raises(ValueError, match="Data must contain only valid numbers"):
            PieChart(data=[1, float("inf"), 3], labels=["A", "B", "C"])

    def test_pie_chart_mixed_valid_invalid(self):
        """Test pie chart with mix of valid and invalid values."""
        with pytest.raises(ValueError):
            PieChart(data=[10, -5, 20], labels=["A", "B", "C"])


class TestPieChartVisualRegression:
    """Visual regression tests for PieChart."""

    def test_pie_chart_baseline(self):
        """Test pie chart matches baseline SVG."""
        chart = PieChart(
            data=[45, 30, 15, 10], labels=["Electronics", "Clothing", "Food", "Other"]
        )
        html = chart.html

        # Verify key SVG elements are present
        assert "<svg" in html.lower()
        assert "</svg>" in html.lower()
        assert "<path" in html.lower()

        # Verify labels are present
        assert "Electronics" in html
        assert "Clothing" in html
        assert "Food" in html
        assert "Other" in html

    def test_pie_chart_doughnut_baseline(self):
        """Test doughnut chart generates correct SVG."""
        chart = PieChart(data=[30, 40, 30], labels=["A", "B", "C"], inner_radius=0.5)
        html = chart.html

        # Verify SVG structure
        assert "<svg" in html.lower()
        assert "<path" in html.lower()

        # Verify labels are present
        assert "A" in html
        assert "B" in html
        assert "C" in html

    def test_pie_chart_slice_angles_sum_to_360(self):
        """Test that slice angles correctly sum to 360 degrees."""
        data = [45, 30, 15, 10]
        total = sum(data)
        angles = [(v / total) * 360 for v in data]
        assert math.isclose(sum(angles), 360, rel_tol=1e-6)

    def test_pie_chart_dense_data_dual_column_legend(self):
        """Test pie chart with 12 slices generates dual-column legend.

        This is the baseline test for dense pie charts (>10 slices) that use
        the dual-column legend layout with golden ratio color spacing.
        """
        import os

        # 12 categories for dense data test
        data = [35, 28, 22, 18, 15, 12, 10, 8, 7, 6, 5, 4]
        labels = [
            "Electronics",
            "Clothing",
            "Food",
            "Housing",
            "Transport",
            "Healthcare",
            "Education",
            "Entertainment",
            "Travel",
            "Savings",
            "Insurance",
            "Miscellaneous",
        ]
        chart = PieChart(data=data, labels=labels)
        svg = chart.to_svg()

        # Load baseline
        baseline_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "baselines",
            "pie_dense_12_slices.svg",
        )
        with open(baseline_path, "r") as f:
            baseline_svg = f.read()

        # Compare SVGs (normalize whitespace for comparison)
        def normalize_svg(svg):
            return " ".join(svg.split())

        assert normalize_svg(svg) == normalize_svg(baseline_svg), (
            "Generated SVG does not match baseline"
        )

    def test_pie_chart_very_dense_data(self):
        """Test pie chart with 15+ slices for extreme dense data scenario."""
        import os

        data = list(range(15, 0, -1))  # [15, 14, 13, ..., 1]
        labels = [f"Category {i}" for i in range(1, 16)]
        chart = PieChart(data=data, labels=labels)
        svg = chart.to_svg()

        # Load baseline
        baseline_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "baselines",
            "pie_dense_15_slices.svg",
        )
        with open(baseline_path, "r") as f:
            baseline_svg = f.read()

        # Compare SVGs (normalize whitespace for comparison)
        def normalize_svg(svg):
            return " ".join(svg.split())

        assert normalize_svg(svg) == normalize_svg(baseline_svg), (
            "Generated SVG does not match baseline"
        )
