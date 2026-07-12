"""Test LogScale ticks for sub-decade ranges."""

from charted.charts.scales import LogScale


def test_log_scale_sub_decade_range_28_55():
    """Test that sub-decade range 28-55 returns minor ticks (30, 40, 50)."""
    scale = LogScale(28, 55)
    ticks = scale.ticks()
    # Should return minor ticks at 30, 40, 50
    assert 30 in ticks
    assert 40 in ticks
    assert 50 in ticks
    # Should not fall back to just endpoints
    assert len(ticks) >= 3


def test_log_scale_sub_decade_range_386_705():
    """Test that sub-decade range 386-705 returns minor ticks (400, 500, 600, 700)."""
    scale = LogScale(386, 705)
    ticks = scale.ticks()
    # Should return minor ticks at 400, 500, 600, 700
    assert 400 in ticks
    assert 500 in ticks
    assert 600 in ticks
    assert 700 in ticks
    # Should not fall back to just endpoints
    assert len(ticks) >= 4


def test_log_scale_full_decade_range():
    """Test that full decade range still returns powers of ten."""
    scale = LogScale(10, 1000)
    ticks = scale.ticks()
    # Should return powers of ten: 10, 100, 1000
    assert 10 in ticks
    assert 100 in ticks
    assert 1000 in ticks


def test_log_scale_single_point():
    """Test that single point falls back to bracketing decade."""
    scale = LogScale(50, 50)
    ticks = scale.ticks()
    # Should return bracketing decade: 10, 100
    assert len(ticks) == 2
    assert min(ticks) == 10
    assert max(ticks) == 100
