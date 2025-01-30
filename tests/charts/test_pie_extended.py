"""Extended PieChart tests for improved coverage.

Covers doughnut mode, explode, series styles, and edge cases.
"""

import pytest

from charted import Theme
from charted.charts.pie import PieChart


class TestPieChartDoughnutMode:
    """Test doughnut mode (inner_radius > 0)."""

    def test_doughnut_basic(self):
        """Test basic doughnut chart."""
        chart = PieChart(data=[25, 35, 40], inner_radius=0.4)
        html = chart.html
        assert "<path" in html.lower()

    def test_doughnut_large_inner_radius(self):
        """Test doughnut with large inner radius."""
        chart = PieChart(data=[25, 35, 40], inner_radius=0.7)
        html = chart.html
        assert "<path" in html.lower()

    def test_doughnut_single_100_percent_slice(self):
        """Test doughnut with single 100% slice."""
        chart = PieChart(data=[100], inner_radius=0.5)
        html = chart.html
        assert "<path" in html.lower()

    def test_doughnut_with_labels(self):
        """Test doughnut chart with labels."""
        chart = PieChart(data=[25, 35, 40], labels=["A", "B", "C"], inner_radius=0.4)
        html = chart.html
        assert "A" in html
        assert "B" in html
        assert "C" in html


class TestPieChartExplode:
    """Test explode parameter for offsetting slices."""

    def test_explode_single_value(self):
        """Test explode with single value applied to all slices."""
        chart = PieChart(data=[25, 35, 40], explode=10)
        html = chart.html
        assert "<path" in html.lower()
        assert "translate" in html.lower()

    def test_explode_list(self):
        """Test explode with list of values."""
        chart = PieChart(data=[25, 35, 40], explode=[0, 10, 20])
        html = chart.html
        assert "<path" in html.lower()

    def test_explode_zero(self):
        """Test explode with zero (no offset)."""
        chart = PieChart(data=[25, 35, 40], explode=0)
        html = chart.html
        assert "<path" in html.lower()

    def test_explode_doughnut(self):
        """Test explode with doughnut mode."""
        chart = PieChart(data=[25, 35, 40], inner_radius=0.4, explode=15)
        html = chart.html
        assert "<path" in html.lower()


class TestPieChartStartAngle:
    """Test start_angle parameter."""

    def test_start_angle_zero(self):
        """Test default start angle (0 = top)."""
        chart = PieChart(data=[25, 35, 40], start_angle=0)
        html = chart.html
        assert "<path" in html.lower()

    def test_start_angle_ninety(self):
        """Test start angle of 90 degrees."""
        chart = PieChart(data=[25, 35, 40], start_angle=90)
        html = chart.html
        assert "<path" in html.lower()

    def test_start_angle_one_eighty(self):
        """Test start angle of 180 degrees."""
        chart = PieChart(data=[25, 35, 40], start_angle=180)
        html = chart.html
        assert "<path" in html.lower()

    def test_start_angle_negative(self):
        """Test negative start angle."""
        chart = PieChart(data=[25, 35, 40], start_angle=-45)
        html = chart.html
        assert "<path" in html.lower()


class TestPieChartSeriesStyles:
    """Test series_styles parameter for per-slice styling.

    Note: series_styles is currently accepted but not passed to super().__init__().
    This test documents the expected behavior when the bug is fixed.
    """

    def test_series_styles_parameter_accepted(self):
        """Test that series_styles parameter is accepted."""
        # This test verifies the parameter is accepted, even if not fully functional yet
        chart = PieChart(
            data=[25, 35, 40],
            series_styles=[{"fill": "#FF0000"}],
        )
        html = chart.html
        assert "<path" in html.lower()


class TestPieChartEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_slice_100_percent(self):
        """Test single slice that takes 100% of the pie."""
        chart = PieChart(data=[100])
        html = chart.html
        assert "<path" in html.lower()

    def test_two_slices_equal(self):
        """Test two equal slices (50/50)."""
        chart = PieChart(data=[50, 50])
        html = chart.html
        assert "<path" in html.lower()

    def test_many_slices(self):
        """Test pie with many slices (>10)."""
        data = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
        chart = PieChart(data=data)
        html = chart.html
        assert "<path" in html.lower()

    def test_many_slices_doughnut(self):
        """Test doughnut with many slices (triggers complementary colors)."""
        data = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
        chart = PieChart(data=data, inner_radius=0.3)
        html = chart.html
        assert "<path" in html.lower()

    def test_very_small_values(self):
        """Test pie with very small values."""
        chart = PieChart(data=[1e-10, 2e-10, 3e-10])
        html = chart.html
        assert "<path" in html.lower()

    def test_very_large_values(self):
        """Test pie with very large values."""
        chart = PieChart(data=[1e6, 2e6, 3e6])
        html = chart.html
        assert "<path" in html.lower()

    def test_decimal_values(self):
        """Test pie with decimal values."""
        chart = PieChart(data=[1.5, 2.5, 3.5])
        html = chart.html
        assert "<path" in html.lower()

    def test_mixed_integer_decimal(self):
        """Test pie with mixed integer and decimal values."""
        chart = PieChart(data=[1, 2.5, 3])
        html = chart.html
        assert "<path" in html.lower()


class TestPieChartValidation:
    """Test input validation."""

    def test_empty_data_raises(self):
        """Test that empty data raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            PieChart(data=[])

    def test_negative_values_raises(self):
        """Test that negative values raise ValueError."""
        with pytest.raises(ValueError, match="negative"):
            PieChart(data=[10, -20, 30])

    def test_zero_sum_raises(self):
        """Test that all-zero data raises ValueError."""
        with pytest.raises(ValueError, match="greater than 0"):
            PieChart(data=[0, 0, 0])

    def test_nan_values_raises(self):
        """Test that NaN values raise ValueError."""
        with pytest.raises(ValueError):
            PieChart(data=[10, float("nan"), 30])

    def test_infinity_values_raises(self):
        """Test that infinity values raise ValueError."""
        with pytest.raises(ValueError):
            PieChart(data=[10, float("inf"), 30])


class TestPieChartThemes:
    """Test theme integration."""

    def test_with_light_theme(self):
        """Test pie chart with light theme."""
        chart = PieChart(data=[25, 35, 40], theme="light")
        html = chart.html
        assert "<path" in html.lower()

    def test_with_dark_theme(self):
        """Test pie chart with dark theme."""
        chart = PieChart(data=[25, 35, 40], theme="dark")
        html = chart.html
        assert "<path" in html.lower()

    def test_with_custom_theme(self):
        """Test pie chart with custom theme."""
        custom_theme = Theme(
            colors=["#FF0000"], background_color="#000000", legend_font_color="#ffffff"
        )
        chart = PieChart(data=[25, 35, 40], theme=custom_theme)
        html = chart.html
        assert "<path" in html.lower()


class TestPieChartRendering:
    """Test rendering correctness."""

    def test_svg_structure_valid(self):
        """Test that generated SVG is valid."""
        chart = PieChart(data=[25, 35, 40])
        html = chart.html
        assert html.startswith("<svg")
        assert "</svg>" in html

    def test_chart_has_title(self):
        """Test pie chart with title."""
        chart = PieChart(data=[25, 35, 40], title="Sales Distribution")
        html = chart.html
        assert "Sales Distribution" in html

    def test_chart_custom_dimensions(self):
        """Test pie chart with custom dimensions."""
        chart = PieChart(data=[25, 35, 40], width=800, height=600)
        html = chart.html
        assert 'width="800"' in html
        assert 'height="600"' in html

    def test_no_axes_rendered(self):
        """Test that pie chart doesn't render axes."""
        chart = PieChart(data=[25, 35, 40])
        assert chart.render_axes is False
