"""Unit tests for the Scale abstraction (linear, log, time)."""

from datetime import date, datetime, timezone

import pytest

from charted.charts.scales import LinearScale, LogScale, Scale, TimeScale


class TestLinearScale:
    def test_linear_scale_matches_current_reproject(self):
        """LinearScale(0, 100) over length 400 maps 50 -> 200.0."""
        scale = LinearScale(0, 100)
        assert scale.reproject(50, 400) == 200.0

    def test_linear_scale_reverse_round_trips(self):
        scale = LinearScale(0, 100)
        pixel = scale.reproject(37, 400)
        assert scale.reverse(pixel, 400) == pytest.approx(37)

    def test_linear_scale_is_a_scale(self):
        assert isinstance(LinearScale(0, 1), Scale)


class TestLogScale:
    def test_log_scale_maps_decades(self):
        """LogScale(1, 1000) over 300 places 1/10/100/1000 at 0/100/200/300."""
        scale = LogScale(1, 1000)
        assert scale.reproject(1, 300) == pytest.approx(0)
        assert scale.reproject(10, 300) == pytest.approx(100)
        assert scale.reproject(100, 300) == pytest.approx(200)
        assert scale.reproject(1000, 300) == pytest.approx(300)

    def test_log_scale_rejects_nonpositive_bounds(self):
        with pytest.raises(ValueError):
            LogScale(0, 1000)
        with pytest.raises(ValueError):
            LogScale(-5, 1000)

    def test_log_scale_rejects_nonpositive_data(self):
        scale = LogScale(1, 1000)
        with pytest.raises(ValueError):
            scale.reproject(0, 300)
        with pytest.raises(ValueError):
            scale.reproject(-10, 300)

    def test_log_scale_ticks_are_powers(self):
        scale = LogScale(1, 1000)
        assert scale.ticks() == [1, 10, 100, 1000]

    def test_log_scale_reverse_round_trips(self):
        scale = LogScale(1, 1000)
        pixel = scale.reproject(50, 300)
        assert scale.reverse(pixel, 300) == pytest.approx(50)


class TestTimeScale:
    def test_time_scale_maps_dates(self):
        """Midpoint of a year maps to ~length/2."""
        scale = TimeScale(date(2024, 1, 1), date(2024, 12, 31))
        midpoint = date(2024, 7, 1)
        pixel = scale.reproject(midpoint, 400)
        assert pixel == pytest.approx(200, abs=5)

    def test_time_scale_accepts_datetime(self):
        scale = TimeScale(datetime(2024, 1, 1), datetime(2024, 12, 31))
        pixel = scale.reproject(datetime(2024, 1, 1), 400)
        assert pixel == pytest.approx(0)

    def test_time_scale_accepts_iso_strings(self):
        scale = TimeScale("2024-01-01", "2024-12-31")
        pixel = scale.reproject("2024-12-31", 400)
        assert pixel == pytest.approx(400)

    def test_time_scale_rejects_bad_string(self):
        with pytest.raises(ValueError):
            TimeScale("not-a-date", "2024-12-31")

    def test_time_scale_nice_ticks(self):
        """A one-year span produces month/quarter boundary ticks."""
        scale = TimeScale(date(2024, 1, 1), date(2024, 12, 31))
        ticks = scale.ticks()
        assert len(ticks) >= 4
        # Every tick should fall on the 1st of a month (a clean boundary).
        for t in ticks:
            dt = datetime.fromtimestamp(t, tz=timezone.utc)
            assert dt.day == 1

    def test_time_scale_tick_pixels_are_tz_independent(self):
        """Concrete tick pixel positions are pinned and TZ-independent.

        These are absolute pixel values (not epoch-relative ratios), so they
        can only pass if the epoch and tick math are done in UTC. A naive
        local-time implementation shifts these by the host's UTC offset.
        """
        scale = TimeScale(date(2024, 1, 1), date(2024, 12, 31))
        # 2024-01-01 is the domain min: pixel 0 regardless of TZ.
        assert scale.reproject(date(2024, 1, 1), 366) == pytest.approx(0.0)
        # 2024-12-31 is the domain max: full length.
        assert scale.reproject(date(2024, 12, 31), 366) == pytest.approx(366.0)
        # 2024-07-01 (day 182 of 365 in the span) lands at a fixed offset.
        # span = 365 days, 2024-07-01 is 182 days in -> 182/365 * 366 = 182.5.
        assert scale.reproject(date(2024, 7, 1), 366) == pytest.approx(182.5, abs=0.1)
        # The first month-boundary tick (2024-02-01) sits at a fixed pixel.
        # 31 days in -> 31/365 * 366 = 31.08.
        feb1 = TimeScale._utc_epoch(2024, 2, 1)
        assert scale.reproject(feb1, 366) == pytest.approx(31.08, abs=0.1)

    def test_time_scale_aware_datetime_is_absolute(self):
        """A tz-aware datetime maps by its absolute UTC instant."""
        from datetime import timedelta

        scale = TimeScale("2024-01-01T00:00:00+00:00", "2024-01-02T00:00:00+00:00")
        # 12:00 UTC is the midpoint.
        noon_utc = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
        assert scale.reproject(noon_utc, 100) == pytest.approx(50.0)
        # The same instant expressed in +12:00 (midnight next day local) is
        # still 12:00 UTC, so it maps to the same pixel.
        same_instant = datetime(2024, 1, 2, 0, 0, tzinfo=timezone(timedelta(hours=12)))
        assert scale.reproject(same_instant, 100) == pytest.approx(50.0)

    def test_time_scale_tick_labels_are_formatted_dates(self):
        scale = TimeScale(date(2024, 1, 1), date(2024, 12, 31))
        labels = scale.tick_labels()
        assert all(isinstance(label, str) for label in labels)
        # Labels should look like dates, not raw epoch seconds.
        assert any("2024" in label or "-" in label for label in labels)


