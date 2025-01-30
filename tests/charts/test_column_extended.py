"""Extended ColumnChart tests for improved coverage.

Covers side-by-side mode, fill overrides, and edge cases.
"""

from charted import Theme
from charted.charts.column import ColumnChart


class TestColumnChartStackedMode:
    """Test stacked column chart mode (y_stacked=True)."""

    def test_stacked_default_true(self):
        """Test that y_stacked defaults to True."""
        chart = ColumnChart(data=[[10, 5], [20, 10]], labels=["a", "b"])
        assert chart.y_stacked is True

    def test_stacked_multi_series_rendering(self):
        """Test stacked multi-series columns render correctly."""
        chart = ColumnChart(
            data=[[10, 5, 3], [20, 10, 6], [30, 15, 9]], labels=["a", "b", "c"]
        )
        html = chart.html
        assert "<path" in html.lower()

    def test_stacked_fill_override(self):
        """Test fill color override in stacked mode."""
        chart = ColumnChart(
            data=[[10, 5], [20, 10]],
            labels=["a", "b"],
            series_styles=[{"fill": "#FF0000"}, {"fill": "#00FF00"}],
        )
        html = chart.html
        assert 'fill="#ff0000"' in html.lower()

    def test_stacked_mixed_positive_negative(self):
        """Test stacked columns with mixed positive and negative values."""
        chart = ColumnChart(
            data=[[10, -5], [20, -10], [30, -15]], labels=["a", "b", "c"]
        )
        html = chart.html
        assert "<path" in html.lower()
        assert "NaN" not in html


class TestColumnChartSideBySideMode:
    """Test side-by-side column chart mode (y_stacked=False)."""

    def test_side_by_side_basic(self):
        """Test basic side-by-side columns."""
        chart = ColumnChart(
            data=[[10, 20], [15, 25]], labels=["a", "b"], y_stacked=False
        )
        html = chart.html
        assert "<path" in html.lower()

    def test_side_by_side_three_series(self):
        """Test side-by-side with three series."""
        chart = ColumnChart(
            data=[[10, 20], [15, 25], [12, 22]], labels=["a", "b"], y_stacked=False
        )
        html = chart.html
        assert "<path" in html.lower()

    def test_side_by_side_fill_override(self):
        """Test fill color override in side-by-side mode."""
        chart = ColumnChart(
            data=[[10, 20], [15, 25]],
            labels=["a", "b"],
            y_stacked=False,
            series_styles=[{"fill": "#0000FF"}, {"fill": "#FFFF00"}],
        )
        html = chart.html
        assert 'fill="#0000ff"' in html.lower()

    def test_side_by_side_all_negative(self):
        """Test side-by-side with all negative values."""
        chart = ColumnChart(
            data=[[-10, -20], [-15, -25]], labels=["a", "b"], y_stacked=False
        )
        html = chart.html
        assert "<path" in html.lower()

    def test_side_by_side_mixed_positive_negative(self):
        """Test side-by-side with mixed positive and negative values."""
        chart = ColumnChart(
            data=[[-10, 20], [15, -25], [-30, 35]], labels=["a", "b"], y_stacked=False
        )
        html = chart.html
        assert "<path" in html.lower()
        assert "NaN" not in html

    def test_side_by_side_negative_only_single_series(self):
        """Test side-by-side with only negative values in single series."""
        chart = ColumnChart(
            data=[[-10, -20, -30]], labels=["a", "b", "c"], y_stacked=False
        )
        html = chart.html
        assert "<path" in html.lower()

    def test_side_by_side_negative_with_fill_override(self):
        """Test side-by-side negative values with fill override."""
        chart = ColumnChart(
            data=[[-10, -20]],
            labels=["a", "b"],
            y_stacked=False,
            series_styles=[{"fill": "#FF0000"}],
        )
        html = chart.html
        assert "<path" in html.lower()
        assert 'fill="#ff0000"' in html.lower()

    def test_side_by_side_single_series(self):
        """Test side-by-side with single series (degrades to normal columns)."""
        chart = ColumnChart(data=[[10, 20]], labels=["a", "b"], y_stacked=False)
        html = chart.html
        assert "<path" in html.lower()


class TestColumnChartColumnGap:
    """Test column_gap parameter."""

    def test_default_column_gap(self):
        """Test default column gap value."""
        chart = ColumnChart(data=[10, 20], labels=["a", "b"])
        assert chart.column_gap is not None

    def test_custom_column_gap(self):
        """Test custom column gap value."""
        chart = ColumnChart(data=[10, 20], labels=["a", "b"], column_gap=0.5)
        assert chart.column_gap == 0.5

    def test_small_column_gap(self):
        """Test very small column gap."""
        chart = ColumnChart(data=[10, 20], labels=["a", "b"], column_gap=0.1)
        html = chart.html
        assert "<path" in html.lower()

    def test_large_column_gap(self):
        """Test large column gap."""
        chart = ColumnChart(data=[10, 20], labels=["a", "b"], column_gap=0.8)
        html = chart.html
        assert "<path" in html.lower()


