"""Tests for BoxPlot chart type.

Covers construction, rendering, quartile calculation, and edge cases.
"""

from charted.charts.box import BoxPlot, _quartiles


class TestQuartiles:
    """Tests for _quartiles() helper."""

    def test_basic_quartiles(self):
        """Basic quartile calculation."""
        min_v, q1, med, q3, max_v = _quartiles([1, 2, 3, 4, 5])
        assert min_v == 1
        assert q1 == 1.5  # median of [1, 2]
        assert med == 3
        assert q3 == 4.5  # median of [4, 5]
        assert max_v == 5

    def test_even_length(self):
        """Even-length dataset quartiles."""
        min_v, q1, med, q3, max_v = _quartiles([1, 2, 3, 4])
        assert min_v == 1
        assert med == 2.5  # (2+3)/2
        assert max_v == 4

    def test_single_element(self):
        """Single element: all quartiles equal."""
        min_v, q1, med, q3, max_v = _quartiles([5])
        assert min_v == 5
        assert q1 == 5
        assert med == 5
        assert q3 == 5
        assert max_v == 5

    def test_two_elements(self):
        """Two elements: median is average."""
        min_v, q1, med, q3, max_v = _quartiles([3, 7])
        assert min_v == 3
        assert med == 5  # (3+7)/2
        assert max_v == 7

    def test_empty_data_returns_zeros(self):
        """Empty data returns zeros."""
        result = _quartiles([])
        assert result == (0, 0, 0, 0, 0)

    def test_negative_values(self):
        """Negative values work correctly."""
        min_v, q1, med, q3, max_v = _quartiles([-5, -3, 0, 2, 4])
        assert min_v == -5
        assert med == 0
        assert max_v == 4

    def test_median_empty_subset(self):
        """Median returns 0 for empty sub-array edge case."""
        min_v, q1, med, q3, max_v = _quartiles([1])
        assert q1 == 1
        assert med == 1
        assert q3 == 1


class TestBoxPlotConstruction:
    """Tests for BoxPlot initialization."""

    def test_basic_construction(self):
        """Basic BoxPlot with single series."""
        chart = BoxPlot(
            data=[[3, 5, 7, 9, 10, 12, 14, 16, 18, 20]],
            labels=["Series A"],
        )
        assert chart.title is None

    def test_with_title(self):
        """BoxPlot with title."""
        chart = BoxPlot(
            data=[[1, 2, 3]],
            labels=["A"],
            title="Test Box",
        )
        assert chart._title.text == "Test Box"

    def test_multi_series(self):
        """BoxPlot with multiple series."""
        chart = BoxPlot(
            data=[
                [3, 5, 7, 9, 10, 12, 14, 16, 18, 20],
                [4, 6, 8, 10, 11, 13, 15, 17, 19, 21],
                [2, 4, 6, 8, 9, 11, 13, 15, 17, 19],
            ],
            labels=["Series A", "Series B", "Series C"],
        )
        assert len(chart.colors) >= 3

    def test_with_series_names(self):
        """BoxPlot with series names."""
        chart = BoxPlot(
            data=[[1, 2, 3]],
            labels=["A"],
            series_names=["Test Series"],
        )
        assert chart.series_names == ["Test Series"]

    def test_with_custom_theme(self):
        """BoxPlot with custom theme."""
        from charted.themes.core import Theme

        theme = Theme(colors=["#ff0000"])
        chart = BoxPlot(data=[[1, 2, 3]], labels=["A"], theme=theme)
        assert chart.colors[0] == "#ff0000"


class TestBoxPlotRendering:
    """Tests for BoxPlot rendering."""

    def test_svg_output(self):
        """BoxPlot produces SVG output."""
        chart = BoxPlot(
            data=[
                [3, 5, 7, 9, 10, 12, 14, 16, 18, 20],
                [4, 6, 8, 10, 11, 13, 15, 17, 19, 21],
                [2, 4, 6, 8, 9, 11, 13, 15, 17, 19],
            ],
            labels=["Series A", "Series B", "Series C"],
        )
        svg = chart.to_svg()
        assert svg.startswith("<svg")
        assert "viewBox" in svg

    def test_to_html(self):
        """BoxPlot to_html works."""
        chart = BoxPlot(data=[[1, 2, 3]], labels=["A"])
        html = chart.to_html()
        assert "<div" in html
        assert "<svg" in html

    def test_to_base64(self):
        """BoxPlot to_base64 works."""
        chart = BoxPlot(data=[[1, 2, 3]], labels=["A"])
        b64 = chart.to_base64()
        assert b64.startswith("data:image/svg+xml")

    def test_representation_returns_g(self):
        """Representation returns a G element."""
        chart = BoxPlot(data=[[1, 2, 3]], labels=["A"])
        from charted.html.element import G

        assert isinstance(chart.representation, G)
