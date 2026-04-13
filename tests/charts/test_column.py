import pytest

from charted.charts.column import ColumnChart
from charted.utils.exceptions import InvalidValue


class TestColumnChart:
    """Tests for ColumnChart class."""

    def test_column_chart_basic(self):
        """Test basic ColumnChart creation."""
        data = [2, 4, 6, 8, 10]
        labels = [1, 2, 3, 4, 5]
        chart = ColumnChart(data=data, labels=labels)
        assert chart is not None
        assert chart.y_data == [data]
        assert chart.x_labels == labels

    def test_column_chart_with_title(self):
        """Test ColumnChart with a title."""
        data = [1, 2, 3]
        labels = [1, 2, 3]
        title = "Test Column Chart"
        chart = ColumnChart(data=data, labels=labels, title=title)
        assert chart.title is not None

    def test_column_chart_with_theme(self):
        """Test ColumnChart with a custom theme."""
        data = [1, 2, 3]
        labels = [1, 2, 3]
        theme = {"colors": ["#ff0000"]}
        chart = ColumnChart(data=data, labels=labels, theme=theme)
        assert chart.theme is not None

    def test_column_chart_no_data_raises_error(self):
        """Test that ColumnChart raises error when no data is provided."""
        with pytest.raises(InvalidValue):
            ColumnChart()

    def test_column_chart_with_only_labels(self):
        """Test ColumnChart with only labels."""
        labels = [1, 2, 3]
        chart = ColumnChart(data=[1, 2, 3], labels=labels)
        assert chart is not None
        assert chart.x_labels == labels

    def test_column_chart_width_height(self):
        """Test ColumnChart with custom dimensions."""
        data = [1, 2, 3]
        labels = [1, 2, 3]
        width = 800
        height = 600
        chart = ColumnChart(data=data, labels=labels, width=width, height=height)
        assert chart.width == width
        assert chart.height == height

    def test_column_chart_series_names(self):
        """Test ColumnChart with series names."""
        data = [[1, 2], [3, 4]]
        labels = [1, 2]
        series_names = ["Series 1", "Series 2"]
        chart = ColumnChart(data=data, labels=labels, series_names=series_names)
        assert chart.series_names == series_names

    def test_column_chart_stacked_mode(self):
        """Test ColumnChart in stacked mode."""
        data = [[1, 2], [3, 4]]
        labels = [1, 2]
        chart = ColumnChart(data=data, labels=labels, y_stacked=True)
        assert chart.y_stacked is True
