"""Property-based tests for DataModel validation and normalization.

These tests use Hypothesis to generate edge cases and verify invariants.
"""

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from charted.utils.data_model import DataModel
from charted.utils.exceptions import InvalidDataError


# Strategies for generating test data
@st.composite
def valid_numeric_data(draw):
    """Generate valid numeric data (single or multi-series)."""
    # Generate 1-5 series with 1-10 values each
    num_series = draw(st.integers(1, 5))
    series_length = draw(st.integers(1, 10))

    # Generate series with various numeric types
    series = []
    for _ in range(num_series):
        values = []
        for _ in range(series_length):
            if draw(st.booleans()):
                values.append(draw(st.integers(-1000, 1000)))
            else:
                values.append(
                    draw(
                        st.floats(
                            min_value=-1e6,
                            max_value=1e6,
                            allow_nan=False,
                            allow_infinity=False,
                        )
                    )
                )
        series.append(values)

    # Return single series or multi-series
    if num_series == 1:
        return series[0]
    return series


@st.composite
def invalid_data_with_nan(draw):
    """Generate data containing NaN values."""
    series_length = draw(st.integers(1, 5))
    pos = draw(st.integers(0, series_length - 1))

    values = [
        draw(st.floats(min_value=-100, max_value=100)) for _ in range(series_length)
    ]
    values[pos] = float("nan")

    return values


@st.composite
def invalid_data_with_infinity(draw):
    """Generate data containing infinity values."""
    series_length = draw(st.integers(1, 5))
    pos = draw(st.integers(0, series_length - 1))

    values = [
        draw(st.floats(min_value=-100, max_value=100)) for _ in range(series_length)
    ]
    values[pos] = draw(st.sampled_from([float("inf"), float("-inf")]))

    return values


@st.composite
def invalid_mismatched_series(draw):
    """Generate data with mismatched series lengths."""
    # Create 2 series with different lengths (small to avoid health check)
    first_length = draw(st.integers(1, 3))
    second_length = draw(st.integers(1, 3))

    # Ensure they're different
    while second_length == first_length:
        second_length = draw(st.integers(1, 3))

    series1 = [
        draw(st.floats(min_value=-100, max_value=100)) for _ in range(first_length)
    ]
    series2 = [
        draw(st.floats(min_value=-100, max_value=100)) for _ in range(second_length)
    ]

    return [series1, series2]


@st.composite
def valid_labels(draw):
    """Generate valid label lists."""
    num_labels = draw(st.integers(1, 10))
    labels = [draw(st.text(min_size=1, max_size=20)) for _ in range(num_labels)]
    return labels


class TestDataModelValidation:
    """Property tests for DataModel validation logic."""

    @given(valid_numeric_data())
    @settings(max_examples=50)
    def test_validate_accepts_valid_numeric_data(self, data):
        """Valid numeric data should pass validation."""
        result = DataModel.validate_data(data)
        assert result is not None
        assert isinstance(result, list)
        # Ensure 2D structure
        assert all(isinstance(series, list) for series in result)

    @given(invalid_data_with_nan())
    @settings(max_examples=50)
    def test_validate_rejects_nan_values(self, data):
        """NaN values should be rejected."""
        with pytest.raises(InvalidDataError, match="NaN"):
            DataModel.validate_data(data)

    @given(invalid_data_with_infinity())
    @settings(max_examples=50)
    def test_validate_accepts_infinity_values(self, data):
        """Infinity values are allowed (only NaN is rejected)."""
        # Note: Current implementation only checks for NaN, not infinity
        result = DataModel.validate_data(data)
        assert result is not None

    @given(invalid_mismatched_series())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.large_base_example])
    def test_validate_rejects_mismatched_lengths(self, data):
        """Series with different lengths should be rejected."""
        from charted import InvalidDataError

        with pytest.raises(InvalidDataError, match="same length"):
            DataModel.validate_data(data)

    def test_validate_rejects_empty_list(self):
        """Empty list should raise ValueError."""
        from charted import NoDataError

        with pytest.raises(NoDataError, match="No data"):
            DataModel.validate_data([])

    @given(st.integers(1, 20))
    @settings(max_examples=50)
    def test_create_default_labels_correct_count(self, length):
        """Default labels should match the array length."""
        labels = DataModel.create_default_labels(length)
        assert len(labels) == length
        assert labels == [str(i) for i in range(length)]


