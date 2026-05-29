"""Anchor tests for the polar area chart (feature-parity roadmap, feature 4).

Placeholders for charted/charts/polar_area.py (PolarAreaChart), skipped so the
suite stays green. See docs/feature_parity_roadmap.md section 4.
"""

import pytest

pytestmark = pytest.mark.skip(reason="feature-parity roadmap, not yet implemented")


def test_polar_area_equal_angles():
    """N values produce N slices each spanning 360/N degrees."""
    raise NotImplementedError


def test_polar_area_radius_encodes_value():
    """Slice radius is monotonic in value (largest value -> outermost slice)."""
    raise NotImplementedError


def test_polar_area_rejects_negative_values():
    """Negative values raise ValueError."""
    raise NotImplementedError
