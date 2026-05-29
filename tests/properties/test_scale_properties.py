"""Property-based tests for the Scale abstraction using hypothesis."""

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from charted.charts.scales import LogScale

positive_floats = st.floats(
    min_value=1e-6, max_value=1e9, allow_nan=False, allow_infinity=False
)


@given(
    a=positive_floats,
    b=positive_floats,
    length=st.floats(min_value=1.0, max_value=2000.0),
    t=st.floats(min_value=0.0, max_value=1.0),
)
@settings(max_examples=200)
def test_log_scale_reproject_within_bounds(a, b, length, t):
    """LogScale.reproject stays within [0, length] for any in-range value."""
    lo, hi = min(a, b), max(a, b)
    assume(hi > lo * 1.0001)
    scale = LogScale(lo, hi)
    # Pick a value inside [lo, hi] via log-space interpolation.
    import math

    log_val = math.log10(lo) + t * (math.log10(hi) - math.log10(lo))
    value = 10**log_val
    value = min(max(value, lo), hi)
    px = scale.reproject(value, length)
    assert -1e-6 <= px <= length + 1e-6


@given(
    a=positive_floats,
    b=positive_floats,
    length=st.floats(min_value=1.0, max_value=2000.0),
)
@settings(max_examples=200)
def test_log_scale_monotonic(a, b, length):
    """LogScale.reproject is monotonically increasing in the value."""
    lo, hi = min(a, b), max(a, b)
    assume(hi > lo * 1.01)
    scale = LogScale(lo, hi)
    import math

    points = []
    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        log_val = math.log10(lo) + frac * (math.log10(hi) - math.log10(lo))
        points.append(scale.reproject(10**log_val, length))
    for earlier, later in zip(points, points[1:]):
        assert later >= earlier - 1e-6
