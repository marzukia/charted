"""Tests for charted.utils.exceptions module.

Covers all custom exception classes with agent-friendly messages.
"""

import pytest

from charted.utils.exceptions import (
    ChartedError,
    DataShapeError,
    InvalidValue,
    LabelMismatchError,
    NoDataError,
    PaletteError,
    ThemeError,
    UnknownChartTypeError,
)


class TestChartedError:
    """Test base exception class."""

    def test_is_exception(self):
        """ChartedError inherits from Exception."""
        assert issubclass(ChartedError, Exception)

    def test_can_raise(self):
        """ChartedError can be raised and caught."""
        with pytest.raises(ChartedError):
            raise ChartedError("base error")


class TestInvalidValue:
    """Test InvalidValue exception."""

    def test_message_format(self):
        """Message includes name and value."""
        exc = InvalidValue(name="h_padding", value=1.5)
        msg = str(exc)
        assert "h_padding" in msg
        assert "1.5" in msg

    def test_attributes(self):
        """Exception stores name and value attributes."""
        exc = InvalidValue(name="v_padding", value=2.0)
        assert exc.name == "v_padding"
        assert exc.value == 2.0

    def test_inheritance(self):
        """InvalidValue inherits from ChartedError."""
        assert issubclass(InvalidValue, ChartedError)


class TestNoDataError:
    """Test NoDataError exception."""

    def test_message_includes_guidance(self):
        """Message tells user what to fix."""
        exc = NoDataError()
        msg = str(exc)
        assert "No data" in msg
        assert "data" in msg
        assert "BarChart" in msg

    def test_inheritance(self):
        """NoDataError inherits from ChartedError."""
        assert issubclass(NoDataError, ChartedError)


class TestDataShapeError:
    """Test DataShapeError exception."""

    def test_message_without_detail(self):
        """Message includes expected and actual shapes."""
        exc = DataShapeError(expected="1D list", actual="2D list")
        msg = str(exc)
        assert "1D list" in msg
        assert "2D list" in msg
        assert "reshaping" in msg.lower() or "Try reshaping" in msg

    def test_message_with_detail(self):
        """Message includes detail when provided."""
        exc = DataShapeError(
            expected="1D list", actual="2D list", detail="Too many dimensions."
        )
        msg = str(exc)
        assert "Too many dimensions." in msg

    def test_attributes(self):
        """Exception stores expected, actual, detail."""
        exc = DataShapeError(expected="flat", actual="nested", detail="detail")
        assert exc.expected == "flat"
        assert exc.actual == "nested"
        assert exc.detail == "detail"

    def test_inheritance(self):
        """DataShapeError inherits from ChartedError."""
        assert issubclass(DataShapeError, ChartedError)


class TestLabelMismatchError:
    """Test LabelMismatchError exception."""

    def test_message_includes_counts(self):
        """Message includes label and data counts."""
        exc = LabelMismatchError(n_labels=3, n_data=5, axis="x")
        msg = str(exc)
        assert "3" in msg
        assert "5" in msg
        assert "x-labels" in msg

    def test_default_axis(self):
        """Axis defaults to 'x'."""
        exc = LabelMismatchError(n_labels=2, n_data=4)
        msg = str(exc)
        assert "x-labels" in msg

    def test_custom_axis(self):
        """Custom axis appears in message."""
        exc = LabelMismatchError(n_labels=2, n_data=4, axis="y")
        msg = str(exc)
        assert "y-labels" in msg

    def test_attributes(self):
        """Exception stores n_labels, n_data, axis."""
        exc = LabelMismatchError(n_labels=3, n_data=5, axis="x")
        assert exc.n_labels == 3
        assert exc.n_data == 5
        assert exc.axis == "x"

    def test_inheritance(self):
        """LabelMismatchError inherits from ChartedError."""
        assert issubclass(LabelMismatchError, ChartedError)


class TestThemeError:
    """Test ThemeError exception."""

    def test_message_includes_guidance(self):
        """Message includes Theme usage guidance."""
        exc = ThemeError("invalid color")
        msg = str(exc)
        assert "invalid color" in msg
        assert "from_preset" in msg

    def test_inheritance(self):
        """ThemeError inherits from ChartedError."""
        assert issubclass(ThemeError, ChartedError)


class TestPaletteError:
    """Test PaletteError exception."""

    def test_message_includes_available(self):
        """Message lists available palettes."""
        exc = PaletteError(name="nonexistent")
        msg = str(exc)
        assert "nonexistent" in msg
        assert "viridis" in msg
        assert "Available" in msg

    def test_inheritance(self):
        """PaletteError inherits from ChartedError."""
        assert issubclass(PaletteError, ChartedError)


class TestUnknownChartTypeError:
    """Test UnknownChartTypeError exception."""

    def test_message_includes_available_types(self):
        """Message lists available chart types."""
        exc = UnknownChartTypeError(chart_type="foo")
        msg = str(exc)
        assert "foo" in msg
        assert "BarChart" in msg
        assert "Available types" in msg

    def test_inheritance(self):
        """UnknownChartTypeError inherits from ChartedError."""
        assert issubclass(UnknownChartTypeError, ChartedError)
