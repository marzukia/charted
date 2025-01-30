"""Tests for charted.utils.series_style module."""

import pytest

from charted.utils.series_style import SeriesStyle


class TestSeriesStyleBuilder:
    """Test SeriesStyle builder methods."""

    def test_default_style(self):
        """Test default style values."""
        style = SeriesStyle()
        assert style._fill is None
        assert style._stroke is None
        assert style._stroke_width is None
        assert style._stroke_dasharray is None
        assert style._show_markers is None

    def test_fill_method(self):
        """Test fill() builder method."""
        style = SeriesStyle().with_fill("#ff0000")
        assert style._fill == "#ff0000"

    def test_stroke_method(self):
        """Test stroke() builder method."""
        style = SeriesStyle().with_stroke("#00ff00")
        assert style._stroke == "#00ff00"

    def test_stroke_width_method(self):
        """Test stroke_width() builder method."""
        style = SeriesStyle().with_stroke_width(2.5)
        assert style._stroke_width == 2.5

    def test_stroke_dasharray_method(self):
        """Test stroke_dasharray() builder method."""
        style = SeriesStyle().with_stroke_dasharray("5,5")
        assert style._stroke_dasharray == "5,5"

    def test_show_markers_method(self):
        """Test show_markers() builder method."""
        style = SeriesStyle().with_show_markers(False)
        assert style._show_markers is False

    def test_chain_methods(self):
        """Test method chaining."""
        style = (
            SeriesStyle()
            .with_fill("#ff0000")
            .with_stroke("#000000")
            .with_stroke_width(2)
            .with_stroke_dasharray("5,5")
            .with_show_markers(False)
        )
        assert style._fill == "#ff0000"
        assert style._stroke == "#000000"
        assert style._stroke_width == 2
        assert style._stroke_dasharray == "5,5"
        assert style._show_markers is False


class TestSeriesStyleImmutability:
    """Test SeriesStyle immutability."""

    def test_cannot_modify_frozen(self):
        """Test frozen dataclass cannot be modified."""
        style = SeriesStyle()
        with pytest.raises(Exception):
            style._fill = "#fff"


class TestSeriesStyleDictAccess:
    """Test backward-compatible dict-style access."""

    def test_getattr_access(self):
        """Test attribute access maps to internal fields."""
        style = SeriesStyle().with_fill("#f00")
        assert style.fill == "#f00"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        style = SeriesStyle().with_fill("#f00").with_stroke_width(2)
        d = style.to_dict()
        assert d["fill"] == "#f00"
        assert d["stroke_width"] == 2
