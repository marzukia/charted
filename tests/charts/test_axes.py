"""Test suite for axis rendering (XAxis, YAxis)."""

import math

import pytest

from charted.charts.axes import XAxis, YAxis
from charted.utils.types import MeasuredText


def _mt(text: str, width: float, height: float = 9.0) -> MeasuredText:
    """Build a MeasuredText with explicit dimensions for overlap tests."""
    return MeasuredText(text=text, width=width, height=height)


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
        config = {"stroke": "#ccc", "stroke_dasharray": "None"}
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

    def test_thousands_separator(self):
        """Mid-range numeric tick labels are grouped with thousands separators.

        Values at or above 1e6 switch to scientific notation, so this checks a
        range whose ticks land in the grouped-but-not-extreme band.
        """
        parent = MockParent()
        data = [[0, 500000]]
        axis = YAxis(parent=parent, data=data)
        texts = [label.text for label in axis.labels]
        assert "500,000" in texts
        # Small values stay ungrouped.
        assert not any("," in t and len(t.replace(",", "")) <= 3 for t in texts)

    def test_extreme_magnitude_scientific_notation(self):
        """Huge tick values render in scientific notation, not long grouped strings."""
        parent = MockParent()
        data = [[0, 1_000_000_000]]
        axis = YAxis(parent=parent, data=data)
        texts = [label.text for label in axis.labels]
        assert "1e9" in texts
        assert not any("," in t for t in texts)


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
        config = {"stroke": "#ccc", "stroke_dasharray": "None"}
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
        """Test XAxis with empty string labels renders without error."""
        parent = MockParent()
        data = [[10, 20, 30]]
        labels = ["", "", ""]
        # Empty strings now render as blank labels
        axis = XAxis(parent=parent, data=data, labels=labels)
        assert axis is not None
        assert len(axis.labels) == 3
        assert all(label.text == "" for label in axis.labels)


class TestXAxisLabelThinning:
    """Tick-thinning on dense ordinal X axes."""

    def test_small_label_count_draws_all(self):
        """Small axes keep every label (no thinning)."""
        parent = MockParent()
        data = [[1, 2, 3, 4, 5]]
        labels = [f"cat{i}" for i in range(5)]
        axis = XAxis(parent=parent, data=data, labels=labels)
        drawn = axis.axis_labels.children
        # Padding adds two blanks, but every label is drawn for small counts.
        assert len(drawn) == len(axis.labels)

    def test_dense_axis_thins_labels(self):
        """A dense ordinal axis renders only a subset of its labels."""
        parent = MockParent()
        labels = [f"cat{i}" for i in range(100)]
        data = [list(range(len(labels)))]
        axis = XAxis(parent=parent, data=data, labels=labels)
        total = len(axis.labels)
        drawn = axis.axis_labels.children
        assert len(drawn) < total
        # Endpoints are always kept.
        drawn_texts = [c.children[0] for c in drawn]
        assert axis.labels[0].text in drawn_texts
        assert axis.labels[-1].text in drawn_texts


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
        # Labels should be formatted
        assert len(labels) > 0


