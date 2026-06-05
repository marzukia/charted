"""Scale and axis-data construction helpers for charts.

Extracted from the :class:`~charted.charts.chart.Chart` base class to reduce
its size. The methods are unchanged; they are mixed back into ``Chart`` via
the class bases, so they continue to operate on the same ``self``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from charted.charts.scales import Scale
    from charted.themes.core import Theme
    from charted.utils.types import Vector, Vector2D


class ChartScaleMixin:
    """Scale/axis-data construction behavior for :class:`Chart`.

    Provides the scale instantiation, time-data normalization, and axis-data
    anchoring helpers used inside ``Chart.__init__``. These rely on attributes
    supplied by the concrete chart class (``theme``, ``_domain_padding``); they
    are declared here only for type checking.
    """

    if TYPE_CHECKING:
        theme: Theme
        _domain_padding: float | None

    # Chart types whose value axis fills from a zero baseline (bars/columns).
    # log/time scales are unsupported on that axis.
    _BAR_VALUE_AXIS = {
        "column": "y",
        "area": "y",
        "histogram": "y",
        "bar": "x",
    }

    @classmethod
    def _reject_unsupported_scales(
        cls,
        chart_type: str | None,
        x_scale_inst: Scale | None,
        y_scale_inst: Scale | None,
    ) -> None:
        """Raise ValueError for log/time scales on a bar/column value axis."""
        value_axis = cls._BAR_VALUE_AXIS.get(cast("str", chart_type))
        if value_axis is None:
            return
        scale = x_scale_inst if value_axis == "x" else y_scale_inst
        if scale is None:
            return
        name = getattr(scale, "name", "linear")
        if name in ("log", "time"):
            raise ValueError(
                f"{name!r} scale is not supported on the value axis "
                f"({value_axis}) of a {chart_type} chart. Bar/column geometry "
                f"fills from a zero baseline, which a log or time scale has no "
                f"meaning for. Use a linear value axis, or switch to a line or "
                f"scatter chart, which plot points instead of filled bars."
            )

    @staticmethod
    def _is_time_scale(spec: object | None) -> bool:
        from charted.charts.scales import TimeScale

        return spec == "time" or isinstance(spec, TimeScale)

    @staticmethod
    def _normalize_time_data(x_data: Vector | Vector2D) -> Vector | Vector2D:
        """Convert date/datetime/ISO-string x-data into epoch seconds."""
        from charted.charts.scales import _to_epoch

        def conv(seq: Vector) -> Vector:
            return [_to_epoch(v) for v in seq]

        if x_data and isinstance(x_data[0], list):
            return [conv(row) for row in x_data]
        return conv(cast("Vector", x_data))

    def _anchor_axis_data(
        self,
        data: Vector2D,
        fixed_range: tuple[float, float] | None,
        zero_baseline: bool = False,
        stacked: bool = False,
    ) -> Vector2D:
        """Return axis data anchored to a fixed range or padded domain.

        The linear axes derive their domain (min/max) from the flattened data
        they are given. To let callers control the visible span without adding
        invisible data points, this appends synthetic anchor values so the
        derived domain reaches the requested bounds:

        - ``fixed_range`` (``x_range``/``y_range``): anchor to its exact
          (min, max), replacing the data-derived domain.
        - ``domain_padding``: a fractional pad applied to the data-derived
          (min, max) on each side, e.g. ``0.1`` adds 10% of the data span as
          headroom above and below.

        ``zero_baseline`` marks a value axis whose geometry fills from zero
        (bar/column/area/histogram). For these, padding the side that holds the
        baseline would push the baseline off zero and distort every bar, so the
        pad is only applied away from zero: above the tallest positive value,
        below the lowest negative value, or both when the data straddles zero.
        The zero baseline itself never moves.

        When neither range nor padding is set the original data is returned
        unchanged, so the historical auto-fit domain is byte-for-byte preserved.
        """
        if fixed_range is None and self._domain_padding is None:
            return data
        if not data or not any(row for row in data):
            return data

        # Determine the data-derived extent the axis will see. A stacked value
        # axis aggregates per category (sum of positive series for the top, sum
        # of negative series for the bottom), so the extent must be measured the
        # same way or the headroom is computed against the wrong magnitude.
        count = len(data[0])
        if stacked:
            tops = [0.0] * count
            bottoms = [0.0] * count
            for row in data:
                for i in range(min(count, len(row))):
                    v = row[i]
                    if v < 0:
                        bottoms[i] += v
                    else:
                        tops[i] += v
            d_min, d_max = min(bottoms), max(tops)
        else:
            flat = [v for row in data for v in row]
            d_min, d_max = min(flat), max(flat)

        if fixed_range is not None:
            lo, hi = min(fixed_range), max(fixed_range)
        else:
            span = d_max - d_min
            # A zero span (single distinct value) has no fraction to pad; leave
            # the data alone so the axis keeps its own degenerate-domain logic.
            if span == 0:
                return data
            # When fixed_range is None the constructor guard guarantees
            # _domain_padding is set; assert it for the type checker.
            assert self._domain_padding is not None
            pad = span * self._domain_padding
            if zero_baseline:
                # Keep the zero baseline pinned: only add headroom on the side
                # away from zero. Positive-only data pads the top, negative-only
                # pads the bottom, straddling data pads both.
                lo = d_min - pad if d_min < 0 else d_min
                hi = d_max + pad if d_max > 0 else d_max
            else:
                lo, hi = d_min - pad, d_max + pad

        if stacked:
            # The axis sums each category, so a short [lo, hi] anchor row would
            # both crash the per-category loop and be summed into a column. Add
            # full-width anchor rows whose top/bottom extremes already account
            # for the existing stacked totals, so the aggregated max reaches hi
            # and min reaches lo without inflating any real category.
            top_row = [0.0] * count
            bot_row = [0.0] * count
            top_i = max(range(count), key=lambda i: tops[i])
            bot_i = min(range(count), key=lambda i: bottoms[i])
            if hi > tops[top_i]:
                top_row[top_i] = hi - tops[top_i]
            if lo < bottoms[bot_i]:
                bot_row[bot_i] = lo - bottoms[bot_i]
            return [*[list(row) for row in data], top_row, bot_row]

        # Append the bounds as an extra series so min()/max() over the flattened
        # data reach lo/hi without altering the plotted points themselves.
        return [*[list(row) for row in data], [lo, hi]]

    def _build_grid_config(self) -> str | dict[str, object]:
        """Assemble the gridline config passed to each axis.

        Returns the plain grid colour string when the theme requests no
        gridline-hierarchy features, keeping existing renders unchanged. When a
        dash pattern, an explicit major width, or minor subdivisions are set,
        returns a dict carrying the major-line attributes plus the minor-grid
        parameters (consumed by the axis grid_lines renderer).
        """
        theme = self.theme
        color = theme.resolved_grid_color
        width = theme.resolved_grid_width
        dasharray = theme.grid_dasharray
        divisions = theme.minor_grid_divisions

        if width is None and dasharray is None and divisions <= 0:
            return color

        config: dict[str, object] = {
            "stroke": color,
            "stroke_dasharray": dasharray if dasharray is not None else "None",
        }
        if width is not None:
            config["stroke_width"] = width
        if divisions > 0:
            config["minor_divisions"] = divisions
            config["minor_stroke"] = theme.resolved_minor_grid_color
            config["minor_stroke_width"] = theme.resolved_minor_grid_width
        return config

    def _build_scale(self, spec: object | None, data: Vector2D) -> Scale | None:
        """Construct a Scale instance for an axis from its data domain.

        Returns None for the default linear case so the axis keeps its
        original tick math untouched.
        """
        from charted.charts.scales import Scale, make_scale

        if spec is None or spec == "linear":
            return None
        flat = [v for row in data for v in row] if data else []
        if not flat:
            domain_min, domain_max = 0.0, 1.0
        else:
            domain_min, domain_max = min(flat), max(flat)
        if isinstance(spec, Scale):
            return spec
        return make_scale(cast("str | Scale | None", spec), domain_min, domain_max)
