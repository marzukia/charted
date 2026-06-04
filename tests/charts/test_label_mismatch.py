"""Tests for the label/data length guard (BUG-LABEL-MISMATCH).

LabelMismatchError must fire when a chart is given a label count that cannot
line up with its data, instead of silently truncating or misaligning. The
guard lives in DataModel so every chart type inherits it.
"""

import pytest

from charted.charts.bar import BarChart
from charted.charts.column import ColumnChart
from charted.charts.histogram import Histogram
from charted.charts.line import LineChart
from charted.charts.pie import PieChart
from charted.utils.data_model import DataModel
from charted.utils.exceptions import LabelMismatchError


class TestValidLabelsPass:
    """Charts whose labels match the data must still build."""

    def test_bar_single_series(self):
        BarChart(data=[10, 20, 30], labels=["a", "b", "c"])

    def test_column_single_series(self):
        ColumnChart(data=[10, 20, 30], labels=["a", "b", "c"])

    def test_pie(self):
        PieChart(data=[25, 35, 40], labels=["a", "b", "c"])

    def test_line(self):
        LineChart(data=[10, 25, 18, 32], labels=["a", "b", "c", "d"])

    def test_no_labels_is_allowed(self):
        # Labels are optional; omitting them must not raise.
        LineChart(data=[1, 2, 3])

    def test_bar_multi_series_labels_match_points(self):
        # Two series of three bars share three category labels.
        BarChart(data=[[1, 2, 3], [4, 5, 6]], labels=["x", "y", "z"])

    def test_column_stacked_labels_match_outer(self):
        # Stacked column: each inner list is one category's segments, so the
        # three labels match the three outer categories.
        ColumnChart(data=[[10, 5], [15, 10], [20, 15]], labels=["a", "b", "c"])

    def test_histogram_edge_labels(self):
        # Histograms label N bins with N+1 boundary labels.
        Histogram(data=[1, 2, 2, 3, 3, 3, 4, 4, 5], bins=5)


class TestMismatchRaises:
    """A label count that fits no orientation must raise."""

    def test_bar_too_few_labels(self):
        with pytest.raises(LabelMismatchError):
            BarChart(data=[1, 2, 3], labels=["a", "b"])

    def test_bar_too_many_labels(self):
        with pytest.raises(LabelMismatchError):
            BarChart(data=[1, 2, 3], labels=["a", "b", "c", "d", "e"])

    def test_column_too_few_labels(self):
        with pytest.raises(LabelMismatchError):
            ColumnChart(data=[1, 2, 3], labels=["a", "b"])

    def test_pie_too_few_labels(self):
        with pytest.raises(LabelMismatchError):
            PieChart(data=[1, 2, 3], labels=["a", "b"])

    def test_line_too_few_labels(self):
        with pytest.raises(LabelMismatchError):
            LineChart(data=[1, 2, 3, 4], labels=["a", "b"])

    def test_multi_series_wrong_count(self):
        # 2 series x 3 points: valid counts are 3 (points) or 2 (series).
        # 5 fits neither orientation.
        with pytest.raises(LabelMismatchError):
            ColumnChart(data=[[1, 2, 3], [4, 5, 6]], labels=["a", "b", "c", "d", "e"])


class TestErrorMessage:
    """The raised error must be actionable."""

    def test_message_reports_counts_and_axis(self):
        with pytest.raises(LabelMismatchError) as exc:
            BarChart(data=[1, 2, 3], labels=["a", "b"])
        msg = str(exc.value)
        assert "2" in msg and "3" in msg
        assert "y-labels" in msg

    def test_datamodel_x_axis_message(self):
        with pytest.raises(LabelMismatchError) as exc:
            DataModel(y_data=[1, 2, 3], x_labels=["a", "b"])
        assert "x-labels" in str(exc.value)
