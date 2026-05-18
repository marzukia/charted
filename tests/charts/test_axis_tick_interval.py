"""Test suite for axis tick interval functionality with proper zero handling."""

from charted.charts.axes import XAxis, YAxis


class MockParent:
    """Mock parent object for axis testing."""

    def __init__(self):
        self.plot_width = 400
        self.plot_height = 300
        self.left_padding = 50
        self.top_padding = 50
        self.x_label_rotation = None


class TestAxisTickIntervalZeroHandling:
    """Tests ensuring zero is rendered when axis spans across it."""

    def test_yaxis_zero_included_negative_to_positive(self):
        """Y-axis spanning negative to positive must include zero in labels."""
        parent = MockParent()
        data = [[-50, -30, 20, 40, 60]]
        axis = YAxis(parent=parent, data=data, axis_tick_interval=2)
        values = axis.values

        # Zero must be in the label values when spanning negative to positive
        assert any(abs(v) < 1e-9 for v in values), (
            f"Zero should be in labels when spanning negative to positive. Got: {values}"
        )

    def test_xaxis_zero_included_negative_to_positive(self):
        """X-axis spanning negative to positive must include zero in labels."""
        parent = MockParent()
        # For XY charts, data[0] contains the x values, labels are for display
        data = [[-2, -1, 0, 1, 2]]
        labels = ["A", "B", "C", "D", "E"]
        axis = XAxis(parent=parent, data=data, labels=labels)

        # For XY charts with negative to positive, zero should be in the values
        assert any(abs(v) < 1e-9 for v in axis.values), (
            f"Zero should be in X-axis labels. Got: {axis.values}"
        )

    def test_yaxis_zero_included_large_interval(self):
        """Y-axis with large interval still includes zero when spanning negative to positive."""
        parent = MockParent()
        data = [[-100, -50, 50, 100]]
        axis = YAxis(parent=parent, data=data, axis_tick_interval=3)
        values = axis.values

        # Zero must be in the label values
        assert any(abs(v) < 1e-9 for v in values), (
            f"Zero should be in labels. Got: {values}"
        )

    def test_yaxis_zero_in_grid_lines(self):
        """Grid lines should always include zero when spanning negative to positive."""
        parent = MockParent()
        data = [[-50, -30, 20, 40, 60]]
        axis = YAxis(parent=parent, data=data, axis_tick_interval=2)
        grid_values = axis._grid_line_values

        # Zero must be in grid lines
        assert any(abs(v) < 1e-9 for v in grid_values), (
            f"Zero should be in grid lines. Got: {grid_values}"
        )

    def test_yaxis_all_negative_zero_index_true(self):
        """Y-axis with all negative values and zero_index=True should include zero."""
        parent = MockParent()
        data = [[-50, -40, -30, -20, -10]]
        axis = YAxis(parent=parent, data=data, zero_index=True)
        values = axis.values

        # When zero_index=True and all values are negative,
        # the axis max should be 0 (zero_index forces axis to extend to zero)
        # Zero should be included in labels since max_value is 0
        assert any(abs(v) < 1e-9 for v in values), (
            f"Zero should be in labels with zero_index=True for all-negative data. Got: {values}"
        )
        assert axis.axis_dimension.max_value == 0, (
            f"max_value should be 0 with zero_index=True for all-negative data. Got: {axis.axis_dimension.max_value}"
        )

    def test_tick_interval_string_percentage(self):
        """Test string percentage interval (e.g., '25%')."""
        parent = MockParent()
        data = [[0, 25, 50, 75, 100, 125, 150, 175, 200]]
        axis = YAxis(parent=parent, data=data, axis_tick_interval="25%")
        values = axis.values

        # Should have fewer values than default
        assert len(values) <= 8, (
            f"Too many labels for 25% interval. Got {len(values)}: {values}"
        )

    def test_tick_interval_float_proportion(self):
        """Test float proportion interval (e.g., 0.2 = 20%)."""
        parent = MockParent()
        data = [[0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200]]
        axis = YAxis(parent=parent, data=data, axis_tick_interval=0.2)
        values = axis.values

        # Should have approximately 20% of all ticks
        assert len(values) > 0, "Should have some labels"

    def test_tick_interval_integer_every_nth(self):
        """Test integer interval shows every Nth tick."""
        parent = MockParent()
        data = [[0, 10, 20, 30, 40, 50, 60, 70, 80]]
        axis = YAxis(parent=parent, data=data, axis_tick_interval=2)
        values = axis.values

        # With interval=2, should show roughly half the ticks
        assert len(values) <= 6, (
            f"Should have fewer labels with interval=2. Got {len(values)}: {values}"
        )


class TestAxisTickIntervalGenerateFunction:
    """Tests for the generate_tick_values class method."""

    def test_generate_ticks_spans_zero(self):
        """generate_tick_values should include zero when spanning negative to positive."""
        labels, grids = YAxis.generate_tick_values(
            min_value=-50, max_value=60, axis_tick_interval=2
        )

        # Zero must be in both labels and grids
        assert any(abs(v) < 1e-9 for v in labels), (
            f"Zero should be in labels. Got: {labels}"
        )
        assert any(abs(v) < 1e-9 for v in grids), (
            f"Zero should be in grids. Got: {grids}"
        )

    def test_generate_ticks_all_positive(self):
        """generate_tick_values for all positive range."""
        labels, grids = YAxis.generate_tick_values(
            min_value=10, max_value=100, axis_tick_interval=2
        )

        # All values should be positive
        assert all(v >= 0 for v in labels), (
            f"All values should be positive. Got: {labels}"
        )

    def test_generate_ticks_all_negative(self):
        """generate_tick_values for all negative range."""
        labels, grids = YAxis.generate_tick_values(
            min_value=-100, max_value=-10, axis_tick_interval=2
        )

        # All values should be negative
        assert all(v <= 0 for v in labels), (
            f"All values should be negative. Got: {labels}"
        )

    def test_generate_ticks_no_interval(self):
        """generate_tick_values without interval uses default behavior."""
        labels, grids = YAxis.generate_tick_values(
            min_value=0, max_value=100, axis_tick_interval=None
        )

        # Should have reasonable number of ticks
        assert len(labels) > 0, "Should have some labels"

    def test_generate_ticks_small_range(self):
        """generate_tick_values for small range."""
        labels, grids = YAxis.generate_tick_values(
            min_value=99, max_value=100, axis_tick_interval=2
        )

        # Should handle small ranges gracefully
        assert len(labels) > 0, "Should have some labels"

    def test_generate_ticks_large_range(self):
        """generate_tick_values for large range."""
        labels, grids = YAxis.generate_tick_values(
            min_value=-1000, max_value=1000, axis_tick_interval=2
        )

        # Zero should be included
        assert any(abs(v) < 1e-9 for v in labels), (
            f"Zero should be in labels for large range. Got: {labels}"
        )
