"""Scale abstractions for mapping data values to pixel positions.

An :class:`Axis` delegates its value-to-pixel mapping to a ``Scale`` instance.
Three scales are provided:

- :class:`LinearScale` reproduces the original ``Axis._reproject`` behaviour.
- :class:`LogScale` maps values in log10 space (positive values only).
- :class:`TimeScale` maps dates/datetimes/ISO strings linearly in epoch
  seconds and generates calendar-aware ticks.

Only the standard library is used, so no new runtime dependency is added.
"""

from __future__ import annotations

import calendar
import math
from datetime import date, datetime, timezone
from typing import TypeAlias, Union, cast

TimeValue: TypeAlias = Union[date, datetime, str, int, float]


class Scale:
    """Base class for value-to-pixel scales.

    A scale knows the data domain ``[min_value, max_value]`` and maps a value
    into the range ``[0, length]`` where ``length`` is the pixel extent of the
    axis (plot width or height).
    """

    def __init__(self, min_value: float, max_value: float):
        self.min_value = min_value
        self.max_value = max_value

    @staticmethod
    def _degenerate_ticks(value: float) -> list[float]:
        """Return two distinct ticks for a zero-width (min == max) domain.

        A single data point, an all-equal series, or all-zero data collapses
        the domain to ``[value, value]``. Returning ``[value, value]`` gives an
        empty axis (both ticks at the same pixel). Instead, pad the value to a
        sensible visible range: ``[0, 1]`` when the value is zero, otherwise a
        unit window centred on the value.
        """
        if value == 0:
            return [0.0, 1.0]
        return [value - 1, value + 1]

    def reproject(self, value: float, length: float) -> float:
        """Map ``value`` to a pixel offset in ``[0, length]``."""
        raise NotImplementedError

    def reverse(self, pixel: float, length: float) -> float:
        """Map a pixel offset back to a data value (inverse of reproject)."""
        raise NotImplementedError

    def ticks(self) -> list[float]:
        """Return tick positions in data space for this scale."""
        raise NotImplementedError

    @property
    def name(self) -> str:
        """Short string identifier used by ``describe()`` / ``to_config()``."""
        return "scale"


class LinearScale(Scale):
    """Linear scale: the original ``(value - min) / (max - min) * length``."""

    @property
    def name(self) -> str:
        return "linear"

    def reproject(self, value: float, length: float) -> float:
        value_range = self.max_value - self.min_value
        if value_range == 0:
            return 0.0
        normalised = (value - self.min_value) / value_range
        return normalised * length

    def reverse(self, pixel: float, length: float) -> float:
        if length == 0:
            return self.min_value
        value_range = self.max_value - self.min_value
        return self.min_value + (pixel / length) * value_range

    def ticks(self) -> list[float]:
        if self.max_value == self.min_value:
            return self._degenerate_ticks(self.min_value)
        return [self.min_value, self.max_value]


class LogScale(Scale):
    """Logarithmic (base-10) scale. Requires strictly positive bounds."""

    def __init__(self, min_value: float, max_value: float):
        if min_value <= 0 or max_value <= 0:
            raise ValueError(
                f"LogScale requires strictly positive bounds, "
                f"got min={min_value}, max={max_value}."
            )
        super().__init__(min_value, max_value)
        self._log_min = math.log10(min_value)
        self._log_max = math.log10(max_value)

    @property
    def name(self) -> str:
        return "log"

    def reproject(self, value: float, length: float) -> float:
        if value <= 0:
            raise ValueError(
                f"LogScale cannot map non-positive value {value}; "
                f"all data must be > 0 for a log scale."
            )
        log_range = self._log_max - self._log_min
        if log_range == 0:
            return 0.0
        normalised = (math.log10(value) - self._log_min) / log_range
        return normalised * length

    def reverse(self, pixel: float, length: float) -> float:
        if length == 0:
            return self.min_value
        log_range = self._log_max - self._log_min
        log_val = self._log_min + (pixel / length) * log_range
        return 10**log_val

    def ticks(self) -> list[float]:
        """Return the powers of ten spanning the domain (inclusive)."""
        if self.max_value == self.min_value:
            # Single positive point / all-equal positive series: pad to the
            # bracketing decade so the axis has two distinct ticks.
            lo = 10 ** math.floor(self._log_min)
            hi = 10 ** math.ceil(self._log_max)
            if hi == lo:
                hi = lo * 10
            return [int(lo) if lo >= 1 else lo, int(hi) if hi >= 1 else hi]
        lo = math.floor(self._log_min)
        hi = math.ceil(self._log_max)
        powers: list[float] = []
        for exp in range(lo, hi + 1):
            value = 10**exp
            if value < self.min_value or value > self.max_value:
                continue
            # Present clean integers where possible.
            powers.append(int(value) if exp >= 0 else value)
        if not powers:
            powers = [self.min_value, self.max_value]
        return powers


def _to_epoch(value: TimeValue) -> float:
    """Normalise a date/datetime/ISO-string into epoch seconds.

    All conversion is timezone-independent. A timezone-aware ``datetime``
    is converted to its absolute UTC epoch. A *naive* ``datetime``, a
    ``date``, or a tz-less ISO string is interpreted as UTC (never local
    time) so the same input always maps to the same epoch regardless of
    the host's ``TZ``.
    """
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.timestamp()
    if isinstance(value, date):
        return calendar.timegm((value.year, value.month, value.day, 0, 0, 0, 0, 0, 0))
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(
                f"Could not parse {value!r} as an ISO date/datetime."
            ) from exc
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.timestamp()
    raise ValueError(
        f"Unsupported time value {value!r} (type {type(value).__name__}); "
        f"expected date, datetime, ISO string, or epoch number."
    )


