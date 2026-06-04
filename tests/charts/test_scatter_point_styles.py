"""Tests for per-point marker styling and the themed data-label colour."""

from charted.charts.scatter import ScatterChart
from charted.themes.core import Theme


class TestPerPointStyles:
    """Per-point marker overrides via ``point_styles``."""

    def test_point_styles_default_is_backward_compatible(self):
        """Without point_styles, output is identical to before the feature."""
        a = ScatterChart(x_data=[0, 1, 2], y_data=[10, 20, 30]).html
        b = ScatterChart(
            x_data=[0, 1, 2], y_data=[10, 20, 30], point_styles=None
        ).html
        assert a == b

    def test_point_style_overrides_shape(self):
        """A per-point marker_shape replaces only that point's marker."""
        chart = ScatterChart(
            x_data=[0, 1, 2],
            y_data=[10, 20, 30],
            point_styles=[[None, {"marker_shape": "square"}, None]],
        )
        html = chart.html
        # The styled point becomes a <rect>; the other two stay circles.
        assert "<rect" in html.lower()
        assert html.lower().count("<circle") == 2

    def test_point_style_overrides_fill_and_opacity(self):
        """Per-point fill and opacity land on the marker element."""
        chart = ScatterChart(
            x_data=[0, 1],
            y_data=[5, 9],
            point_styles=[[{"fill": "#ff0000", "opacity": 0.3}, None]],
        )
        html = chart.html
        assert "#ff0000" in html
        assert "0.3" in html

    def test_point_style_wins_over_series_style(self):
        """A per-point shape beats the per-series marker_shape."""
        chart = ScatterChart(
            x_data=[0, 1],
            y_data=[5, 9],
            series_styles=[{"marker_shape": "square"}],
            point_styles=[[{"marker_shape": "circle"}, None]],
        )
        html = chart.html
        # One point reverts to a circle, the other stays a square rect.
        assert "<circle" in html.lower()
        assert "<rect" in html.lower()

    def test_ragged_point_styles_are_safe(self):
        """Short/empty point-style rows do not raise and leave points default."""
        chart = ScatterChart(
            x_data=[0, 1, 2],
            y_data=[10, 20, 30],
            point_styles=[[{"marker_shape": "square"}]],  # only first point
        )
        html = chart.html
        assert "<rect" in html.lower()
        assert html.lower().count("<circle") == 2


class TestThemedDataLabelColor:
    """The new ``data_label_color`` theme token."""

    def test_default_data_label_color_matches_axis_title(self):
        """Unset token defers to the axis-title tier (backward compatible)."""
        theme = Theme()
        assert theme.resolved_data_label_color == theme.resolved_axis_title_color

    def test_data_label_color_override_applied(self):
        """An explicit token colour is honoured and reaches the SVG labels."""
        theme = Theme(data_label_color="#123456")
        assert theme.resolved_data_label_color == "#123456"
        chart = ScatterChart(
            x_data=[0, 1],
            y_data=[10, 20],
            data_labels=["a", "b"],
            theme=theme,
        )
        assert "#123456" in chart.html

    def test_data_labels_default_color_unchanged(self):
        """Default theme data labels still render in the axis-title colour."""
        theme = Theme()
        chart = ScatterChart(
            x_data=[0, 1],
            y_data=[10, 20],
            data_labels=["a", "b"],
            theme=theme,
        )
        assert theme.resolved_axis_title_color in chart.html

    def test_invalid_data_label_color_rejected(self):
        """A malformed token colour fails validation."""
        import pytest

        with pytest.raises(ValueError):
            Theme(data_label_color="not-a-color")
