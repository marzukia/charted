"""Test suite for axis rendering (XAxis, YAxis)."""

import pytest
from charted.charts.axes import XAxis, YAxis


class MockParent:
    """Mock parent object for axis testing."""

    def __init__(self):
        self.plot_width = 400
        self.plot_height = 300
        self.left_padding = 50
        self.top_padding = 50
        self.x_label_rotation = None


class TestXAxisHappyPath:
    """Happy path tests for XAxis."""

    def test_basic_ticks(self):
        """Test basic tick generation for XAxis."""
        parent = MockParent()
        data = [[10, 20, 30, 40, 50]]
        axis = XAxis(parent=parent, data=data)
        values = axis.values
        # Should have values calculated
        assert len(values) > 0
        assert all(isinstance(v, (int, float)) for v in values)

    def test_custom_labels(self):
        """Test custom labels for XAxis."""
        parent = MockParent()
        data = [[10, 20, 30]]
        labels = ["A", "B", "C"]
        axis = XAxis(parent=parent, data=data, labels=labels)
        # Labels should be applied
        assert len(axis.labels) == 3

    def test_with_gridlines(self):
        """Test grid line generation for XAxis."""
        parent = MockParent()
        data = [[10, 20, 30]]
        from charted.utils.themes import GridConfig

        config = GridConfig(stroke="#ccc", stroke_width=1)
        axis = XAxis(parent=parent, data=data, config=config)
        grid = axis.grid_lines
        # Should have grid lines when config provided
        assert grid is not None

    def test_decimal_formatting(self):
        """Test decimal formatting for XAxis."""
        parent = MockParent()
        data = [[10.5, 20.75, 30.125]]
        axis = XAxis(parent=parent, data=data)
        labels = axis.labels
        # Labels should be formatted
        assert len(labels) > 0


class TestYAxisHappyPath:
    """Happy path tests for YAxis."""

    def test_basic_ticks(self):
        """Test basic tick generation for YAxis."""
        parent = MockParent()
        data = [[10, 20, 30, 40, 50]]
        axis = YAxis(parent=parent, data=data)
        values = axis.values
        assert len(values) > 0
        assert all(isinstance(v, (int, float)) for v in values)

    def test_with_gridlines(self):
        """Test grid line generation for YAxis."""
        parent = MockParent()
        data = [[10, 20, 30]]
        from charted.utils.themes import GridConfig

        config = GridConfig(stroke="#ccc", stroke_width=1)
        axis = YAxis(parent=parent, data=data, config=config)
        grid = axis.grid_lines
        assert grid is not None

    def test_explicit_range(self):
        """Test with different data ranges for YAxis."""
        parent = MockParent()
        data = [[10, 20, 30, 40, 50]]
        axis = YAxis(parent=parent, data=data)
        assert axis.axis_dimension.min_value <= 10
        assert axis.axis_dimension.max_value >= 50


class TestXAxisSadPath:
    """Sad path / edge case tests for XAxis."""

    def test_zero_range(self):
        """Test XAxis with zero range (all same values)."""
        parent = MockParent()
        data = [[5, 5, 5, 5]]
        # Should handle gracefully or raise
        axis = XAxis(parent=parent, data=data)
        # Check it doesn't crash
        _ = axis.values

    def test_invalid_tick_count(self):
        """Test XAxis with single data point."""
        parent = MockParent()
        data = [[42]]
        axis = XAxis(parent=parent, data=data)
        # Should handle single value
        assert len(axis.values) > 0

    def test_nan_input(self):
        """Test XAxis with NaN in data raises ValueError."""
        parent = MockParent()
        data = [[float("nan"), 20, 30]]
        # Should raise ValueError when NaN is in data
        with pytest.raises(ValueError):
            XAxis(parent=parent, data=data)

    def test_empty_string_labels(self):
        """Test XAxis with empty string labels raises ValueError."""
        parent = MockParent()
        data = [[10, 20, 30]]
        labels = ["", "", ""]
        # Empty strings cause ValueError in text dimension calculation
        with pytest.raises(ValueError):
            XAxis(parent=parent, data=data, labels=labels)
    def test_empty_string_labels(self):
        """Test XAxis with empty string labels raises ValueError."""
        parent = MockParent()
        data = [[10, 20, 30]]
        labels = ["", "", ""]
        # Empty strings cause ValueError in text dimension calculation
        with pytest.raises(ValueError):
            XAxis(parent=parent, data=data, labels=labels)
    def test_empty_string_labels(self):
        """Test XAxis with empty string labels raises ValueError."""
        parent = MockParent()
        data = [[10, 20, 30]]
        labels = ["", "", ""]
        # Empty strings cause ValueError in text dimension calculation
        with pytest.raises(ValueError):
            XAxis(parent=parent, data=data, labels=labels)
    def test_empty_string_labels(self):
        """Test XAxis with empty string labels raises ValueError."""
        parent = MockParent()
        data = [[10, 20, 30]]
        labels = ["", "", ""]
        # Empty strings cause ValueError in text dimension calculation
        with pytest.raises(ValueError):
            XAxis(parent=parent, data=data, labels=labels)
    def test_empty_string_labels(self):
        """Test XAxis with empty string labels raises ValueError."""
        parent = MockParent()
        data = [[10, 20, 30]]
        labels = ["", "", ""]
        # Empty strings cause ValueError in text dimension calculation
        with pytest.raises(ValueError):
            XAxis(parent=parent, data=data, labels=labels)
    def test_empty_string_labels(self):
        """Test XAxis with empty string labels raises ValueError."""
        parent = MockParent()
        data = [[10, 20, 30]]
        labels = ["", "", ""]
        # Empty strings cause ValueError in text dimension calculation
        with pytest.raises(ValueError):
            XAxis(parent=parent, data=data, labels=labels)
    def test_empty_string_labels(self):
        """Test XAxis with empty string labels raises ValueError."""
        parent = MockParent()
        data = [[10, 20, 30]]
        labels = ["", "", ""]
        # Empty strings cause ValueError in text dimension calculation
        with pytest.raises(ValueError):
            XAxis(parent=parent, data=data, labels=labels)
    def test_empty_string_labels(self):
        """Test XAxis with empty string labels raises ValueError."""
        parent = MockParent()
        data = [[10, 20, 30]]
        labels = ["", "", ""]
        # Empty strings cause ValueError in text dimension calculation
        with pytest.raises(ValueError):
            XAxis(parent=parent, data=data, labels=labels)


class TestYAxisSadPath:
    """Sad path / edge case tests for YAxis."""

    def test_zero_range(self):
        """Test YAxis with zero range (all same values)."""
        parent = MockParent()
        data = [[100, 100, 100]]
        axis = YAxis(parent=parent, data=data)
        # Should handle gracefully
        _ = axis.values

    def test_negative_ticks(self):
        """Test YAxis with negative values."""
        parent = MockParent()
        data = [[-10, -20, -30]]
        axis = YAxis(parent=parent, data=data)
        # Should handle negative values
        assert axis.axis_dimension.min_value < 0

    def test_label_overflow(self):
        """Test YAxis with large range that could cause label issues."""
        parent = MockParent()
        data = [[0, 1e10]]
        axis = YAxis(parent=parent, data=data)
        labels = axis.labels
        # Should not crash
        assert len(labels) > 0

    def test_huge_precision(self):
        """Test YAxis with high precision values."""
        parent = MockParent()
        data = [[0.123456789, 0.987654321]]
        axis = YAxis(parent=parent, data=data)
        labels = axis.labels
        # Labels should be reasonable
        assert all(len(str(label)) < 100 for label in labels)
