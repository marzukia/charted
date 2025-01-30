"""Extended tests for charted.utils.series_style module."""

import pytest

from charted.utils.series_style import SeriesStyle


class TestSeriesStyleMarkerMethods:
    """Test marker-related builder methods."""

    def test_marker_shape_method(self):
        """Test marker_shape() builder method."""
        style = SeriesStyle().with_marker_shape("square")
        assert style._marker_shape == "square"

    def test_marker_size_method(self):
        """Test marker_size() builder method."""
        style = SeriesStyle().with_marker_size(6.0)
        assert style._marker_size == 6.0

    def test_all_marker_methods_chain(self):
        """Test chaining all marker methods."""
        style = (
            SeriesStyle()
            .with_show_markers(True)
            .with_marker_shape("diamond")
            .with_marker_size(8.0)
        )
        assert style._show_markers is True
        assert style._marker_shape == "diamond"
        assert style._marker_size == 8.0


class TestSeriesStyleGetAttr:
    """Test __getattr__ backward compatibility."""

    def test_getattr_fill(self):
        """Test getattr maps to _fill."""
        style = SeriesStyle().with_fill("#abc")
        assert style.fill == "#abc"

    def test_getattr_stroke(self):
        """Test getattr maps to _stroke."""
        style = SeriesStyle().with_stroke("#def")
        assert style.stroke == "#def"

    def test_getattr_stroke_width(self):
        """Test getattr maps to _stroke_width."""
        style = SeriesStyle().with_stroke_width(3.0)
        assert style.stroke_width == 3.0

    def test_getattr_all_fields(self):
        """Test getattr for all mapped fields."""
        style = (
            SeriesStyle()
            .with_fill("#111")
            .with_stroke("#222")
            .with_stroke_width(1.5)
            .with_stroke_dasharray("3,3")
            .with_show_markers(True)
            .with_marker_shape("circle")
            .with_marker_size(4.0)
        )
        assert style.fill == "#111"
        assert style.stroke == "#222"
        assert style.stroke_width == 1.5
        assert style.stroke_dasharray == "3,3"
        assert style.show_markers is True
        assert style.marker_shape == "circle"
        assert style.marker_size == 4.0

    def test_getattr_private_raises(self):
        """Test that accessing non-existent private attributes raises AttributeError."""
        style = SeriesStyle()
        # Non-existent private attributes raise AttributeError via __getattr__
        with pytest.raises(AttributeError, match="_nonexistent"):
            _ = style._nonexistent

    def test_getattr_nonexistent_raises(self):
        """Test that nonexistent attributes raise AttributeError."""
        style = SeriesStyle()
        with pytest.raises(AttributeError, match="nonexistent"):
            _ = style.nonexistent


class TestSeriesStyleGet:
    """Test dict-style get() method."""

    def test_get_existing_key(self):
        """Test get() for existing key."""
        style = SeriesStyle().with_fill("#fff")
        assert style.get("fill") == "#fff"

    def test_get_nonexistent_key(self):
        """Test get() for nonexistent key returns default."""
        style = SeriesStyle()
        assert style.get("fill") is None

    def test_get_with_custom_default_none_value(self):
        """Test get() when value is None (returns None, not default)."""
        style = SeriesStyle()
        # When the field exists but is None, get() returns None
        assert style.get("fill", "#000") is None

    def test_get_all_fields(self):
        """Test get() for all fields."""
        style = (
            SeriesStyle()
            .with_fill("#123")
            .with_stroke_width(2.0)
            .with_marker_shape("square")
        )
        assert style.get("fill") == "#123"
        assert style.get("stroke_width") == 2.0
        assert style.get("marker_shape") == "square"
        assert style.get("nonexistent") is None


