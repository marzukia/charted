"""Anchor tests for continuous color interpolation (feature-parity roadmap, feature 7).

Placeholders for interpolate_color / interpolate_palette and diverging scales,
skipped so the suite stays green. See docs/feature_parity_roadmap.md section 7.
"""

import pytest

pytestmark = pytest.mark.skip(reason="feature-parity roadmap, not yet implemented")


def test_interpolate_sequential_endpoints():
    """interpolate('viridis', 0.0)/1.0 equal the palette's first/last colors."""
    raise NotImplementedError


def test_interpolate_midpoint_between_stops():
    """interpolate(['#000000','#ffffff'], 0.5) returns mid-gray within tolerance."""
    raise NotImplementedError


def test_diverging_scale_center():
    """A diverging scale returns mid at center and endpoints at the extremes."""
    raise NotImplementedError


def test_interpolate_clamps_out_of_range():
    """t < 0 clamps to the first color, t > 1 to the last."""
    raise NotImplementedError
