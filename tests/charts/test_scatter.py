import pytest

from charted.charts.scatter import ScatterChart
from charted.utils.exceptions import InvalidValue


class TestScatterChart:
    """Tests for ScatterChart class."""

    def test_scatter_chart_basic(self):
        """Test basic ScatterChart creation."""
        x_data = [1, 2, 3, 4, 5]
        y_data = [2, 4, 6, 8, 10]
        chart = ScatterChart(x_data=x_data, y_data=y_data)
        assert chart is not None
        assert chart.x_data == [x_data]
        assert chart.y_data == [y_data]

    def test_scatter_chart_with_title(self):
        """Test ScatterChart with a title."""
        x_data = [1, 2, 3]
        y_data = [1, 2, 3]
        title = "Test Scatter Chart"
        chart = ScatterChart(x_data=x_data, y_data=y_data, title=title)
        assert chart.title is not None

    def test_scatter_chart_with_theme(self):
        """Test ScatterChart with a custom theme."""
        x_data = [1, 2, 3]
        y_data = [1, 2, 3]
        theme = {"colors": ["#ff0000"]}
        chart = ScatterChart(x_data=x_data, y_data=y_data, theme=theme)
        assert chart.theme is not None

    def test_scatter_chart_no_data_raises_error(self):
        """Test that ScatterChart raises error when no data is provided."""
        with pytest.raises(InvalidValue):
            ScatterChart(x_data=[], y_data=[])

    def test_scatter_chart_with_only_x_data(self):
        """Test ScatterChart with only x_data."""
        x_data = [1, 2, 3]
        chart = ScatterChart(x_data=x_data, y_data=[])
        assert chart is not None
        assert chart.x_data == [x_data]

    def test_scatter_chart_with_only_y_data(self):
        """Test ScatterChart with only y_data."""
        y_data = [1, 2, 3]
        chart = ScatterChart(x_data=[], y_data=y_data)
        assert chart is not None
        assert chart.y_data == [y_data]

    def test_scatter_chart_width_height(self):
        """Test ScatterChart with custom dimensions."""
        x_data = [1, 2, 3]
        y_data = [1, 2, 3]
        width = 800
        height = 600
        chart = ScatterChart(x_data=x_data, y_data=y_data, width=width, height=height)
        assert chart.width == width
        assert chart.height == height

    def test_scatter_chart_series_names(self):
        """Test ScatterChart with series names."""
        x_data = [1, 2, 3]
        y_data = [1, 2, 3]
        series_names = ["Series 1"]
        chart = ScatterChart(x_data=x_data, y_data=y_data, series_names=series_names)
        assert chart.series_names == series_names
