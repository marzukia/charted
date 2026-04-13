import pytest

from charted.charts.axes import Axis, XAxis, YAxis


class TestAxis:
    """Tests for Axis base class."""

    def test_axis_init_with_labels(self):
        """Test Axis initialization with labels."""
        labels = ["A", "B", "C"]
        axis = Axis(parent=None, labels=labels)
        assert axis.labels is not None

    def test_axis_init_with_data(self):
        """Test Axis initialization with data."""
        data = [[1, 2, 3]]
        axis = Axis(parent=None, data=data)
        assert axis.data == data

    def test_axis_init_with_data_and_labels(self):
        """Test Axis initialization with both data and labels."""
        data = [[1, 2, 3]]
        labels = ["A", "B", "C"]
        axis = Axis(parent=None, data=data, labels=labels)
        assert axis.labels is not None

    def test_axis_init_raises_error_without_data_or_labels(self):
        """Test Axis raises error without data or labels."""
        with pytest.raises(Exception, match="Need labels or data"):
            Axis(parent=None)

    def test_axis_stacked_property(self):
        """Test Axis stacked property."""
        data = [[1, 2, 3]]
        axis = Axis(parent=None, data=data, stacked=True)
        assert axis.stacked is True

    def test_axis_values_property(self):
        """Test Axis values property."""
        data = [[1, 2, 3]]
        axis = Axis(parent=None, data=data)
        assert axis.values is not None

    def test_axis_zero_index_property(self):
        """Test Axis zero_index parameter."""
        data = [[1, 2, 3]]
        axis = Axis(parent=None, data=data, zero_index=True)
        assert axis.values is not None

    def test_axis_calculate_axis_dimensions_stacked(self):
        """Test calculate_axis_dimensions with stacked data."""
        data = [[1, 2, 3], [4, 5, 6]]
        result = Axis.calculate_axis_dimensions(data=data, stacked=True)
        assert result.min_value == 0
        assert result.max_value == 9  # 3 + 6

    def test_axis_calculate_axis_dimensions_non_stacked(self):
        """Test calculate_axis_dimensions with non-stacked data."""
        data = [[1, 2, 3], [4, 5, 6]]
        result = Axis.calculate_axis_dimensions(data=data, stacked=False, zero_index=False)
        assert result.min_value == 1
        assert result.max_value == 6

    def test_axis_calculate_axis_dimensions_zero_index(self):
        """Test calculate_axis_dimensions with zero_index."""
        data = [[10, 20, 30]]
        result = Axis.calculate_axis_dimensions(data=data, zero_index=True)
        assert result.min_value == 0

    def test_axis_calculate_axis_dimensions_negative_values(self):
        """Test calculate_axis_dimensions with negative values."""
        data = [[-10, 0, 10]]
        result = Axis.calculate_axis_dimensions(data=data, zero_index=False)
        assert result.min_value < 0
        assert result.max_value == 10

    def test_axis_calculate_axis_dimensions_single_series(self):
        """Test calculate_axis_dimensions with single series."""
        data = [[1, 2, 3, 4, 5]]
        result = Axis.calculate_axis_dimensions(data=data)
        assert result.count == 5

    def test_axis_calculate_axis_values(self):
        """Test calculate_axis_values method."""
        data = [[0, 10, 20, 30, 40, 50]]
        axd, values = Axis.calculate_axis_values(data=data)
        assert axd.count == 6
        assert len(values) > 0


    def test_axis_values_setter(self):
        """Test Axis values setter."""
        data = [[1, 2, 3]]
        axis = Axis(parent=None, data=data)
        assert axis.values is not None