class TestNonOverlappingIndices:
    """Direct unit tests for ``XAxis._non_overlapping_indices``.

    This pass decides which tick labels survive a width-aware overlap drop.
    A silent bug here would quietly remove labels users need, so the kept set
    is pinned directly rather than only through the geometric-invariant suite.
    """

    def test_fitting_labels_keep_every_index(self):
        """Well-spaced labels never collide, so all are kept."""
        coords = [0.0, 50.0, 100.0, 150.0]
        labels = [_mt("a", 10.0) for _ in coords]
        keep = XAxis._non_overlapping_indices(coords, labels, dx=0.0)
        assert keep == {0, 1, 2, 3}

    def test_single_and_empty(self):
        """Zero or one label is always fully kept (no neighbour to clear)."""
        assert XAxis._non_overlapping_indices([], [], dx=0.0) == set()
        assert XAxis._non_overlapping_indices([5.0], [_mt("a", 99.0)], dx=0.0) == {0}

    def test_colliding_middles_drop_to_minimal_set(self):
        """Wide labels packed tightly keep first, last, and minimal middles.

        Boxes are centred half-widths: at width 40 on a 20px pitch every
        neighbour overlaps, so the greedy pass keeps index 0, the first middle
        that clears it (2), and the forced final (4).
        """
        coords = [0.0, 20.0, 40.0, 60.0, 80.0]
        labels = [_mt(str(i), 40.0) for i in range(5)]
        keep = XAxis._non_overlapping_indices(coords, labels, dx=0.0)
        assert keep == {0, 2, 4}

    def test_first_and_last_always_retained(self):
        """Even with everything colliding, the axis range stays labelled."""
        coords = [0.0, 5.0, 10.0, 15.0]
        labels = [_mt(str(i), 80.0) for i in range(4)]
        keep = XAxis._non_overlapping_indices(coords, labels, dx=0.0)
        assert 0 in keep
        assert 3 in keep

    def test_chain_collision_drops_only_the_blocker(self):
        """A final label colliding with the last middle pops just that middle.

        Coords/widths are chosen so the greedy pass keeps {0, 1, 2} and then the
        forced final (3) overlaps only the last kept middle (2). The pass must
        drop index 2 and keep index 1, not cascade further.
        """
        coords = [0.0, 30.0, 55.0, 60.0]
        labels = [_mt(str(i), 20.0) for i in range(4)]
        keep = XAxis._non_overlapping_indices(coords, labels, dx=0.0)
        assert keep == {0, 1, 3}

    def test_dx_shift_does_not_change_relative_overlap(self):
        """A uniform dx offset shifts every box equally; the kept set is stable."""
        coords = [0.0, 20.0, 40.0, 60.0, 80.0]
        labels = [_mt(str(i), 40.0) for i in range(5)]
        base = XAxis._non_overlapping_indices(coords, labels, dx=0.0)
        shifted = XAxis._non_overlapping_indices(coords, labels, dx=17.0)
        assert base == shifted == {0, 2, 4}

    def test_rotated_span_projects_full_footprint(self):
        """The rotated x-span matches the projected corners of the tilted box."""
        label = _mt("AB", 20.0, height=10.0)
        left, right = XAxis._rotated_x_span(100.0, label, rotation_angle=30.0)
        char_shift = label.width / len(label.text)  # 10.0
        rad = math.radians(30.0)
        cos, sin = math.cos(rad), math.sin(rad)
        xs = [
            px * cos - py * sin
            for px in (-char_shift, -char_shift + label.width)
            for py in (-label.height, 0.0)
        ]
        assert left == pytest.approx(100.0 + min(xs))
        assert right == pytest.approx(100.0 + max(xs))

    def test_rotated_fitting_labels_keep_every_index(self):
        """Rotated labels that clear their neighbour are all kept."""
        coords = [0.0, 200.0, 400.0]
        labels = [_mt("x", 8.0, height=9.0) for _ in coords]
        keep = XAxis._non_overlapping_indices(
            coords, labels, dx=0.0, rotation_angle=45.0
        )
        assert keep == {0, 1, 2}

    def test_rotated_colliding_labels_drop(self):
        """Steeply rotated wide labels on a tight pitch collide and are thinned.

        At 60 degrees the projected footprint of each 60px-wide label spans well
        past the 30px pitch, so the pass keeps first, last, and a minimal middle
        rather than the overlapping full set.
        """
        coords = [0.0, 30.0, 60.0, 90.0, 120.0]
        labels = [_mt("wide" + str(i), 60.0, height=12.0) for i in range(5)]
        keep = XAxis._non_overlapping_indices(
            coords, labels, dx=0.0, rotation_angle=60.0
        )
        assert keep != {0, 1, 2, 3, 4}
        assert 0 in keep and 4 in keep
        assert len(keep) < 5
