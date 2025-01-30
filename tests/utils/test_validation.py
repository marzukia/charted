"""Tests for charted.utils.validation."""

from charted.utils.validation import (
    create_default_labels,
    get_data_length,
    validate_attribute_value,
    validate_data,
    validate_padding,
    validate_series_count,
)


class TestValidationFunctions:
    """Test validation utility functions."""

    def test_validate_data(self):
        """Test data validation."""
        data = [[1, 2, 3], [4, 5, 6]]
        result = validate_data(data)
        assert len(result) == 2

    def test_validate_attribute_value(self):
        """Test attribute value validation."""
        # Note: validate_attribute_value returns the input value
        assert validate_attribute_value("x", 10.5) == 10.5

    def test_validate_padding(self):
        """Test padding validation."""
        assert validate_padding(0.1) == 0.1
        assert validate_padding(0.5) == 0.5

    def test_validate_series_count(self):
        """Test series count validation."""
        styles = [{"fill": "#ff0000"}, {"fill": "#00ff00"}]
        assert validate_series_count(styles, 2) == 2

    def test_create_default_labels(self):
        """Test default label creation."""
        labels = create_default_labels(5)
        assert len(labels) == 5
        # Default labels are spaces for spacing purposes
        assert labels == [" ", " ", " ", " ", " "]

    def test_get_data_length(self):
        """Test data length extraction."""
        data = [[1, 2, 3], [4, 5, 6]]
        assert get_data_length(data) == 3
