from charted.utils.exceptions import (
    InvalidValue,
    NoDataError,
    VectorLengthMismatchError,
)


class TestInvalidValue:
    """Tests for InvalidValue exception."""

    def test_invalid_value_basic(self):
        """Test basic InvalidValue exception creation."""
        exception = InvalidValue("age", -1)
        assert exception.name == "age"
        assert exception.value == -1
        assert "age" in str(exception)
        assert "-1" in str(exception)

    def test_invalid_value_string_value(self):
        """Test InvalidValue with string value."""
        exception = InvalidValue("username", "")
        assert exception.name == "username"
        assert exception.value == ""

    def test_invalid_value_exception_message(self):
        """Test that InvalidValue has a proper error message."""
        exception = InvalidValue("temperature", 200)
        expected_msg = "'200' is not a valid value for 'temperature'"
        assert str(exception) == expected_msg

    def test_invalid_value_inherits_from_exception(self):
        """Test that InvalidValue inherits from Exception."""
        exception = InvalidValue("test", "value")
        assert isinstance(exception, Exception)


class TestNoDataError:
    """Tests for NoDataError exception."""

    def test_no_data_error_basic(self):
        """Test basic NoDataError creation."""
        exception = NoDataError()
        assert isinstance(exception, NoDataError)
        assert isinstance(exception, Exception)

    def test_no_data_error_with_message(self):
        """Test NoDataError with custom message."""
        message = "No data available for chart"
        exception = NoDataError(message)
        assert isinstance(exception, NoDataError)
        assert str(exception) == message

    def test_no_data_error_inherits_from_chart_error(self):
        """Test that NoDataError inherits from ChartError."""
        from charted.utils.exceptions import ChartError

        exception = NoDataError()
        assert isinstance(exception, ChartError)


class TestVectorLengthMismatchError:
    """Tests for VectorLengthMismatchError exception."""

    def test_vector_length_mismatch_basic(self):
        """Test basic VectorLengthMismatchError creation."""
        exception = VectorLengthMismatchError()
        assert isinstance(exception, VectorLengthMismatchError)
        assert isinstance(exception, Exception)

    def test_vector_length_mismatch_with_message(self):
        """Test VectorLengthMismatchError with custom message."""
        message = "Vectors have different lengths"
        exception = VectorLengthMismatchError(message)
        assert isinstance(exception, VectorLengthMismatchError)
        assert str(exception) == message