class TestDataModelInvariants:
    """Property tests for DataModel invariants."""

    @given(valid_numeric_data())
    @settings(max_examples=50)
    def test_data_preserves_values(self, data):
        """DataModel should preserve all original values."""
        model = DataModel(y_data=data)
        validated = model.y_data

        # Flatten both for comparison
        if isinstance(data[0], list):
            original_flat = [v for series in data for v in series]
        else:
            original_flat = list(data)
        validated_flat = [v for series in validated for v in series]

        assert len(original_flat) == len(validated_flat)
        for orig, val in zip(original_flat, validated_flat):
            assert orig == val

    @given(valid_numeric_data(), st.booleans())
    @settings(max_examples=50)
    def test_zero_index_property_preserved(self, data, zero_index):
        """zero_index property should be preserved after initialization."""
        model = DataModel(y_data=data, zero_index=zero_index)
        assert model.zero_index == zero_index

    @given(valid_labels())
    @settings(max_examples=50)
    def test_labels_get_text_dimensions(self, labels):
        """Labels should be converted to MeasuredText objects."""
        model = DataModel(x_labels=labels)
        assert model.x_labels is not None
        # Each label should have width and height properties
        for measured in model.x_labels:
            assert hasattr(measured, "width")
            assert hasattr(measured, "height")

    @given(st.lists(st.floats(min_value=-100, max_value=100), min_size=1, max_size=10))
    @settings(max_examples=50)
    def test_y_count_matches_data_length(self, y_values):
        """y_count should match the length of y_data."""
        model = DataModel(y_data=y_values)
        assert model.y_count == len(y_values)

    @given(st.lists(st.floats(min_value=-100, max_value=100), min_size=1, max_size=10))
    @settings(max_examples=50)
    def test_x_data_defaults_to_none_when_not_provided(self, y_values):
        """When x_data is None, it should remain None."""
        model = DataModel(y_data=y_values, x_data=None)
        assert model.x_data is None

    def test_x_count_uses_labels_when_no_data(self):
        """x_count should use labels when no x_data is provided."""
        labels = ["A", "B", "C"]
        model = DataModel(x_labels=labels, x_data=None)
        assert model.x_count == len(labels)

    def test_y_count_uses_labels_when_no_data(self):
        """y_count should use labels when no y_data is provided."""
        labels = ["10", "20", "30", "40"]
        model = DataModel(y_labels=labels, y_data=None)
        assert model.y_count == len(labels)


class TestDataModelEdgeCases:
    """Property tests for edge cases in DataModel."""

    @given(
        st.floats(
            min_value=-1e10, max_value=1e10, allow_nan=False, allow_infinity=False
        )
    )
    @settings(max_examples=50)
    def test_very_large_values_accepted(self, value):
        """Very large numeric values should be accepted."""
        model = DataModel(y_data=[[value]])
        assert model.y_data[0][0] == value

    @given(
        st.floats(
            min_value=-1e-10, max_value=1e-10, allow_nan=False, allow_infinity=False
        )
    )
    @settings(max_examples=50)
    def test_very_small_values_accepted(self, value):
        """Very small numeric values should be accepted."""
        model = DataModel(y_data=[[value]])
        assert model.y_data[0][0] == value

    def test_single_element_data(self):
        """Single element data should work correctly."""
        model = DataModel(y_data=[[42]])
        assert model.y_count == 1
        assert model.y_data[0][0] == 42

    def test_empty_list_raises_error(self):
        """Empty list should raise an error."""
        with pytest.raises(Exception):
            DataModel.validate_data([])

    def test_none_data_returns_none(self):
        """None data should return None from validate_data."""
        result = DataModel.validate_data(None)
        assert result is None

    def test_rejects_non_numeric_values(self):
        """Non-numeric values should raise InvalidDataError."""
        with pytest.raises(InvalidDataError, match="Invalid data value"):
            DataModel.validate_data([1, 2, "three", 4])

    @given(
        st.lists(st.sampled_from(["a", None, {"key": "val"}]), min_size=1, max_size=3)
    )
    @settings(max_examples=30)
    def test_rejects_various_invalid_types(self, invalid_values):
        """Various non-numeric types should be rejected."""
        with pytest.raises(InvalidDataError, match="Invalid data value"):
            DataModel.validate_data(invalid_values)