class TestXAxis:
    """Tests for XAxis class."""

    def test_xaxis_reproject(self):
        """Test XAxis reproject method."""
        from unittest.mock import MagicMock

        parent = MagicMock()
        parent.plot_width = 500
        parent.left_padding = 50
        parent.top_padding = 50
        parent.plot_height = 400

        xaxis = XAxis(parent=parent, data=[[0, 1, 2]])
        result = xaxis.reproject(0.5)
        assert result > 0

    def test_xaxis_reverse(self):
        """Test XAxis reverse method."""
        from unittest.mock import MagicMock

        parent = MagicMock()
        parent.plot_width = 500
        parent.left_padding = 50
        parent.top_padding = 50
        parent.plot_height = 400

        xaxis = XAxis(parent=parent, data=[[0, 1, 2]])
        result = xaxis.reverse(100)
        assert result is not None

    def test_xaxis_coordinates(self):
        """Test XAxis coordinates property."""
        from unittest.mock import MagicMock

        parent = MagicMock()
        parent.plot_width = 500
        parent.left_padding = 50
        parent.top_padding = 50
        parent.plot_height = 400

        xaxis = XAxis(parent=parent, data=[[0, 1, 2]])
        coords = xaxis.coordinates
        assert coords is not None
        assert len(coords) > 0

    def test_xaxis_grid_lines(self):
        """Test XAxis grid_lines property."""
        from unittest.mock import MagicMock

        parent = MagicMock()
        parent.plot_width = 500
        parent.plot_height = 400
        parent.left_padding = 50
        parent.top_padding = 50
        parent.config = MagicMock()
        parent.config.grid_style = {"stroke": "gray", "stroke_width": 1}

        xaxis = XAxis(parent=parent, data=[[0, 1, 2]])
        grid = xaxis.grid_lines
        assert grid is not None

    def test_xaxis_axis_labels(self):
        """Test XAxis axis_labels property."""
        from unittest.mock import MagicMock

        parent = MagicMock()
        parent.plot_width = 500
        parent.plot_height = 400
        parent.left_padding = 50
        parent.top_padding = 50
        parent.x_label_rotation = None

        xaxis = XAxis(parent=parent, data=[[0, 1, 2]], labels=["A", "B", "C"])
        labels = xaxis.axis_labels
        assert labels is not None


class TestYAxis:
    """Tests for YAxis class."""

    def test_yaxis_reproject(self):
        """Test YAxis reproject method."""
        from unittest.mock import MagicMock

        parent = MagicMock()
        parent.plot_width = 500
        parent.left_padding = 50
        parent.top_padding = 50
        parent.plot_height = 400

        yaxis = YAxis(parent=parent, data=[[0, 1, 2]])
        result = yaxis.reproject(0.5)
        assert result is not None

    def test_yaxis_reverse(self):
        """Test YAxis reverse method."""
        from unittest.mock import MagicMock

        parent = MagicMock()
        parent.plot_width = 500
        parent.left_padding = 50
        parent.top_padding = 50
        parent.plot_height = 400

        yaxis = YAxis(parent=parent, data=[[0, 1, 2]])
        result = yaxis.reverse(100)
        assert result is not None

    def test_yaxis_coordinates(self):
        """Test YAxis coordinates property."""
        from unittest.mock import MagicMock

        parent = MagicMock()
        parent.plot_width = 500
        parent.plot_height = 400
        parent.left_padding = 50
        parent.top_padding = 50

        yaxis = YAxis(parent=parent, data=[[0, 1, 2]])
        coords = yaxis.coordinates
        assert coords is not None
        assert len(coords) > 0

    def test_yaxis_coordinates_with_stacked_negative(self):
        """Test YAxis coordinates with stacked negative values."""
        from unittest.mock import MagicMock

        parent = MagicMock()
        parent.plot_width = 500
        parent.plot_height = 400
        parent.left_padding = 50
        parent.top_padding = 50

        yaxis = YAxis(parent=parent, data=[[-10, 5, 15]], stacked=True)
        coords = yaxis.coordinates
        assert coords is not None

    def test_yaxis_grid_lines(self):
        """Test YAxis grid_lines property."""
        from unittest.mock import MagicMock

        parent = MagicMock()
        parent.plot_width = 500
        parent.plot_height = 400
        parent.config = MagicMock()
        parent.config.grid_style = {"stroke": "gray", "stroke_width": 1}
        parent.left_padding = 50
        parent.top_padding = 50

        yaxis = YAxis(parent=parent, data=[[0, 1, 2]])
        grid = yaxis.grid_lines
        assert grid is not None

    def test_yaxis_axis_labels(self):
        """Test YAxis axis_labels property."""
        from unittest.mock import MagicMock

        parent = MagicMock()
        parent.plot_width = 500
        parent.plot_height = 400
        parent.left_padding = 50
        parent.top_padding = 50

        yaxis = YAxis(parent=parent, data=[[0, 1, 2]], labels=["0", "1", "2"])
        labels = yaxis.axis_labels
        assert labels is not None