class TimeScale(Scale):
    """Time scale: linear in epoch seconds, with calendar-aware ticks.

    Accepts ``date``, ``datetime``, ISO 8601 strings, or epoch numbers for
    the domain bounds and for values passed to :meth:`reproject`.
    """

    def __init__(self, min_value: TimeValue, max_value: TimeValue):
        lo = _to_epoch(min_value)
        hi = _to_epoch(max_value)
        super().__init__(lo, hi)

    @property
    def name(self) -> str:
        return "time"

    def reproject(self, value: TimeValue, length: float) -> float:
        epoch = _to_epoch(value)
        value_range = self.max_value - self.min_value
        if value_range == 0:
            return 0.0
        normalised = (epoch - self.min_value) / value_range
        return normalised * length

    def reverse(self, pixel: float, length: float) -> float:
        if length == 0:
            return self.min_value
        value_range = self.max_value - self.min_value
        return self.min_value + (pixel / length) * value_range

    @staticmethod
    def _utc_epoch(year: int, month: int = 1, day: int = 1) -> float:
        """Epoch seconds for a UTC calendar boundary (TZ-independent)."""
        return float(calendar.timegm((year, month, day, 0, 0, 0, 0, 0, 0)))

    def _span_days(self) -> float:
        return (self.max_value - self.min_value) / 86400.0

    def ticks(self) -> list[float]:
        """Return tick positions (epoch seconds) on clean calendar boundaries.

        Spans up to ~3 years land on month or quarter boundaries; longer spans
        fall back to year boundaries; sub-month spans fall back to evenly
        spaced ticks.
        """
        if self.max_value == self.min_value:
            # Single date / all-equal dates: pad to a one-day window so the
            # axis has two distinct tick positions instead of one.
            return [self.min_value, self.min_value + 86400.0]

        start = datetime.fromtimestamp(self.min_value, tz=timezone.utc)
        span_days = self._span_days()

        if span_days <= 31:
            # Even fallback for short spans.
            return self._even_ticks(5)

        if span_days <= 3 * 366:
            # Monthly (or quarterly for ~1-3 year spans) boundaries.
            step_months = 1 if span_days <= 200 else 3
            ticks: list[float] = []
            year, month = start.year, start.month
            # Snap up to the first month boundary >= start.
            if start.day != 1 or start.hour or start.minute or start.second:
                month += 1
                if month > 12:
                    month = 1
                    year += 1
            # Align to the quarter grid when stepping by 3 months.
            if step_months == 3:
                month = ((month - 1) // 3) * 3 + 1
            while True:
                ts = self._utc_epoch(year, month, 1)
                if ts > self.max_value:
                    break
                if ts >= self.min_value:
                    ticks.append(ts)
                month += step_months
                while month > 12:
                    month -= 12
                    year += 1
            if len(ticks) >= 2:
                return ticks
            return self._even_ticks(5)

        # Year boundaries for long spans.
        ticks = []
        year = (
            start.year
            if self._utc_epoch(start.year, 1, 1) >= self.min_value
            else start.year + 1
        )
        while True:
            ts = self._utc_epoch(year, 1, 1)
            if ts > self.max_value:
                break
            if ts >= self.min_value:
                ticks.append(ts)
            year += 1
        if len(ticks) >= 2:
            return ticks
        return self._even_ticks(5)

    def _even_ticks(self, count: int) -> list[float]:
        if count < 2:
            return [self.min_value, self.max_value]
        step = (self.max_value - self.min_value) / (count - 1)
        return [self.min_value + i * step for i in range(count)]

    def tick_labels(self, fmt: str | None = None) -> list[str]:
        """Return formatted date strings for each tick position."""
        ticks = self.ticks()
        span_days = self._span_days()
        if fmt is None:
            if span_days > 3 * 366:
                fmt = "%Y"
            elif span_days > 31:
                fmt = "%Y-%m"
            else:
                fmt = "%Y-%m-%d"
        return [datetime.fromtimestamp(t, tz=timezone.utc).strftime(fmt) for t in ticks]


def make_scale(
    spec: str | Scale | None, min_value: TimeValue, max_value: TimeValue
) -> Scale:
    """Build a Scale from a string spec or pass through a Scale instance.

    Args:
        spec: ``"linear"``, ``"log"``, ``"time"``, or a :class:`Scale`.
        min_value: Domain minimum (raw value; dates for time scales).
        max_value: Domain maximum.

    Returns:
        A concrete :class:`Scale`.
    """
    if isinstance(spec, Scale):
        return spec
    if spec is None or spec == "linear":
        return LinearScale(cast(float, min_value), cast(float, max_value))
    if spec == "log":
        return LogScale(cast(float, min_value), cast(float, max_value))
    if spec == "time":
        return TimeScale(min_value, max_value)
    raise ValueError(
        f"Unknown scale {spec!r}; expected 'linear', 'log', 'time', "
        f"or a Scale instance."
    )
