"""Anchor tests for log and time scales (feature-parity roadmap, feature 1).

These are placeholders for the not-yet-implemented scale abstraction
(charted/charts/scales.py). They are skipped so the suite stays green; remove
the skip mark and flesh out the assertions when implementing the feature.

See docs/feature_parity_roadmap.md section 1.
"""

import pytest

pytestmark = pytest.mark.skip(reason="feature-parity roadmap, not yet implemented")


def test_linear_scale_matches_current_reproject():
    """LinearScale(0, 100) over length 400 maps 50 -> 200.0 (pins current math)."""
    raise NotImplementedError


def test_log_scale_maps_decades():
    """LogScale(1, 1000) over length 300 spaces decades evenly (0,100,200,300)."""
    raise NotImplementedError


def test_log_scale_rejects_nonpositive():
    """LogScale with min <= 0 or non-positive data raises ValueError."""
    raise NotImplementedError


def test_log_scale_ticks_are_powers():
    """Ticks for [1, 1000] are [1, 10, 100, 1000]."""
    raise NotImplementedError


def test_time_scale_maps_dates():
    """TimeScale maps the midpoint date of a span to ~length/2."""
    raise NotImplementedError


def test_time_scale_nice_ticks():
    """A one-year span produces clean month/quarter boundary ticks."""
    raise NotImplementedError
