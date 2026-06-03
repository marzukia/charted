"""Extended ScatterChart tests for improved coverage.

Covers marker shapes, series styles, themes, and edge cases.
"""

import pytest

from charted import Theme
from charted.charts.scatter import ScatterChart


class TestScatterChartMarkerShapes:
    """Test different marker shapes in scatter charts."""

    def test_circle_marker_default(self):
        """Test default circle markers render correctly."""
        chart = ScatterChart(x_data=[0, 1, 2], y_data=[10, 20, 30])
        html = chart.html
        assert "<circle" in html.lower()
        assert 'r="4"' in html

    def test_square_marker_override(self):
        """Test square marker shape override."""
        chart = ScatterChart(
            x_data=[0, 1, 2],
            y_data=[10, 20, 30],
            series_styles=[{"marker_shape": "square"}],
        )
        html = chart.html
        assert "<rect" in html.lower()

    def test_diamond_marker_override(self):
        """Test diamond marker shape override."""
        chart = ScatterChart(
            x_data=[0, 1, 2],
            y_data=[10, 20, 30],
            series_styles=[{"marker_shape": "diamond"}],
        )
        html = chart.html
        assert "<path" in html.lower()

    def test_none_marker_hides_markers(self):
        """Test marker_shape='none' hides markers."""
        chart = ScatterChart(
            x_data=[0, 1, 2],
            y_data=[10, 20, 30],
            series_styles=[{"marker_shape": "none"}],
        )
        html = chart.html
        assert "<circle" not in html.lower()


class TestScatterChartMarkerSize:
    """Test marker size customization."""

    def test_custom_marker_size(self):
        """Test custom marker size."""
        chart = ScatterChart(
            x_data=[0, 1, 2],
            y_data=[10, 20, 30],
            series_styles=[{"marker_size": 8}],
        )
        html = chart.html
        assert 'r="8"' in html

    def test_default_marker_size(self):
        """Test default marker size is 4."""
        chart = ScatterChart(x_data=[0, 1, 2], y_data=[10, 20, 30])
        html = chart.html
        assert 'r="4"' in html


class TestScatterChartSeriesStyles:
    """Test series style overrides."""

    def test_fill_color_override(self):
        """Test fill color override."""
        chart = ScatterChart(
            x_data=[0, 1, 2],
            y_data=[10, 20, 30],
            series_styles=[{"fill": "#FF0000"}],
        )
        html = chart.html
        assert 'fill="#ff0000"' in html.lower()

    def test_multiple_series_styles(self):
        """Test multiple series with different styles."""
        chart = ScatterChart(
            x_data=[[0, 1], [0, 1]],
            y_data=[[10, 20], [15, 25]],
            series_styles=[
                {"marker_shape": "circle", "fill": "#FF0000"},
                {"marker_shape": "square", "fill": "#00FF00"},
            ],
        )
        html = chart.html
        assert "<circle" in html.lower()
        assert "<rect" in html.lower()

    def test_partial_series_style(self):
        """Test style override for only first series."""
        chart = ScatterChart(
            x_data=[[0, 1], [0, 1]],
            y_data=[[10, 20], [15, 25]],
            series_styles=[{"marker_shape": "square"}],
        )
        html = chart.html
        assert "<rect" in html.lower()


class TestScatterChartMultiSeries:
    """Test multi-series scatter charts."""

    def test_multi_series_with_names(self):
        """Test multi-series with series names."""
        chart = ScatterChart(
            x_data=[[0, 1], [2, 3]],
            y_data=[[10, 20], [15, 25]],
            series_names=["Series A", "Series B"],
        )
        html = chart.html
        assert "Series A" in html
        assert "Series B" in html

    def test_multi_series_different_x_data(self):
        """Test multi-series with different x-coordinates."""
        chart = ScatterChart(
            x_data=[[0, 1, 2], [5, 6, 7]],
            y_data=[[10, 20, 30], [15, 25, 35]],
        )
        html = chart.html
        assert "<circle" in html.lower()

    def test_multi_series_mismatched_lengths_raises(self):
        """Test that mismatched series lengths raise error."""
        with pytest.raises(Exception, match="Not all data vectors"):
            ScatterChart(
                x_data=[[0, 1], [0, 1, 2]],
                y_data=[[10, 20], [15, 25]],
            )


class TestScatterChartThemes:
    """Test theme integration."""

    def test_with_light_theme(self):
        """Test scatter chart with light theme."""
        chart = ScatterChart(x_data=[0, 1, 2], y_data=[10, 20, 30], theme="light")
        html = chart.html
        assert "<circle" in html.lower()

    def test_with_dark_theme(self):
        """Test scatter chart with dark theme."""
        chart = ScatterChart(x_data=[0, 1, 2], y_data=[10, 20, 30], theme="dark")
        html = chart.html
        assert "<circle" in html.lower()

    def test_with_custom_theme(self):
        """Test scatter chart with custom theme."""
        custom_theme = Theme(
            colors=["#FF0000"], background_color="#000000", legend_font_color="#ffffff"
        )
        chart = ScatterChart(x_data=[0, 1, 2], y_data=[10, 20, 30], theme=custom_theme)
        html = chart.html
        assert 'fill="#ff0000"' in html.lower()


class TestScatterChartEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_point_scatter(self):
        """Test scatter chart with single point."""
        chart = ScatterChart(x_data=[5], y_data=[10])
        html = chart.html
        assert "<circle" in html.lower()

    def test_very_small_values(self):
        """Test scatter chart with very small values."""
        chart = ScatterChart(x_data=[0, 1], y_data=[1e-10, 2e-10])
        html = chart.html
        assert "NaN" not in html
        assert "Infinity" not in html

    def test_mixed_positive_negative(self):
        """Test scatter chart with mixed positive and negative values."""
        chart = ScatterChart(x_data=[0, 1, 2], y_data=[-10, 0, 10])
        html = chart.html
        assert "<circle" in html.lower()

    def test_with_title(self):
        """Test scatter chart with title."""
        chart = ScatterChart(x_data=[0, 1, 2], y_data=[10, 20, 30], title="Test Chart")
        html = chart.html
        assert "Test Chart" in html

    def test_with_custom_dimensions(self):
        """Test scatter chart with custom dimensions."""
        chart = ScatterChart(
            x_data=[0, 1, 2], y_data=[10, 20, 30], width=800, height=600
        )
        html = chart.html
        assert 'width="800"' in html
        assert 'height="600"' in html

    def test_x_data_single_series_expands(self):
        """Test that single x_data series expands to match y_data."""
        chart = ScatterChart(x_data=[[0, 1]], y_data=[[10, 20], [30, 40]])
        html = chart.html
        assert "<circle" in html.lower()


class TestScatterChartRendering:
    """Test rendering correctness."""

    def test_svg_structure_valid(self):
        """Test that generated SVG is valid."""
        chart = ScatterChart(x_data=[0, 1, 2], y_data=[10, 20, 30])
        html = chart.html
        assert html.startswith("<svg")
        assert "</svg>" in html

    def test_markers_have_coordinates(self):
        """Test that markers have valid coordinates."""
        chart = ScatterChart(x_data=[0, 1, 2], y_data=[10, 20, 30])
        html = chart.html
        assert "cx=" in html or 'x="' in html

    def test_chart_has_axes(self):
        """Test that chart has axis elements."""
        chart = ScatterChart(x_data=[0, 1, 2], y_data=[10, 20, 30])
        html = chart.html
        assert "path" in html.lower()


class TestScatterChartLegend:
    """Test the scatter legend (shape + colour mapping and placement)."""

    def _two_series(self, **kwargs):
        return ScatterChart(
            x_data=[[0, 1, 2], [0, 1, 2]],
            y_data=[[1, 2, 3], [2, 3, 4]],
            series_names=["Alpha", "Beta"],
            shape_cycle=True,
            **kwargs,
        )

    def test_legend_defaults_to_none_layout_unchanged(self):
        """Default legend='none' reserves no extra layout space."""
        plain = ScatterChart(
            x_data=[[0, 1, 2], [0, 1, 2]],
            y_data=[[1, 2, 3], [2, 3, 4]],
            series_names=["Alpha", "Beta"],
        )
        assert plain.layout.legend_position == "none"
        assert plain.layout.legend_extent == 0.0
        # Padding matches a chart constructed with no legend argument at all.
        assert plain.right_padding == plain.h_padding * plain.width

    def test_legend_right_reserves_horizontal_space(self):
        """A right legend shrinks the plot width and lists each series."""
        with_legend = self._two_series(legend="right")
        without = self._two_series()
        assert with_legend.layout.legend_position == "right"
        assert with_legend.layout.legend_extent > 0
        # Reserved band comes out of the plot width.
        assert with_legend.plot_width < without.plot_width
        html = with_legend.html
        assert "Alpha" in html and "Beta" in html

    def test_legend_bottom_reserves_vertical_space(self):
        """A bottom legend shrinks the plot height."""
        with_legend = self._two_series(legend="bottom")
        without = self._two_series()
        assert with_legend.layout.legend_position == "bottom"
        assert with_legend.plot_height < without.plot_height

    def test_legend_top_reserves_vertical_space(self):
        """A top legend shrinks the plot height."""
        with_legend = self._two_series(legend="top")
        without = self._two_series()
        assert with_legend.layout.legend_position == "top"
        assert with_legend.plot_height < without.plot_height

    def test_legend_maps_shape_and_colour(self):
        """Legend swatches carry the series colour and per-series marker shape."""
        chart = ScatterChart(
            x_data=[[0, 1, 2], [0, 1, 2]],
            y_data=[[1, 2, 3], [2, 3, 4]],
            series_names=["Circles", "Squares"],
            series_styles=[{"marker_shape": "circle"}, {"marker_shape": "square"}],
            colors=["#112233", "#445566"],
            legend="right",
        )
        legend = chart.legend
        html = legend.html
        # Both series colours appear on swatches.
        assert "#112233" in html
        assert "#445566" in html
        # Shape mapping: a circle and a square swatch are both present.
        assert "<circle" in html.lower()
        assert "<rect" in html.lower()

    def test_legend_invalid_placement_raises(self):
        """An unknown placement is rejected up front."""
        with pytest.raises(ValueError, match="Invalid legend placement"):
            ScatterChart(
                x_data=[0, 1, 2],
                y_data=[1, 2, 3],
                series_names=["A"],
                legend="sideways",
            )

    def test_legend_without_series_names_reserves_nothing(self):
        """With no series names there is nothing to label, so no band."""
        chart = ScatterChart(
            x_data=[0, 1, 2], y_data=[1, 2, 3], legend="right"
        )
        assert chart.layout.legend_position == "none"
        assert chart.layout.legend_extent == 0.0
