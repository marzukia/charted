"""Tests for HeatmapChart - matrix data visualization."""

import pytest

from charted import HeatmapChart


class TestHeatmapChartInit:
    """Test HeatmapChart initialization and validation."""

    def test_basic_init(self):
        """Basic initialization with 3x3 matrix."""
        chart = HeatmapChart(
            data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            x_labels=["A", "B", "C"],
            y_labels=["X", "Y", "Z"],
        )
        assert chart._n_rows == 3
        assert chart._n_cols == 3
        assert chart._data_min == 1
        assert chart._data_max == 9

    def test_rectangular_matrix(self):
        """Non-square matrix (2 rows, 4 cols)."""
        chart = HeatmapChart(
            data=[[1, 2, 3, 4], [5, 6, 7, 8]],
            x_labels=["A", "B", "C", "D"],
            y_labels=["X", "Y"],
        )
        assert chart._n_rows == 2
        assert chart._n_cols == 4

    def test_single_row(self):
        """Single row matrix."""
        chart = HeatmapChart(
            data=[[1, 2, 3]],
            x_labels=["A", "B", "C"],
            y_labels=["Single"],
        )
        assert chart._n_rows == 1
        assert chart._n_cols == 3

    def test_single_cell(self):
        """Single cell matrix."""
        chart = HeatmapChart(data=[[42]], show_values=True)
        assert chart._n_rows == 1
        assert chart._n_cols == 1
        assert chart._data_min == 42
        assert chart._data_max == 42

    def test_auto_labels(self):
        """Auto-generated labels when none provided."""
        chart = HeatmapChart(data=[[1, 2], [3, 4]])
        assert len(chart._x_labels) == 2
        assert len(chart._y_labels) == 2
        assert chart._x_labels == ["1", "2"]
        assert chart._y_labels == ["1", "2"]

    def test_empty_data(self):
        """Empty data raises error."""
        with pytest.raises(ValueError, match="non-empty"):
            HeatmapChart(data=[])

    def test_invalid_data_type(self):
        """Non-2D data raises error."""
        with pytest.raises(ValueError, match="2D matrix"):
            HeatmapChart(data=[1, 2, 3])

    def test_mismatched_rows(self):
        """Uneven row lengths raises error."""
        with pytest.raises(ValueError, match="Row 1"):
            HeatmapChart(data=[[1, 2], [3]])

    def test_mismatched_x_labels(self):
        """Wrong x_labels count raises error."""
        with pytest.raises(ValueError, match="x_labels"):
            HeatmapChart(data=[[1, 2, 3]], x_labels=["A", "B"])

    def test_mismatched_y_labels(self):
        """Wrong y_labels count raises error."""
        with pytest.raises(ValueError, match="y_labels"):
            HeatmapChart(data=[[1], [2]], y_labels=["A"])

    def test_svg_output(self):
        """Chart produces valid SVG."""
        chart = HeatmapChart(
            data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            x_labels=["A", "B", "C"],
            y_labels=["X", "Y", "Z"],
        )
        svg = chart.html
        assert svg.startswith("<svg")
        assert svg.endswith("</svg>")
        assert "path" in svg or "Path" in svg

    def test_cell_properties(self):
        """Cell dimension calculations."""
        chart = HeatmapChart(
            data=[[1, 2], [3, 4]],
        )
        assert chart.cell_width > 0
        assert chart.cell_height > 0
        assert chart.draw_cell_width < chart.cell_width
        assert chart.draw_cell_height < chart.cell_height

    def test_color_scale_uniform(self):
        """All same value maps to low_color."""
        chart = HeatmapChart(
            data=[[5, 5], [5, 5]],
            low_color="#0000ff",
            high_color="#ff0000",
        )
        color = chart._value_to_color(5)
        assert color == "#0000ff"

    def test_color_scale_range(self):
        """Value mapping across the gradient."""
        chart = HeatmapChart(
            data=[[0, 100]],
            low_color="#000000",
            high_color="#ffffff",
        )
        assert chart._value_to_color(0) == "#000000"
        assert chart._value_to_color(100) == "#ffffff"
        mid = chart._value_to_color(50)
        r, g, b = int(mid[1:3], 16), int(mid[3:5], 16), int(mid[5:7], 16)
        assert 120 <= r <= 136
        assert g == r
        assert b == r

    def test_render_axes_false(self):
        """Heatmap does not render standard axes."""
        chart = HeatmapChart(data=[[1, 2], [3, 4]])
        assert chart.render_axes is False

    def test_no_legend(self):
        """Heatmap returns None for series legend."""
        chart = HeatmapChart(data=[[1, 2], [3, 4]])
        assert chart.legend is None

    def test_show_values_false(self):
        """Disabling value annotations."""
        chart = HeatmapChart(
            data=[[1, 2], [3, 4]],
            show_values=False,
        )
        svg = chart.html
        assert svg.startswith("<svg")

    def test_custom_format(self):
        """Custom value format string."""
        chart = HeatmapChart(
            data=[[1.234, 2.345]],
            value_format=".2f",
            show_values=True,
        )
        svg = chart.html
        assert "1.23" in svg
        assert "2.35" in svg


class TestLerpColor:
    """Test the internal color interpolation."""

    def test_lerp_exact(self):
        from charted.charts.heatmap import _lerp_color

        assert _lerp_color("#000000", "#ffffff", 0.0) == "#000000"
        assert _lerp_color("#000000", "#ffffff", 1.0) == "#ffffff"

    def test_lerp_midpoint(self):
        from charted.charts.heatmap import _lerp_color

        mid = _lerp_color("#000000", "#ffffff", 0.5)
        r, g, b = int(mid[1:3], 16), int(mid[3:5], 16), int(mid[5:7], 16)
        assert 120 <= r <= 136
        assert g == r
        assert b == r

    def test_lerp_clamp(self):
        from charted.charts.heatmap import _lerp_color

        assert _lerp_color("#000000", "#ffffff", -0.5) == "#000000"
        assert _lerp_color("#000000", "#ffffff", 1.5) == "#ffffff"