class TestColumnChartSeriesStyles:
    """Test series style overrides."""

    def test_stacked_single_fill_override(self):
        """Test single fill override in stacked mode."""
        chart = ColumnChart(
            data=[[10, 5], [20, 10]],
            labels=["a", "b"],
            series_styles=[{"fill": "#FF0000"}],
        )
        html = chart.html
        assert 'fill="#ff0000"' in html.lower()

    def test_side_by_side_single_fill_override(self):
        """Test single fill override in side-by-side mode."""
        chart = ColumnChart(
            data=[[10, 20], [15, 25]],
            labels=["a", "b"],
            y_stacked=False,
            series_styles=[{"fill": "#00FF00"}],
        )
        html = chart.html
        assert 'fill="#00ff00"' in html.lower()

    def test_mixed_style_overrides(self):
        """Test multiple style overrides with some None."""
        chart = ColumnChart(
            data=[[10, 5], [20, 10], [15, 8]],
            labels=["a", "b"],
            series_styles=[{"fill": "#FF0000"}, None, {"fill": "#0000FF"}],
        )
        html = chart.html
        assert 'fill="#ff0000"' in html.lower()

    def test_style_override_without_fill_key(self):
        """Test style override that doesn't specify fill (should use default color)."""
        chart = ColumnChart(
            data=[[10, 5], [20, 10]],
            labels=["a", "b"],
            series_styles=[{"marker_shape": "square"}],  # No fill key
        )
        html = chart.html
        assert "<path" in html.lower()

    def test_style_override_empty_dict(self):
        """Test style override with empty dict."""
        chart = ColumnChart(
            data=[[10, 5], [20, 10]],
            labels=["a", "b"],
            series_styles=[{}],
        )
        html = chart.html
        assert "<path" in html.lower()


class TestColumnChartEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_value_single_label(self):
        """Test single value with single label."""
        chart = ColumnChart(data=[42], labels=["only"])
        html = chart.html
        assert "<path" in html.lower()

    def test_very_large_values_stacked(self):
        """Test very large values in stacked mode."""
        chart = ColumnChart(data=[[1e6, 5e5], [2e6, 1e6]], labels=["a", "b"])
        html = chart.html
        assert "NaN" not in html
        assert "Infinity" not in html

    def test_very_large_values_side_by_side(self):
        """Test very large values in side-by-side mode."""
        chart = ColumnChart(
            data=[[1e6, 5e5], [2e6, 1e6]], labels=["a", "b"], y_stacked=False
        )
        html = chart.html
        assert "NaN" not in html
        assert "Infinity" not in html

    def test_very_small_values(self):
        """Test very small values."""
        chart = ColumnChart(data=[1e-10, 2e-10], labels=["a", "b"])
        html = chart.html
        assert "NaN" not in html
        assert "Infinity" not in html

    def test_zero_values(self):
        """Test zero values."""
        chart = ColumnChart(data=[0, 0, 0], labels=["a", "b", "c"])
        html = chart.html
        assert "<path" in html.lower()

    def test_mixed_zero_positive_negative(self):
        """Test mixed zero, positive, and negative values."""
        chart = ColumnChart(data=[-10, 0, 10], labels=["a", "b", "c"])
        html = chart.html
        assert "<path" in html.lower()

    def test_with_title(self):
        """Test column chart with title."""
        chart = ColumnChart(
            data=[10, 20, 30], labels=["a", "b", "c"], title="Sales Report"
        )
        html = chart.html
        assert "Sales Report" in html

    def test_with_custom_dimensions(self):
        """Test column chart with custom dimensions."""
        chart = ColumnChart(data=[10, 20], labels=["a", "b"], width=1000, height=700)
        html = chart.html
        assert 'width="1000"' in html
        assert 'height="700"' in html

    def test_with_light_theme(self):
        """Test column chart with light theme."""
        chart = ColumnChart(data=[10, 20], labels=["a", "b"], theme="light")
        html = chart.html
        assert "<path" in html.lower()

    def test_with_dark_theme(self):
        """Test column chart with dark theme."""
        chart = ColumnChart(data=[10, 20], labels=["a", "b"], theme="dark")
        html = chart.html
        assert "<path" in html.lower()

    def test_with_custom_theme(self):
        """Test column chart with custom theme."""
        custom_theme = Theme(
            colors=["#FF0000"], background_color="#000000", legend_font_color="#ffffff"
        )
        chart = ColumnChart(data=[10, 20], labels=["a", "b"], theme=custom_theme)
        html = chart.html
        assert 'fill="#ff0000"' in html.lower()


class TestColumnChartRendering:
    """Test rendering correctness."""

    def test_svg_structure_valid(self):
        """Test that generated SVG is valid."""
        chart = ColumnChart(data=[10, 20], labels=["a", "b"])
        html = chart.html
        assert html.startswith("<svg")
        assert "</svg>" in html

    def test_paths_have_coordinates(self):
        """Test that paths have valid coordinates."""
        chart = ColumnChart(data=[10, 20], labels=["a", "b"])
        html = chart.html
        # Path elements should have d attribute with coordinates
        assert 'd="' in html

    def test_chart_has_legend(self):
        """Test that multi-series chart has legend."""
        chart = ColumnChart(
            data=[[10, 20], [15, 25]], labels=["a", "b"], series_names=["S1", "S2"]
        )
        html = chart.html
        assert "S1" in html
        assert "S2" in html
