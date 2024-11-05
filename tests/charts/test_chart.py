"""Tests for Chart base class methods."""

import pytest

from charted.charts.column import ColumnChart


def test_get_base_transform_returns_4_elements():
    """Transform chain returns list of 4 transform functions."""
    chart = ColumnChart(data=[1, 2, 3])
    transforms = chart.get_base_transform()
    assert len(transforms) == 4


def test_x_offset_property_returns_reprojected_value():
    """x_offset returns reprojected value when labels=True."""
    chart = ColumnChart(data=[1, 2, 3], labels=["a", "b", "c"])
    offset = chart.x_offset
    assert offset > 0


def test_apply_stacking_adds_offset_when_stacked():
    """Stacking adds offset only when y_stacked=True."""
    chart = ColumnChart(data=[1, 2, 3])
    chart.y_stacked = True

    # When stacked, should add offset
    result = chart._apply_stacking(10, 5)
    assert result == 15

    # When not stacked, should return y unchanged
    chart.y_stacked = False
    result = chart._apply_stacking(10, 5)
    assert result == 10


def test_h_padding_rejects_value_greater_than_one():
    """h_padding > 1 raises InvalidValue."""
    with pytest.raises(Exception) as exc_info:
        chart = ColumnChart(data=[1, 2, 3])
        chart.h_padding = 1.5
    assert "h_padding" in str(exc_info.value).lower()


def test_v_padding_rejects_value_greater_than_one():
    """v_padding > 1 raises InvalidValue."""
    with pytest.raises(Exception) as exc_info:
        chart = ColumnChart(data=[1, 2, 3])
        chart.v_padding = 1.5
    assert "v_padding" in str(exc_info.value).lower()


def test_validate_data_rejects_empty_data():
    """Empty data raises exception."""
    from charted.utils.data_model import DataModel

    with pytest.raises(Exception, match="No data was provided"):
        DataModel([], None)


def test_validate_data_rejects_mismatched_lengths():
    """Data vectors of different lengths raise exception."""
    from charted.utils.data_model import DataModel

    with pytest.raises(Exception, match="Not all vectors were same length"):
        DataModel([[1, 2, 3], [4, 5]], None)
