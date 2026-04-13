"""Tests for Chart base class methods."""

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
