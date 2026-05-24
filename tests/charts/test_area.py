"""Tests for AreaChart class.

Covers construction, rendering, and edge cases.
"""

import pytest

from charted.charts.area import AreaChart
from charted.utils.exceptions import NoDataError


class TestAreaChartConstruction:
    """Tests for AreaChart initialization."""

    def test_basic_construction(self):
        """Basic AreaChart with single series."""
        chart = AreaChart(
            data=[15, 30, 45, 70, 55, 80, 75, 90, 85, 95],
            labels=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
        )
        assert chart.title is None

    def test_with_title(self):
        """AreaChart with title."""
        chart = AreaChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            title="Test Area",
        )
        assert chart._title.text == "Test Area"

    def test_with_custom_fill_opacity(self):
        """AreaChart with custom fill_opacity."""
        chart = AreaChart(
            data=[10, 20, 30],
            fill_opacity=0.5,
        )
        assert chart.fill_opacity == 0.5

    def test_multi_series(self):
        """AreaChart with multiple series."""
        chart = AreaChart(
            data=[[10, 20, 30], [15, 25, 35]],
            labels=["A", "B", "C"],
            series_names=["Series 1", "Series 2"],
        )
        assert chart.series_names == ["Series 1", "Series 2"]

    def test_with_x_data(self):
        """AreaChart with explicit x_data."""
        chart = AreaChart(
            data=[10, 20, 30],
            x_data=[1.0, 2.0, 3.0],
        )
        assert chart.data_model is not None

    def test_with_custom_theme(self):
        """AreaChart with custom theme."""
        from charted.themes.core import Theme

        theme = Theme(colors=["#ff0000"])
        chart = AreaChart(data=[10, 20, 30], theme=theme)
        assert chart.colors[0] == "#ff0000"

    def test_with_series_styles(self):
        """AreaChart with series styles."""
        from charted.utils.series_style import SeriesStyle

        styles = [SeriesStyle(_fill="#ff0000")]
        chart = AreaChart(
            data=[10, 20, 30],
            series_styles=styles,
        )
        assert chart.series_styles == styles

    def test_pad_x_labels_false(self):
        """AreaChart has pad_x_labels=False by default."""
        chart = AreaChart(data=[10, 20, 30])
        assert chart.pad_x_labels is False

    def test_x_offset_zero(self):
        """AreaChart x_offset is always 0."""
        chart = AreaChart(data=[10, 20, 30])
        assert chart.x_offset == 0.0

    def test_empty_data_raises(self):
        """Empty data raises NoDataError."""
        with pytest.raises(NoDataError):
            AreaChart(data=[], labels=[])


class TestAreaChartRendering:
    """Tests for AreaChart rendering."""

    def test_svg_output(self):
        """AreaChart produces SVG output."""
        chart = AreaChart(
            data=[15, 30, 45, 70, 55, 80, 75, 90, 85, 95],
            labels=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
        )
        svg = chart.to_svg()
        assert svg.startswith("<svg")
        assert "viewBox" in svg

    def test_to_html(self):
        """AreaChart to_html works."""
        chart = AreaChart(data=[10, 20, 30])
        html = chart.to_html()
        assert "<div" in html
        assert "<svg" in html

    def test_to_base64(self):
        """AreaChart to_base64 works."""
        chart = AreaChart(data=[10, 20, 30])
        b64 = chart.to_base64()
        assert b64.startswith("data:image/svg+xml")

    def test_representation_returns_g(self):
        """Representation returns a G element."""
        chart = AreaChart(data=[10, 20, 30])
        from charted.html.element import G

        assert isinstance(chart.representation, G)

    def test_single_data_point(self):
        """Single data point renders correctly."""
        chart = AreaChart(data=[50], labels=["A"])
        svg = chart.to_svg()
        assert svg.startswith("<svg")

    def test_two_data_points(self):
        """Two data points render correctly."""
        chart = AreaChart(data=[10, 20], labels=["A", "B"])
        svg = chart.to_svg()
        assert "M" in svg  # has path data
