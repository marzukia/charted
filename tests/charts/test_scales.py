"""Unit tests for the Scale abstraction (linear, log, time)."""

from datetime import date, datetime

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
            dt = datetime.fromtimestamp(t)
            assert dt.day == 1

    def test_time_scale_tick_labels_are_formatted_dates(self):
        scale = TimeScale(date(2024, 1, 1), date(2024, 12, 31))
        labels = scale.tick_labels()
        assert all(isinstance(label, str) for label in labels)
        # Labels should look like dates, not raw epoch seconds.
        assert any("2024" in label or "-" in label for label in labels)
