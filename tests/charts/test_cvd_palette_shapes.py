"""Tests for the colourblind-safe palette and redundant shape encoding."""

from charted.charts.scatter import ScatterChart
from charted.themes.core import NAMED_PALETTES, Theme, resolve_palette


class TestOkabeItoPalette:
    """The Okabe-Ito colourblind-safe palette and high-contrast preset."""

    def test_okabe_ito_registered(self):
        assert "okabe-ito" in NAMED_PALETTES
        palette = resolve_palette("okabe-ito")
        assert len(palette) == 8
        assert palette[0] == "#e69f00"

    def test_high_contrast_uses_okabe_ito(self):
        theme = Theme.from_preset("high-contrast")
        assert theme.colors == NAMED_PALETTES["okabe-ito"]


class TestShapeCycle:
    """Redundant shape encoding for multi-series scatter plots."""

    def _two_series(self, **kwargs):
        return ScatterChart(
            x_data=[[0, 1], [0, 1]],
            y_data=[[10, 20], [15, 25]],
            **kwargs,
        )

    def test_default_all_circles(self):
        """Without shape_cycle, every series renders circles (unchanged)."""
        markers = str(self._two_series().representation).lower()
        assert "<circle" in markers
        assert "<rect" not in markers

    def test_shape_cycle_true_differs_by_shape(self):
        """shape_cycle=True gives series 0 a circle and series 1 a square."""
        markers = str(self._two_series(shape_cycle=True).representation).lower()
        assert "<circle" in markers
        assert "<rect" in markers

    def test_custom_shape_cycle(self):
        """A custom cycle list is honoured."""
        markers = str(
            self._two_series(shape_cycle=["square", "triangle"]).representation
        ).lower()
        assert "<rect" in markers
        assert "<path" in markers
        assert "<circle" not in markers

    def test_series_styles_override_cycle(self):
        """An explicit per-series marker_shape wins over the cycle."""
        chart = ScatterChart(
            x_data=[[0, 1], [0, 1]],
            y_data=[[10, 20], [15, 25]],
            shape_cycle=True,
            series_styles=[{"marker_shape": "circle"}, {"marker_shape": "circle"}],
        )
        markers = str(chart.representation).lower()
        assert "<circle" in markers
        assert "<rect" not in markers