class TestDegenerateRanges:
    """Single-point, all-equal, and all-zero domains must not collapse.

    A zero-width domain (min == max) previously made ``ticks()`` return two
    identical positions, giving an empty axis, and ``reproject`` divides by a
    zero range. These guards keep the axis non-empty and the math NaN-free.
    """

    def test_linear_single_point_does_not_divide_by_zero(self):
        scale = LinearScale(5, 5)
        # No ZeroDivisionError, no NaN: collapses to the min pixel.
        assert scale.reproject(5, 400) == 0.0

    def test_linear_single_point_ticks_are_distinct(self):
        scale = LinearScale(5, 5)
        ticks = scale.ticks()
        assert len(ticks) == 2
        assert ticks[0] != ticks[1]
        assert all(t == t for t in ticks)  # not NaN

    def test_linear_all_zero_ticks_are_distinct(self):
        scale = LinearScale(0, 0)
        ticks = scale.ticks()
        assert len(ticks) == 2
        assert ticks[0] != ticks[1]
        assert ticks == [0.0, 1.0]

    def test_linear_all_equal_series_ticks_span_value(self):
        """An all-equal series (e.g. [7, 7, 7]) gives a window around 7."""
        scale = LinearScale(7, 7)
        ticks = scale.ticks()
        assert ticks[0] < 7 < ticks[1]

    def test_log_single_point_ticks_are_distinct(self):
        scale = LogScale(5, 5)
        ticks = scale.ticks()
        assert len(ticks) == 2
        assert ticks[0] != ticks[1]
        assert all(t == t for t in ticks)  # not NaN

    def test_log_single_point_does_not_divide_by_zero(self):
        scale = LogScale(5, 5)
        assert scale.reproject(5, 300) == 0.0

    def test_time_single_date_ticks_are_distinct(self):
        scale = TimeScale(date(2024, 6, 1), date(2024, 6, 1))
        ticks = scale.ticks()
        assert len(ticks) == 2
        assert ticks[0] != ticks[1]
        assert all(t == t for t in ticks)  # not NaN

    def test_time_single_date_does_not_divide_by_zero(self):
        scale = TimeScale(date(2024, 6, 1), date(2024, 6, 1))
        assert scale.reproject(date(2024, 6, 1), 400) == 0.0


class TestBarColumnScaleRejection:
    """log/time scales are unsupported on a bar/column value axis."""

    def test_column_rejects_log_value_axis(self):
        from charted.charts.column import ColumnChart

        with pytest.raises(ValueError, match="not supported on the value axis"):
            ColumnChart(data=[1, 10, 100], labels=["a", "b", "c"], y_scale="log")

    def test_column_rejects_time_value_axis(self):
        from charted.charts.column import ColumnChart

        with pytest.raises(ValueError, match="not supported on the value axis"):
            ColumnChart(data=[1, 10, 100], labels=["a", "b", "c"], y_scale="time")

    def test_area_rejects_log_value_axis(self):
        from charted.charts.area import AreaChart

        with pytest.raises(ValueError, match="not supported on the value axis"):
            AreaChart(data=[1, 10, 100], labels=["a", "b", "c"], y_scale="log")

    def test_line_still_allows_log_value_axis(self):
        """Line plots points, not filled bars, so log on y stays valid."""
        from charted.charts.line import LineChart

        chart = LineChart(data=[1, 10, 100], labels=["a", "b", "c"], y_scale="log")
        assert "svg" in chart.html.lower()
