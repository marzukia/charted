"""Tests for chart.py."""

import pytest
from charted.charts.column import ColumnChart


class TestColumnChart:
    """Tests for ColumnChart."""

    def test_column_chart_basic(self):
        """Test ColumnChart creation."""
        data = [1, 2, 3]
        labels = [1, 2, 3]
        chart = ColumnChart(data=data, labels=labels)
        assert chart is not None
        assert chart.y_data == [data]

    def test_column_chart_no_data_raises_error(self):
        """Test that ColumnChart raises error when no data is provided."""
        with pytest.raises(Exception):
            ColumnChart()

    def test_column_chart_with_title(self):
        """Test ColumnChart with a title."""
        data = [1, 2, 3]
        labels = [1, 2, 3]
        title = "Test Chart"
        chart = ColumnChart(data=data, labels=labels, title=title)
        assert chart.title is not None

    def test_column_chart_with_theme(self):
        """Test ColumnChart with a custom theme."""
        data = [1, 2, 3]
        labels = [1, 2, 3]
        theme = {"colors": ["#ff0000"]}
        chart = ColumnChart(data=data, labels=labels, theme=theme)
        assert chart.theme is not None

    def test_column_chart_with_x_labels(self):
        """Test ColumnChart with custom x_labels."""
        data = [1, 2, 3]
        labels = ["A", "B", "C"]
        chart = ColumnChart(data=data, labels=labels)
        assert chart.x_labels == labels

    def test_column_chart_with_y_labels(self):
        """Test ColumnChart with custom y_labels."""
        data = [1, 2, 3]
        y_labels = ["Low", "Medium", "High"]
        chart = ColumnChart(data=data, y_labels=y_labels)
        assert chart.y_labels == y_labels

    def test_column_chart_with_series_names(self):
        """Test ColumnChart with series names."""
        data = [[1, 2], [3, 4]]
        labels = [1, 2]
        series_names = ["Series 1", "Series 2"]
        chart = ColumnChart(data=data, labels=labels, series_names=series_names)
        assert chart.series_names == series_names

    def test_column_chart_custom_width_height(self):
        """Test ColumnChart with custom dimensions."""
        data = [1, 2, 3]
        labels = [1, 2, 3]
        width = 800
        height = 600
        chart = ColumnChart(data=data, labels=labels, width=width, height=height)
        assert chart.width == width
        assert chart.height == height

    def test_column_chart_stacked_mode(self):
        """Test ColumnChart in stacked mode."""
        data = [[1, 2], [3, 4]]
        labels = [1, 2]
        chart = ColumnChart(data=data, labels=labels, y_stacked=True)
        assert chart.y_stacked is True

    def test_column_chart_zero_index(self):
        """Test ColumnChart with zero_index setting."""
        data = [1, 2, 3]
        labels = [1, 2, 3]
        chart = ColumnChart(data=data, labels=labels, zero_index=False)
        assert chart.zero_index is False
