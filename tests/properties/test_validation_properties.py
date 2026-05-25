"""Property-based tests for validation utilities using hypothesis.

These tests generate random inputs to find edge cases in data validation logic.
Install hypothesis: uv pip install hypothesis
Run: pytest tests/properties/ --hypothesis-seed=0
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from charted.utils.exceptions import InvalidValue
from charted.utils.validation import (
    create_default_labels,
    get_data_length,
    match_data_series,
    normalize_labels,
    validate_attribute_value,
    validate_data,
    validate_padding,
    validate_series_count,
)

# ============================================================
# validate_data Properties
# ============================================================


@given(
    data=st.lists(
        st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10
    ),
)
@settings(max_examples=50)
def test_validate_data_1d_returns_2d(data):
    """validate_data should convert 1D to 2D list."""
    result = validate_data(data)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0] == data


@given(
    length=st.integers(min_value=1, max_value=5),
)
@settings(max_examples=50)
def test_validate_data_2d_preserves_structure(length):
    """validate_data should preserve 2D structure."""
    # Generate data with matching lengths
    data = [[1.0, 2.0, 3.0][:length] for _ in range(2)]
    result = validate_data(data)

    assert isinstance(result, list)
    assert len(result) == len(data)
    for i, series in enumerate(result):
        assert series == data[i]


@given(
    data=st.just([]),
)
@settings(max_examples=20)
def test_validate_data_empty_raises(data):
    """validate_data should raise for empty input."""
    with pytest.raises(Exception, match="No data"):
        validate_data([])


@given(
    data1=st.lists(
        st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=3
    ),
    data2=st.lists(
        st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=3
    ),
)
@settings(max_examples=50)
def test_validate_data_mismatched_lengths_raises(data1, data2):
    """validate_data should raise for mismatched series lengths."""
    if len(data1) != len(data2):
        with pytest.raises(Exception, match="Data shape mismatch"):
            validate_data([data1, data2])


@given(
    data=st.none(),
)
@settings(max_examples=20)
def test_validate_data_none_returns_none(data):
    """validate_data should return None for None input."""
    result = validate_data(data)

    assert result is None


# ============================================================
# validate_attribute_value Properties
# ============================================================


@given(
    name=st.text(min_size=1, max_size=20),
    value=st.floats(min_value=0, max_value=1e10),
)
@settings(max_examples=50)
def test_validate_attribute_value_non_negative_passes(name, value):
    """validate_attribute_value should accept non-negative values."""
    result = validate_attribute_value(name, value)

    assert result == value


@given(
    name=st.text(min_size=1, max_size=20),
    value=st.floats(max_value=-0.0001),
)
@settings(max_examples=50)
def test_validate_attribute_value_negative_raises(name, value):
    """validate_attribute_value should reject negative values."""
    with pytest.raises(InvalidValue):
        validate_attribute_value(name, value)


@given(
    value=st.floats(min_value=0),
)
@settings(max_examples=30)
def test_validate_attribute_value_zero_passes(value):
    """validate_attribute_value should accept zero."""
    result = validate_attribute_value("test", 0.0)

    assert result == 0.0


# ============================================================
# validate_padding Properties
# ============================================================


@given(
    value=st.floats(min_value=0, max_value=1.0),
)
@settings(max_examples=50)
def test_validate_padding_in_range_passes(value):
    """validate_padding should accept values in [0, 1]."""
    result = validate_padding(value)

    assert result == value


@given(
    value=st.floats(min_value=1.0001, max_value=10.0),
)
@settings(max_examples=50)
def test_validate_padding_above_max_raises(value):
    """validate_padding should reject values > 1.0."""
    with pytest.raises(InvalidValue):
        validate_padding(value)


@given(
    value=st.floats(max_value=-0.0001),
)
@settings(max_examples=50)
def test_validate_padding_negative_raises(value):
    """validate_padding should reject negative values."""
    with pytest.raises(InvalidValue):
        validate_padding(value)


@given(
    value=st.floats(min_value=0, max_value=10.0),
    max_val=st.floats(min_value=0.5, max_value=2.0),
)
@settings(max_examples=50)
def test_validate_padding_custom_max(value, max_val):
    """validate_padding should respect custom max_value."""
    if value <= max_val:
        result = validate_padding(value, max_value=max_val)
        assert result == value
    else:
        with pytest.raises(InvalidValue):
            validate_padding(value, max_value=max_val)


# ============================================================
# validate_series_count Properties
# ============================================================


@given(
    target=st.integers(min_value=1, max_value=10),
)
@settings(max_examples=50)
def test_validate_series_count_none_returns_target(target):
    """validate_series_count with None styles should return target."""
    result = validate_series_count(None, target)

    assert result == target


@given(
    styles=st.lists(st.just({}), min_size=1, max_size=10),
    target=st.integers(min_value=1, max_value=10),
)
@settings(max_examples=50)
def test_validate_series_count_returns_max(styles, target):
    """validate_series_count should return max(styles length, target)."""
    result = validate_series_count(styles, target)

    expected = max(len(styles), target)
    assert result == expected


# ============================================================
# match_data_series Properties
# ============================================================


@given(
    y_data=st.lists(
        st.lists(
            st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=5
        ),
        min_size=1,
        max_size=3,
    ),
)
@settings(max_examples=50)
def test_match_data_series_none_x_expands(y_data):
    """match_data_series should expand None x_data to match y_data."""
    result = match_data_series(None, y_data)

    assert len(result) == len(y_data)
    # Each row should have same length as first y_data row
    if y_data:
        expected_len = len(y_data[0])
        for row in result:
            assert len(row) == expected_len


@given(
    x_series=st.lists(
        st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=5
    ),
    y_data=st.lists(
        st.lists(
            st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=5
        ),
        min_size=1,
        max_size=3,
    ),
)
@settings(max_examples=50)
def test_match_data_series_single_x_expands(x_series, y_data):
    """match_data_series should expand single x_series to match y_data count."""
    result = match_data_series([x_series], y_data)

    assert len(result) == len(y_data)


@given(
    x_data=st.lists(
        st.lists(
            st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=5
        ),
        min_size=1,
        max_size=3,
    ),
    y_data=st.lists(
        st.lists(
            st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=5
        ),
        min_size=1,
        max_size=3,
    ),
)
@settings(max_examples=50)
def test_match_data_series_matching_counts_returns_x(x_data, y_data):
    """match_data_series should return x_data when counts match."""
    if len(x_data) == len(y_data):
        result = match_data_series(x_data, y_data)

        assert result == x_data


# ============================================================
# normalize_labels Properties
# ============================================================


@given(
    labels=st.lists(st.text(), min_size=1, max_size=10),
)
@settings(max_examples=50)
def test_normalize_labels_returns_list(labels):
    """normalize_labels should return list copy."""
    result = normalize_labels(labels)

    assert isinstance(result, list)
    assert result == labels
    assert result is not labels  # Different object


@given(
    labels=st.none(),
)
@settings(max_examples=20)
def test_normalize_labels_none_returns_none(labels):
    """normalize_labels should return None for None input."""
    result = normalize_labels(labels)

    assert result is None


@given(
    labels=st.lists(st.text(), min_size=1, max_size=5),
)
@settings(max_examples=30)
def test_normalize_labels_preserves_content(labels):
    """normalize_labels should preserve all label content."""
    result = normalize_labels(labels)

    for i, label in enumerate(labels):
        assert result[i] == label


# ============================================================
# create_default_labels Properties
# ============================================================


@given(
    length=st.integers(min_value=0, max_value=100),
)
@settings(max_examples=50)
def test_create_default_labels_correct_length(length):
    """create_default_labels should return list of correct length."""
    result = create_default_labels(length)

    assert len(result) == length


@given(
    length=st.integers(min_value=1, max_value=20),
)
@settings(max_examples=50)
def test_create_default_labels_all_blanks(length):
    """create_default_labels should return list of blank strings."""
    result = create_default_labels(length)

    for label in result:
        assert label == " "


# ============================================================
# get_data_length Properties
# ============================================================


@given(
    data=st.lists(st.floats(), min_size=1, max_size=10),
)
@settings(max_examples=50)
def test_get_data_length_1d(data):
    """get_data_length should return length for 1D data."""
    result = get_data_length(data)

    assert result == len(data)


@given(
    data=st.lists(
        st.lists(st.floats(), min_size=1, max_size=5), min_size=1, max_size=3
    ),
)
@settings(max_examples=50)
def test_get_data_length_2d(data):
    """get_data_length should return first series length for 2D data."""
    result = get_data_length(data)

    assert result == len(data[0])


@given(
    data=st.none(),
)
@settings(max_examples=20)
def test_get_data_length_none_returns_zero(data):
    """get_data_length should return 0 for None."""
    result = get_data_length(data)

    assert result == 0


@given(
    data=st.just([]),
)
@settings(max_examples=20)
def test_get_data_length_empty_returns_zero(data):
    """get_data_length should return 0 for empty list."""
    result = get_data_length(data)

    assert result == 0
