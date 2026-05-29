"""Tests for continuous sequential/diverging color interpolation."""

from charted.themes.core import NAMED_PALETTES, ColorScale, diverging_scale
from charted.utils.colors import (
    _parse_color_to_rgb,
    hex_to_rgb,
    interpolate_color,
    interpolate_palette,
)


def _close(a, b, tol=4):
    """Channel-wise closeness for two hex colors."""
    ra, ga, ba = hex_to_rgb(a)
    rb, gb, bb = hex_to_rgb(b)
    return abs(ra - rb) <= tol and abs(ga - gb) <= tol and abs(ba - bb) <= tol


class TestInterpolatePalette:
    def test_interpolate_sequential_endpoints(self):
        """t=0.0 yields first palette color, t=1.0 yields last."""
        viridis = NAMED_PALETTES["viridis"]
        assert _close(interpolate_palette("viridis", 0.0), viridis[0])
        assert _close(interpolate_palette("viridis", 1.0), viridis[-1])

    def test_interpolate_midpoint_between_stops(self):
        """Midpoint of black->white is roughly mid-gray."""
        result = interpolate_palette(["#000000", "#ffffff"], 0.5)
        assert _close(result, "#7f7f7f", tol=2)

    def test_interpolate_clamps_out_of_range(self):
        """t<0 clamps to first color, t>1 clamps to last."""
        palette = ["#000000", "#ffffff"]
        assert _close(interpolate_palette(palette, -0.5), "#000000")
        assert _close(interpolate_palette(palette, 1.5), "#ffffff")

    def test_interpolate_color_endpoints(self):
        """interpolate_color returns endpoints at t=0 and t=1."""
        assert _close(interpolate_color("#000000", "#ffffff", 0.0), "#000000")
        assert _close(interpolate_color("#000000", "#ffffff", 1.0), "#ffffff")
        assert _close(interpolate_color("#000000", "#ffffff", 0.5), "#7f7f7f", tol=2)


class TestDivergingScale:
    def test_diverging_scale_center(self):
        """Diverging scale returns mid at domain center, endpoints at extremes."""
        scale = diverging_scale("#0000ff", "#ffffff", "#ff0000", domain=(-1.0, 1.0))
        assert _close(scale(-1.0), "#0000ff")
        assert _close(scale(0.0), "#ffffff")
        assert _close(scale(1.0), "#ff0000")

    def test_diverging_scale_default_domain(self):
        """Default domain (0,1) centers at 0.5."""
        scale = diverging_scale("#000000", "#808080", "#ffffff")
        assert _close(scale(0.0), "#000000")
        assert _close(scale(0.5), "#808080", tol=2)
        assert _close(scale(1.0), "#ffffff")

    def test_diverging_scale_clamps(self):
        """Out of domain clamps to endpoints."""
        scale = diverging_scale("#0000ff", "#ffffff", "#ff0000", domain=(-1.0, 1.0))
        assert _close(scale(-5.0), "#0000ff")
        assert _close(scale(5.0), "#ff0000")


class TestColorScale:
    def test_color_scale_maps_domain(self):
        """ColorScale maps a domain value to an interpolated palette color."""
        scale = ColorScale("viridis", domain=(0.0, 100.0))
        assert _close(scale(0.0), NAMED_PALETTES["viridis"][0])
        assert _close(scale(100.0), NAMED_PALETTES["viridis"][-1])

    def test_color_scale_clamps(self):
        scale = ColorScale(["#000000", "#ffffff"], domain=(0.0, 10.0))
        assert _close(scale(-1.0), "#000000")
        assert _close(scale(20.0), "#ffffff")

    def test_color_scale_output_parseable(self):
        scale = ColorScale("inferno", domain=(0.0, 1.0))
        for v in (0.0, 0.25, 0.5, 0.75, 1.0):
            _parse_color_to_rgb(scale(v))
