"""Test LogScale ticks for sub-decade ranges."""

from charted.charts.scales import LogScale


def test_log_scale_sub_decade_range_28_55():
    """Test that sub-decade range 28-55 returns minor ticks (30, 40, 50)."""
    scale = LogScale(28, 55)
    ticks = scale.ticks()
    # Should return minor ticks at 30, 40, 50 (no power of 10 in range)
    assert ticks == [30, 40, 50]


def test_log_scale_sub_decade_range_386_705():
    """Test that sub-decade range 386-705 returns minor ticks (400, 500, 600, 700)."""
    scale = LogScale(386, 705)
    ticks = scale.ticks()
    # Should return minor ticks at 400, 500, 600, 700 (no power of 10 in range)
    assert ticks == [400, 500, 600, 700]


def test_log_scale_full_decade_range_returns_only_powers():
    """Test that full decade range returns ONLY powers of ten, no minor ticks."""
    scale = LogScale(1, 1000)
    ticks = scale.ticks()
    # Should return ONLY powers: [1, 10, 100, 1000], NOT minor ticks
    assert ticks == [1, 10, 100, 1000]
    assert len(ticks) == 4  # Critical: no minor ticks for full decades


def test_log_scale_full_decade_range_10_1000():
    """Test another full decade range."""
    scale = LogScale(10, 1000)
    ticks = scale.ticks()
    assert ticks == [10, 100, 1000]


def test_log_scale_single_point():
    """Test that single point falls back to bracketing decade."""
    scale = LogScale(50, 50)
    ticks = scale.ticks()
    # Should return bracketing decade: 10, 100
    assert ticks == [10, 100]


def test_log_scale_negative_exponents():
    """Test ranges with negative exponents (0 < x < 1)."""
    import pytest

    # Range that includes a power of ten (0.1 = 10^-1)
    scale_with_power = LogScale(0.1, 0.5)
    ticks_with_power = scale_with_power.ticks()
    # Contains 0.1 (power of 10), so returns only that power
    assert ticks_with_power == [0.1]

    # True sub-decade with negative exponents: no power of 10 in range
    scale_sub_decade = LogScale(0.15, 0.5)
    ticks_sub_decade = scale_sub_decade.ticks()
    # No power of 10 in [0.15, 0.5], returns minor ticks
    # Note: floating point precision may cause 0.3 to be 0.30000000000000004
    assert len(ticks_sub_decade) == 4  # 0.2, 0.3, 0.4, 0.5
    assert 0.2 in ticks_sub_decade
    assert pytest.approx(0.3) in ticks_sub_decade or any(
        abs(t - 0.3) < 1e-10 for t in ticks_sub_decade
    )
    assert 0.4 in ticks_sub_decade
    assert 0.5 in ticks_sub_decade


def test_log_scale_crosses_decade_boundary():
    """Test range that includes a power of ten (full-decade behavior)."""
    scale = LogScale(5, 50)
    ticks = scale.ticks()
    # Contains 10, so returns ONLY powers: [10]
    assert ticks == [10]


def test_log_scale_just_below_decade():
    """Test range just below a decade boundary."""
    scale = LogScale(2, 8)
    ticks = scale.ticks()
    # No power of 10 in [2, 8], returns minor ticks
    assert ticks == [2, 3, 4, 5, 6, 7, 8]