class TestSeriesStyleToDict:
    """Test to_dict() method."""

    def test_to_dict_empty(self):
        """Test to_dict() with empty style."""
        style = SeriesStyle()
        d = style.to_dict()
        assert d == {}

    def test_to_dict_single_field(self):
        """Test to_dict() with single field."""
        style = SeriesStyle().with_fill("#abc")
        d = style.to_dict()
        assert d == {"fill": "#abc"}

    def test_to_dict_multiple_fields(self):
        """Test to_dict() with multiple fields."""
        style = SeriesStyle().with_fill("#111").with_stroke_width(2.5)
        d = style.to_dict()
        assert d == {"fill": "#111", "stroke_width": 2.5}

    def test_to_dict_all_fields(self):
        """Test to_dict() with all fields set."""
        style = (
            SeriesStyle()
            .with_fill("#fff")
            .with_stroke("#000")
            .with_stroke_width(3.0)
            .with_stroke_dasharray("5,5")
            .with_show_markers(True)
            .with_marker_shape("diamond")
            .with_marker_size(6.0)
        )
        d = style.to_dict()
        assert d == {
            "fill": "#fff",
            "stroke": "#000",
            "stroke_width": 3.0,
            "stroke_dasharray": "5,5",
            "show_markers": True,
            "marker_shape": "diamond",
            "marker_size": 6.0,
        }

    def test_to_dict_excludes_none(self):
        """Test to_dict() excludes None values."""
        style = SeriesStyle().with_fill("#fff")
        d = style.to_dict()
        # Should only have fill, not other fields
        assert "fill" in d
        assert "stroke" not in d
        assert "stroke_width" not in d


class TestSeriesStyleImmutability:
    """Test SeriesStyle immutability properties."""

    def test_replace_creates_new_instance(self):
        """Test that builder methods create new instances."""
        style1 = SeriesStyle()
        style2 = style1.with_fill("#fff")
        assert style1 is not style2
        assert style1._fill is None
        assert style2._fill == "#fff"

    def test_multiple_replaces(self):
        """Test chaining multiple replaces."""
        style1 = SeriesStyle()
        style2 = style1.with_fill("#fff")
        style3 = style2.with_stroke("#000")
        assert style1._fill is None
        assert style2._fill == "#fff"
        assert style2._stroke is None
        assert style3._fill == "#fff"
        assert style3._stroke == "#000"


class TestSeriesStyleEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_marker_shape_variants(self):
        """Test different marker shape values."""
        for shape in ["circle", "square", "diamond", "none", "triangle"]:
            style = SeriesStyle().with_marker_shape(shape)
            assert style._marker_shape == shape

    def test_marker_size_variants(self):
        """Test different marker size values."""
        for size in [0.5, 1.0, 2.5, 10.0, 100.0]:
            style = SeriesStyle().with_marker_size(size)
            assert style._marker_size == size

    def test_stroke_width_zero(self):
        """Test stroke width of zero."""
        style = SeriesStyle().with_stroke_width(0)
        assert style._stroke_width == 0

    def test_stroke_width_very_large(self):
        """Test very large stroke width."""
        style = SeriesStyle().with_stroke_width(1000.0)
        assert style._stroke_width == 1000.0

    def test_empty_dasharray(self):
        """Test empty dash array string."""
        style = SeriesStyle().with_stroke_dasharray("")
        assert style._stroke_dasharray == ""

    def test_complex_dasharray(self):
        """Test complex dash array pattern."""
        style = SeriesStyle().with_stroke_dasharray("5,3,1,3")
        assert style._stroke_dasharray == "5,3,1,3"


class TestSeriesStyleIntegration:
    """Test SeriesStyle integration scenarios."""

    def test_style_for_line_chart(self):
        """Test style configuration for line chart."""
        style = (
            SeriesStyle()
            .with_stroke("#ff0000")
            .with_stroke_width(2.0)
            .with_show_markers(True)
            .with_marker_shape("circle")
            .with_marker_size(4.0)
        )
        assert style.stroke == "#ff0000"
        assert style.stroke_width == 2.0
        assert style.show_markers is True

    def test_style_for_bar_chart(self):
        """Test style configuration for bar chart."""
        style = (
            SeriesStyle()
            .with_fill("#00ff00")
            .with_stroke("#00cc00")
            .with_stroke_width(1.0)
        )
        assert style.fill == "#00ff00"
        assert style.stroke == "#00cc00"

    def test_style_for_area_chart(self):
        """Test style configuration for area chart."""
        style = (
            SeriesStyle()
            .with_fill("#0000ff")
            .with_stroke_dasharray("2,2")
            .with_show_markers(False)
        )
        assert style.fill == "#0000ff"
        assert style.stroke_dasharray == "2,2"
        assert style.show_markers is False
