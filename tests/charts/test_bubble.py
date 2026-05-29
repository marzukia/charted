"""Anchor tests for the bubble chart (feature-parity roadmap, feature 4).

Placeholders for charted/charts/bubble.py (BubbleChart), skipped so the suite
stays green. See docs/feature_parity_roadmap.md section 4.
"""

import pytest

pytestmark = pytest.mark.skip(reason="feature-parity roadmap, not yet implemented")


def test_bubble_radius_encodes_third_dim():
    """Circle r is monotonic in the size value (largest size -> largest radius)."""
    raise NotImplementedError


def test_bubble_radius_within_bounds():
    """All radii fall within the configured [min_radius, max_radius] range."""
    raise NotImplementedError


def test_bubble_reuses_scatter_positioning():
    """Point centers match an equivalent ScatterChart."""
    raise NotImplementedError


def test_bubble_rejects_negative_sizes():
    """Negative sizes raise ValueError."""
    raise NotImplementedError
