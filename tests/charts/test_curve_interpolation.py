"""Anchor tests for line/area curve interpolation (feature-parity roadmap, feature 3).

Placeholders for charted/utils/curves.py and the curve= option, skipped so the
suite stays green. See docs/feature_parity_roadmap.md section 3.
"""

import pytest

pytestmark = pytest.mark.skip(reason="feature-parity roadmap, not yet implemented")


def test_linear_curve_is_default_polyline():
    """Default output uses straight L segments (pins current behavior)."""
    raise NotImplementedError


def test_step_curve_emits_horizontal_then_vertical():
    """curve='step' produces axis-aligned segments between points."""
    raise NotImplementedError


def test_cardinal_curve_emits_cubic_beziers():
    """curve='cardinal'/'basis' produces a path containing C commands."""
    raise NotImplementedError


def test_curve_passes_through_endpoints():
    """Curved path starts and ends at the first/last data points."""
    raise NotImplementedError


def test_area_curve_matches_line_curve():
    """AreaChart fills under the same smoothed boundary the line draws."""
    raise NotImplementedError


def test_invalid_curve_raises():
    """An unknown curve name raises ValueError."""
    raise NotImplementedError
