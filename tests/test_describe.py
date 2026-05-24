"""Tests for Chart.describe() method (Issue #14)."""

import pytest

from charted.charts.bar import BarChart
from charted.charts.column import ColumnChart
from charted.charts.line import LineChart
from charted.charts.pie import PieChart


class TestDescribeReturnStructure:
    """Test that describe() returns a well-formed dict with expected keys."""

    def test_returns_dict(self):
        chart = BarChart(data=[1, 2, 3], labels=["a", "b", "c"])
        result = chart.describe()
        assert isinstance(result, dict)

    def test_all_expected_keys_present(self):
        chart = BarChart(
            data=[1, 2, 3],
            labels=["a", "b", "c"],
            title="Test",
        )
        result = chart.describe()
        expected_keys = {
            "chart_type",
            "title",
            "dimensions",
            "series",
            "labels",
            "label_count",
            "series_count",
            "theme",
            "has_negative_values",
            "stacked",
        }
        assert expected_keys == set(result.keys())


class TestDescribeBarChart:
    """Test describe() on BarChart with single series."""

    def test_single_series_bar_chart(self):
        chart = BarChart(
            data=[120, 180, 210, 150],
            labels=["Q1", "Q2", "Q3", "Q4"],
            title="Sales by Quarter",
        )
        result = chart.describe()

        assert result["chart_type"] == "BarChart"
        assert result["title"] == "Sales by Quarter"
        assert result["dimensions"] == {"width": 500, "height": 500}
        assert result["labels"] == ["Q1", "Q2", "Q3", "Q4"]
        assert result["label_count"] == 4
        assert result["series_count"] == 1
        assert result["stacked"] is False
        assert result["has_negative_values"] is False

    def test_series_stats(self):
        chart = BarChart(data=[120, 180, 210, 150], labels=["Q1", "Q2", "Q3", "Q4"])
        result = chart.describe()

        assert len(result["series"]) == 1
        series = result["series"][0]
        assert series["count"] == 4
        assert series["min"] == 120.0
        assert series["max"] == 210.0
        assert series["sum"] == 660.0
        assert series["mean"] == 165.0


class TestDescribeMultiSeries:
    """Test describe() on multi-series LineChart."""

    def test_multi_series_line_chart(self):
        chart = LineChart(
            data=[[10, 20, 30], [15, 25, 35]],
            labels=["Jan", "Feb", "Mar"],
            series_names=["Revenue", "Profit"],
            title="Financials",
        )
        result = chart.describe()

        assert result["chart_type"] == "LineChart"
        assert result["series_count"] == 2
        assert result["label_count"] == 3
        assert result["labels"] == ["Jan", "Feb", "Mar"]

    def test_multi_series_names_in_series(self):
        chart = LineChart(
            data=[[10, 20, 30], [15, 25, 35]],
            labels=["Jan", "Feb", "Mar"],
            series_names=["Revenue", "Profit"],
        )
        result = chart.describe()

        assert result["series"][0]["name"] == "Revenue"
        assert result["series"][1]["name"] == "Profit"

    def test_multi_series_stats_correct(self):
        chart = LineChart(
            data=[[10, 20, 30], [100, 200, 300]],
            labels=["a", "b", "c"],
            series_names=["Small", "Large"],
        )
        result = chart.describe()

        small = result["series"][0]
        assert small["min"] == 10.0
        assert small["max"] == 30.0
        assert small["sum"] == 60.0
        assert small["mean"] == 20.0

        large = result["series"][1]
        assert large["min"] == 100.0
        assert large["max"] == 300.0
        assert large["sum"] == 600.0
        assert large["mean"] == 200.0


class TestDescribeNegativeValues:
    """Test describe() detects negative values."""

    def test_has_negative_values_true(self):
        chart = ColumnChart(
            data=[-5, 10, -3, 20],
            labels=["a", "b", "c", "d"],
        )
        result = chart.describe()
        assert result["has_negative_values"] is True

    def test_has_negative_values_false(self):
        chart = ColumnChart(
            data=[5, 10, 3, 20],
            labels=["a", "b", "c", "d"],
        )
        result = chart.describe()
        assert result["has_negative_values"] is False


class TestDescribeStacked:
    """Test describe() on stacked charts."""

    def test_stacked_column_chart(self):
        chart = ColumnChart(
            data=[[1, 2, 3], [4, 5, 6]],
            labels=["a", "b", "c"],
            y_stacked=True,
        )
        result = chart.describe()
        assert result["stacked"] is True

    def test_non_stacked_chart(self):
        chart = BarChart(
            data=[[1, 2, 3], [4, 5, 6]],
            labels=["a", "b", "c"],
            x_stacked=False,
        )
        result = chart.describe()
        assert result["stacked"] is False

    def test_stacked_bar_chart(self):
        chart = BarChart(
            data=[[1, 2, 3], [4, 5, 6]],
            labels=["a", "b", "c"],
            x_stacked=True,
        )
        result = chart.describe()
        assert result["stacked"] is True


class TestDescribePieChart:
    """Test describe() on PieChart (different data shape)."""

    def test_pie_chart_type(self):
        chart = PieChart(data=[25, 35, 40], labels=["A", "B", "C"])
        result = chart.describe()
        assert result["chart_type"] == "PieChart"

    def test_pie_chart_series(self):
        chart = PieChart(data=[25, 35, 40], labels=["A", "B", "C"])
        result = chart.describe()
        # PieChart has one logical series (the slices)
        assert result["series_count"] == 1
        series = result["series"][0]
        assert series["count"] == 3
        assert series["min"] == 25.0
        assert series["max"] == 40.0
        assert series["sum"] == 100.0

    def test_pie_chart_labels(self):
        chart = PieChart(data=[25, 35, 40], labels=["A", "B", "C"])
        result = chart.describe()
        assert result["labels"] == ["A", "B", "C"]


class TestDescribeNoTitle:
    """Test describe() when title is None."""

    def test_title_is_none(self):
        chart = BarChart(data=[1, 2, 3], labels=["a", "b", "c"])
        result = chart.describe()
        assert result["title"] is None


class TestDescribeNoLabels:
    """Test describe() when no labels provided."""

    def test_labels_are_none_or_generated(self):
        chart = LineChart(data=[1, 2, 3])
        result = chart.describe()
        # Should still have label_count matching data length
        assert result["label_count"] == 3


class TestDescribeSeriesWithoutNames:
    """Test describe() when series_names not provided."""

    def test_series_name_defaults(self):
        chart = LineChart(data=[[1, 2], [3, 4]], labels=["a", "b"])
        result = chart.describe()
        # Without names, series should have None or auto-generated name
        assert result["series"][0]["name"] is None
        assert result["series"][1]["name"] is None
