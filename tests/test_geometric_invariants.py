"""Property-based geometric-invariant tests for charted chart types.

These tests are *additive*: they sit alongside the baseline/snapshot suite and
never replace it. They render charts on randomized adversarial data (single
points, all-equal series, negatives, tiny/huge magnitudes, zero ranges) and on
random scale domains, then assert invariants that must hold regardless of the
data:

1.  well-formed        - output parses as XML with exactly one root ``<svg>``.
2.  finite-coordinates - every emitted coordinate is a finite number.
3.  in-frame           - every painted element's absolute bbox lies inside the
                         viewBox (within a small stroke/anti-alias tolerance).
4.  no-overlap         - x-axis tick-label boxes do not overlap.
5.  bars-in-plot       - bar/column/bin rects sit inside the plot-area rect.
6.  determinism        - same input + config renders byte-identical SVG.
7.  scale-monotonic     - a larger data value never maps to a smaller pixel
                         offset along a scale's value axis.
8.  scale-proportional - a linear scale maps values proportionally (the
                         midpoint of the domain lands at the midpoint pixel).
9.  ticks-sorted        - scale tick positions are sorted and within domain.
10. clean-failure      - rendering succeeds or raises a charted/value error;
                         any other exception is a real test failure.

Calibration notes
-----------------
The render-level invariants (3-5) are checked at *realistic* canvas sizes
(>= 400 px, charted's default is 500x500) with non-empty labels. Text-label
containment is excluded from the in-frame check: charted does not clip long
labels, an open item in its own TODO.md (#45). Four genuine bugs surfaced
during calibration are documented and pinned by the ``test_known_bug_*`` cases
at the end of this module (all-negative LineChart and BarChart projection, an
empty-label ZeroDivisionError, and small-canvas bottom-label overflow) rather
than silently weakening the main invariants. We do NOT fix charted here.
"""

from __future__ import annotations

import math

import pytest
from hypothesis import HealthCheck, Phase, assume, given, settings
from hypothesis import strategies as st

from charted import (
    AreaChart,
    BarChart,
    ColumnChart,
    HeatmapChart,
    Histogram,
    LineChart,
    PieChart,
    RadarChart,
    ScatterChart,
)
from charted.charts.scales import LinearScale, LogScale
from charted.utils.exceptions import ChartedError
from tests._svg_geometry import (
    BBox,
    bar_boxes,
    bbox_inside_box,
    bbox_inside_viewbox,
    boxes_overlap,
    parse_svg,
    plot_area_box,
    x_axis_tick_label_boxes,
)

# Errors charted raises for input it legitimately rejects. The brief asks us to
# treat a "charted ValueError" as acceptable; charted raises both bare
# ValueError (e.g. negative/all-zero pie) and ChartedError subclasses
# (NoData/InvalidData/etc.), so both count as a clean rejection.
ACCEPTABLE_ERRORS = (ValueError, ChartedError)

# NB: no derandomize=True. Combined with the "ci" hypothesis profile loaded by
# tests/conftest.py it sends generation into a pathological high-memory loop on
# these chart strategies. The repo's CI pins determinism with --hypothesis-seed
# (see tests/properties/*), which is the right knob here.
#
# database=None and a trimmed phase list keep the suite fast and stable on a
# busy shared box: the on-disk example DB stalls badly under disk/swap
# contention, and the explain phase adds re-runs we do not need. Determinism
# comes from --hypothesis-seed in CI.
SETTINGS = settings(
    max_examples=20,
    deadline=None,
    database=None,
    phases=(Phase.explicit, Phase.reuse, Phase.generate, Phase.shrink),
    suppress_health_check=[HealthCheck.data_too_large, HealthCheck.too_slow],
)

# Charted reserves a fixed bottom margin for value-axis labels that does not
# scale down on small canvases (see module docstring). Restrict render-level
# invariants to canvases at least this size, where the contract holds.
DIMENSIONS = [(500.0, 500.0), (640.0, 480.0), (500.0, 400.0)]
_dims = st.sampled_from(DIMENSIONS)

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Values spanning 1e-4 .. 1e9 in magnitude, both signs, including zero.
_adversarial_float = st.one_of(
    st.floats(min_value=-1e9, max_value=1e9, allow_nan=False, allow_infinity=False),
    st.floats(min_value=1e-4, max_value=1e9, allow_nan=False, allow_infinity=False).map(
        lambda v: -v
    ),
    st.just(0.0),
    st.just(1e-4),
    st.just(1e9),
)

# Strictly positive values (for charts/scales that require them, e.g. pie/log).
_positive_float = st.one_of(
    st.floats(min_value=1e-4, max_value=1e9, allow_nan=False, allow_infinity=False),
    st.just(1e-4),
    st.just(1e9),
)


def value_lists(
    min_size: int = 1, max_size: int = 60
) -> st.SearchStrategy[list[float]]:
    """Lists of adversarial floats: mixed signs, tiny/huge magnitudes, zeros."""
    return st.lists(_adversarial_float, min_size=min_size, max_size=max_size)


def equal_value_lists(max_size: int = 30) -> st.SearchStrategy[list[float]]:
    """All-equal value lists (degenerate domain), length 1..max_size."""
    return st.builds(
        lambda v, n: [v] * n,
        _adversarial_float,
        st.integers(min_value=1, max_value=max_size),
    )


def any_value_lists(
    min_size: int = 1, max_size: int = 30
) -> st.SearchStrategy[list[float]]:
    """Either a varied or an all-equal adversarial value list."""
    return st.one_of(value_lists(min_size, max_size), equal_value_lists(max_size))


# Label pools, always non-empty. (No 40+ char labels: charted does not clip
# arbitrarily long labels, an orthogonal text-layout concern - TODO.md #45.
# Empty labels crash the rotated axis with a ZeroDivisionError, a separate
# known bug pinned by test_known_bug_empty_label_zero_division.)
#
# Labels are generated by picking one short style and cycling it to the exact
# series length. A fixed-size list-of-text strategy is both slow to generate
# and prone to large example buffers, so we draw a single style index instead.
_LABEL_POOLS: tuple[tuple[str, ...], ...] = (
    ("a", "bb", "ccc", "d", "ee", "fff"),
    ("東京", "日本", "中文", "한국", "ñü", "éx"),
    ("x",),
)


def labels_for(n: int) -> st.SearchStrategy[list[str]]:
    """A list of exactly ``n`` non-empty labels, cycled from a small pool."""
    return st.sampled_from(_LABEL_POOLS).map(
        lambda pool: [pool[i % len(pool)] for i in range(n)]
    )


@st.composite
def labeled_values(
    draw: st.DrawFn,
    min_size: int = 1,
    max_size: int = 30,
) -> tuple[list[float], list[str], tuple[float, float]]:
    """Draw (values, matching labels, (width, height))."""
    values = draw(any_value_lists(min_size, max_size))
    labels = draw(labels_for(len(values)))
    dims = draw(_dims)
    return values, labels, dims


# ---------------------------------------------------------------------------
# Shared assertion helpers
# ---------------------------------------------------------------------------


def _assert_well_formed(svg: str) -> None:
    parsed = parse_svg(svg)  # raises on malformed XML
    assert svg.lstrip().startswith("<svg"), "output does not start with a root <svg>"
    assert svg.count("<svg") == 1, "more than one <svg> root element"
    assert svg.rstrip().endswith("</svg>")
    vb = parsed.viewbox
    assert all(math.isfinite(v) for v in vb), f"non-finite viewBox {vb}"


def _assert_finite_coords(svg: str) -> None:
    parsed = parse_svg(svg)
    for el in parsed.elements:
        box = el.bbox()
        if any(math.isnan(v) or math.isinf(v) for v in box):
            raise AssertionError(f"non-finite bbox for <{el.tag}>: {box}")


def _assert_in_frame(svg: str, tol: float = 1.0) -> None:
    """Assert every painted *data-geometry* element stays inside the viewBox.

    Text elements are excluded: long/unicode tick and value labels can extend
    past the plot, which charted documents as an open item (TODO.md #45,
    "graceful handling (or truncation) of ... very long labels overflowing the
    plot"). Label containment is therefore not a current charted contract, so
    asserting it would test an intended-future feature, not today's geometry.
    The geometry that *is* contractual - bars, points, data paths, gridlines -
    must stay framed.
    """
    parsed = parse_svg(svg)
    for el in parsed.elements:
        if el.tag == "text":
            continue
        box = el.bbox()
        if any(math.isnan(v) or math.isinf(v) for v in box):
            raise AssertionError(f"non-finite bbox for <{el.tag}>: {box}")
        assert bbox_inside_viewbox(el, parsed.viewbox, tol=tol), (
            f"<{el.tag}> bbox={box} escapes viewBox={parsed.viewbox}"
        )


def _assert_no_label_overlap(svg: str, tol: float = 1.0) -> None:
    parsed = parse_svg(svg)
    boxes: list[BBox] = x_axis_tick_label_boxes(parsed)
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            assert not boxes_overlap(boxes[i], boxes[j], tol=tol), (
                f"x-axis tick labels overlap: {boxes[i]} vs {boxes[j]}"
            )


def _assert_bars_in_plot(svg: str, tol: float = 1.0) -> None:
    parsed = parse_svg(svg)
    plot = plot_area_box(svg)
    assume(plot is not None)
    assert plot is not None  # for type-narrowing
    for box in bar_boxes(parsed):
        assert bbox_inside_box(box, plot, tol=tol), (
            f"bar rect {box} escapes plot area {plot}"
        )


def _render_or_skip(make: object) -> str | None:
    """Render via ``make()``; return SVG, or None if charted rejected the input.

    Any non-charted exception propagates and fails the test (the clean-failure
    invariant).
    """
    assert callable(make)
    try:
        return str(make())
    except ACCEPTABLE_ERRORS:
        return None


# All chart builders keyed by name, parameterised on a single value list.
# LineChart is restricted to non-all-negative data via _line_safe (or an inline
# guard) where it is exercised, because all-negative line projection is a known
# bug pinned by test_known_bug_line_all_negative_overflows_top.
ALL_CHART_BUILDERS: dict[str, object] = {
    "BarChart": lambda v: BarChart(v, labels=[str(i) for i in range(len(v))]),
    "ColumnChart": lambda v: ColumnChart(v, labels=[str(i) for i in range(len(v))]),
    "LineChart": lambda v: LineChart(v, labels=[str(i) for i in range(len(v))]),
    "AreaChart": lambda v: AreaChart(v, labels=[str(i) for i in range(len(v))]),
    "ScatterChart": lambda v: ScatterChart(v, v),
    "Histogram": lambda v: Histogram(v),
    "HeatmapChart": lambda v: HeatmapChart([v]),
    "RadarChart": lambda v: RadarChart(v, labels=[str(i) for i in range(len(v))]),
    "PieChart": lambda v: PieChart(v),
}


# ---------------------------------------------------------------------------
# Invariant 1 + 2: well-formed SVG and finite coordinates (all chart types)
# ---------------------------------------------------------------------------


@SETTINGS
@given(
    values=any_value_lists(min_size=1, max_size=40),
    name=st.sampled_from(sorted(ALL_CHART_BUILDERS)),
)
def test_well_formed_and_finite(values: list[float], name: str) -> None:
    builder = ALL_CHART_BUILDERS[name]
    assert callable(builder)
    # LineChart projects all-negative series above the frame (known bug, see
    # the xfail test); keep it out of the well-formed/finite sweep so this test
    # exercises the contract that does hold for every type.
    if name == "LineChart" and values and all(v < 0 for v in values):
        values = [abs(v) for v in values]
    svg = _render_or_skip(lambda: builder(values).to_svg())
    assume(svg is not None)
    assert svg is not None
    _assert_well_formed(svg)
    _assert_finite_coords(svg)


# ---------------------------------------------------------------------------
# Invariant 3: in-frame (all element bboxes inside viewBox)
# ---------------------------------------------------------------------------


def _line_safe(
    data: tuple[list[float], list[str], tuple[float, float]],
) -> tuple[list[float], list[str], tuple[float, float]]:
    """Replace an all-negative line series with its magnitudes (known bug)."""
    values, labels, dims = data
    if values and all(v < 0 for v in values):
        values = [abs(v) for v in values]
    return values, labels, dims


@SETTINGS
@given(data=labeled_values())
def test_bar_in_frame(data: tuple[list[float], list[str], tuple[float, float]]) -> None:
    # BarChart (horizontal) places its zero gridline far outside the plot for an
    # all-negative series, the same projection bug as LineChart. Exclude that
    # case here; it is pinned by test_known_bug_all_negative_overflows below.
    values, labels, (w, h) = _line_safe(data)
    svg = _render_or_skip(
        lambda: BarChart(values, labels=labels, width=w, height=h).to_svg()
    )
    assume(svg is not None)
    assert svg is not None
    _assert_in_frame(svg)


@SETTINGS
@given(data=labeled_values())
def test_column_in_frame(
    data: tuple[list[float], list[str], tuple[float, float]],
) -> None:
    values, labels, (w, h) = data
    svg = _render_or_skip(
        lambda: ColumnChart(values, labels=labels, width=w, height=h).to_svg()
    )
    assume(svg is not None)
    assert svg is not None
    _assert_in_frame(svg)


@SETTINGS
@given(data=labeled_values())
def test_line_in_frame(
    data: tuple[list[float], list[str], tuple[float, float]],
) -> None:
    values, labels, (w, h) = _line_safe(data)
    svg = _render_or_skip(
        lambda: LineChart(values, labels=labels, width=w, height=h).to_svg()
    )
    assume(svg is not None)
    assert svg is not None
    _assert_in_frame(svg)


@SETTINGS
@given(data=labeled_values())
def test_area_in_frame(
    data: tuple[list[float], list[str], tuple[float, float]],
) -> None:
    values, labels, (w, h) = data
    svg = _render_or_skip(
        lambda: AreaChart(values, labels=labels, width=w, height=h).to_svg()
    )
    assume(svg is not None)
    assert svg is not None
    _assert_in_frame(svg)


@SETTINGS
@given(
    xs=value_lists(min_size=1, max_size=40),
    data=st.data(),
    dims=_dims,
)
def test_scatter_in_frame(
    xs: list[float], data: st.DataObject, dims: tuple[float, float]
) -> None:
    ys = data.draw(st.lists(_adversarial_float, min_size=len(xs), max_size=len(xs)))
    w, h = dims
    svg = _render_or_skip(lambda: ScatterChart(xs, ys, width=w, height=h).to_svg())
    assume(svg is not None)
    assert svg is not None
    _assert_in_frame(svg)


@SETTINGS
@given(values=value_lists(min_size=1, max_size=120), dims=_dims)
def test_histogram_in_frame(values: list[float], dims: tuple[float, float]) -> None:
    w, h = dims
    svg = _render_or_skip(lambda: Histogram(values, width=w, height=h).to_svg())
    assume(svg is not None)
    assert svg is not None
    _assert_in_frame(svg)


@SETTINGS
@given(
    rows=st.integers(min_value=1, max_value=8),
    cols=st.integers(min_value=1, max_value=8),
    data=st.data(),
    dims=_dims,
)
def test_heatmap_in_frame(
    rows: int, cols: int, data: st.DataObject, dims: tuple[float, float]
) -> None:
    matrix = [
        data.draw(st.lists(_adversarial_float, min_size=cols, max_size=cols))
        for _ in range(rows)
    ]
    w, h = dims
    svg = _render_or_skip(lambda: HeatmapChart(matrix, width=w, height=h).to_svg())
    assume(svg is not None)
    assert svg is not None
    _assert_in_frame(svg)


@SETTINGS
@given(
    values=st.lists(_positive_float, min_size=1, max_size=12),
    dims=_dims,
    data=st.data(),
)
def test_pie_in_frame(
    values: list[float], dims: tuple[float, float], data: st.DataObject
) -> None:
    labels = data.draw(labels_for(len(values)))
    w, h = dims
    svg = _render_or_skip(
        lambda: PieChart(values, labels=labels, width=w, height=h).to_svg()
    )
    assume(svg is not None)
    assert svg is not None
    _assert_in_frame(svg)


# ---------------------------------------------------------------------------
# Invariant 4: no x-axis tick-label overlap
# ---------------------------------------------------------------------------


@SETTINGS
@given(data=labeled_values())
def test_bar_no_label_overlap(
    data: tuple[list[float], list[str], tuple[float, float]],
) -> None:
    values, labels, (w, h) = data
    svg = _render_or_skip(
        lambda: BarChart(values, labels=labels, width=w, height=h).to_svg()
    )
    assume(svg is not None)
    assert svg is not None
    _assert_no_label_overlap(svg)


@SETTINGS
@given(data=labeled_values())
def test_column_no_label_overlap(
    data: tuple[list[float], list[str], tuple[float, float]],
) -> None:
    values, labels, (w, h) = data
    svg = _render_or_skip(
        lambda: ColumnChart(values, labels=labels, width=w, height=h).to_svg()
    )
    assume(svg is not None)
    assert svg is not None
    _assert_no_label_overlap(svg)


@SETTINGS
@given(data=labeled_values())
def test_line_no_label_overlap(
    data: tuple[list[float], list[str], tuple[float, float]],
) -> None:
    values, labels, (w, h) = _line_safe(data)
    svg = _render_or_skip(
        lambda: LineChart(values, labels=labels, width=w, height=h).to_svg()
    )
    assume(svg is not None)
    assert svg is not None
    _assert_no_label_overlap(svg)


# ---------------------------------------------------------------------------
# Invariant 5: bars/columns/bins inside plot area
# ---------------------------------------------------------------------------


@SETTINGS
@given(data=labeled_values())
def test_bar_bars_in_plot(
    data: tuple[list[float], list[str], tuple[float, float]],
) -> None:
    # All-negative bars project past the plot right edge (same root cause as the
    # gridline bug, pinned by test_known_bug_bar_all_negative_gridline_overflows).
    values, labels, (w, h) = _line_safe(data)
    svg = _render_or_skip(
        lambda: BarChart(values, labels=labels, width=w, height=h).to_svg()
    )
    assume(svg is not None)
    assert svg is not None
    _assert_bars_in_plot(svg)


@SETTINGS
@given(data=labeled_values())
def test_column_bars_in_plot(
    data: tuple[list[float], list[str], tuple[float, float]],
) -> None:
    values, labels, (w, h) = data
    svg = _render_or_skip(
        lambda: ColumnChart(values, labels=labels, width=w, height=h).to_svg()
    )
    assume(svg is not None)
    assert svg is not None
    _assert_bars_in_plot(svg)


@SETTINGS
@given(values=value_lists(min_size=1, max_size=120), dims=_dims)
def test_histogram_bars_in_plot(values: list[float], dims: tuple[float, float]) -> None:
    w, h = dims
    svg = _render_or_skip(lambda: Histogram(values, width=w, height=h).to_svg())
    assume(svg is not None)
    assert svg is not None
    _assert_bars_in_plot(svg)


# ---------------------------------------------------------------------------
# Invariant 6: rendering is deterministic (byte-identical for same input)
# ---------------------------------------------------------------------------


@SETTINGS
@given(
    values=any_value_lists(min_size=1, max_size=40),
    name=st.sampled_from(sorted(ALL_CHART_BUILDERS)),
)
def test_render_is_deterministic(values: list[float], name: str) -> None:
    builder = ALL_CHART_BUILDERS[name]
    assert callable(builder)
    first = _render_or_skip(lambda: builder(values).to_svg())
    assume(first is not None)
    # A clean rejection must be deterministic too: re-rendering rejects again.
    second = _render_or_skip(lambda: builder(values).to_svg())
    assert first == second, f"{name} render not deterministic for {values!r}"


# ---------------------------------------------------------------------------
# Invariants 7-9: scale geometry (monotonic, proportional, ticks sorted)
# ---------------------------------------------------------------------------

_finite_value = st.floats(
    min_value=-1e9, max_value=1e9, allow_nan=False, allow_infinity=False
)
_length = st.floats(min_value=1.0, max_value=2000.0)


@st.composite
def _ordered_domain(draw: st.DrawFn) -> tuple[float, float]:
    """A (lo, hi) domain with lo <= hi, both finite."""
    a = draw(_finite_value)
    b = draw(_finite_value)
    return (a, b) if a <= b else (b, a)


@SETTINGS
@given(
    domain=_ordered_domain(),
    length=_length,
    vals=st.lists(_finite_value, min_size=2, max_size=20),
)
def test_linear_scale_monotonic(
    domain: tuple[float, float], length: float, vals: list[float]
) -> None:
    lo, hi = domain
    scale = LinearScale(lo, hi)
    ordered = sorted(vals)
    pixels = [scale.reproject(v, length) for v in ordered]
    for p in pixels:
        assert math.isfinite(p), f"non-finite pixel {p}"
    for a, b in zip(pixels, pixels[1:]):
        # Larger value -> not a smaller pixel offset (weakly increasing).
        assert b >= a - 1e-6, (
            f"linear scale non-monotonic on domain {domain}: {a} -> {b}"
        )


@SETTINGS
@given(domain=_ordered_domain(), length=_length)
def test_linear_scale_proportional(domain: tuple[float, float], length: float) -> None:
    lo, hi = domain
    assume(hi - lo > 1e-3)  # non-degenerate domain
    scale = LinearScale(lo, hi)
    mid_value = (lo + hi) / 2.0
    mid_pixel = scale.reproject(mid_value, length)
    # Midpoint value lands at the midpoint pixel, within float tolerance scaled
    # by the magnitude of the operands.
    expected = length / 2.0
    tol = 1e-6 * max(1.0, abs(length), abs(lo), abs(hi))
    assert math.isclose(mid_pixel, expected, abs_tol=max(tol, 1e-6)), (
        f"midpoint {mid_value} -> {mid_pixel}, expected {expected} (domain {domain})"
    )
    # Endpoints map to 0 and length (float tolerance scaled by length).
    endpoint_tol = max(1e-6, 1e-9 * length)
    assert math.isclose(scale.reproject(lo, length), 0.0, abs_tol=endpoint_tol)
    assert math.isclose(scale.reproject(hi, length), length, abs_tol=endpoint_tol)


@SETTINGS
@given(domain=_ordered_domain())
def test_linear_ticks_sorted_in_domain(domain: tuple[float, float]) -> None:
    lo, hi = domain
    scale = LinearScale(lo, hi)
    ticks = scale.ticks()
    assert ticks, "linear scale produced no ticks"
    assert all(math.isfinite(t) for t in ticks)
    assert ticks == sorted(ticks), f"ticks not sorted: {ticks}"
    if hi > lo:
        # Non-degenerate domain ticks stay within the (padded) domain bounds.
        assert min(ticks) >= lo - 1e-6
        assert max(ticks) <= hi + 1e-6


@SETTINGS
@given(
    lo=st.floats(min_value=1e-4, max_value=1e8, allow_nan=False, allow_infinity=False),
    factor=st.floats(
        min_value=1.0, max_value=1e4, allow_nan=False, allow_infinity=False
    ),
    length=_length,
)
def test_log_scale_monotonic_and_ticks(lo: float, factor: float, length: float) -> None:
    hi = lo * factor
    scale = LogScale(lo, hi)
    # Monotonic across a geometric sweep of the domain.
    n = 8
    samples = [lo * (hi / lo) ** (i / n) for i in range(n + 1)] if hi > lo else [lo]
    pixels = [scale.reproject(v, length) for v in samples]
    for p in pixels:
        assert math.isfinite(p)
    for a, b in zip(pixels, pixels[1:]):
        assert b >= a - 1e-6, f"log scale non-monotonic: {a} -> {b}"
    ticks = scale.ticks()
    assert ticks, "log scale produced no ticks"
    assert ticks == sorted(ticks), f"log ticks not sorted: {ticks}"


# ---------------------------------------------------------------------------
# Invariant 10: clean failure (no unexpected exception type)
# ---------------------------------------------------------------------------


@SETTINGS
@given(
    values=any_value_lists(min_size=1, max_size=120),
    name=st.sampled_from(sorted(ALL_CHART_BUILDERS)),
)
def test_clean_failure_no_unexpected_exception(values: list[float], name: str) -> None:
    builder = ALL_CHART_BUILDERS[name]
    assert callable(builder)
    try:
        svg = str(builder(values).to_svg())
    except ACCEPTABLE_ERRORS:
        return
    # If it rendered, the output must at least be a well-formed SVG string.
    assert svg.startswith("<svg")
    assert svg.rstrip().endswith("</svg>")


# ---------------------------------------------------------------------------
# Documented known bugs (pinned, not fixed)
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "GEOMETRY BUG: LineChart with an all-negative series projects the data "
        "path above the top of the viewBox. Repro: LineChart([-2.0, -3.0, -1.0], "
        "labels=['a','b','c'], width=500, height=500) -> line path bbox top y ~= "
        "-200 (viewBox top is 0). Mixed-sign and all-positive series render "
        "correctly; AreaChart clamps and is unaffected."
    ),
)
def test_known_bug_line_all_negative_overflows_top() -> None:
    svg = str(
        LineChart(
            [-2.0, -3.0, -1.0], labels=["a", "b", "c"], width=500, height=500
        ).to_svg()
    )
    _assert_in_frame(svg)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "GEOMETRY BUG: horizontal BarChart with an all-negative series places "
        "both its zero gridline and the bar rect far to the right of the plot. "
        "Repro: BarChart([-2.0], labels=[''], width=500, height=500) -> gridline "
        "path 'M900 0 v450' at x~=925 (viewBox is 500 wide); BarChart([-16.0], "
        "labels=['a']) -> bar rect x-extent 475..1802 vs plot right edge 475. "
        "With [-1e9] the gridline is at x~=4.5e11. Same projection fault as the "
        "LineChart case. ColumnChart and mixed-sign data are unaffected."
    ),
)
def test_known_bug_bar_all_negative_gridline_overflows() -> None:
    svg = str(BarChart([-2.0], labels=[""], width=500, height=500).to_svg())
    _assert_in_frame(svg)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "CLEAN-FAILURE BUG: an empty-string axis label crashes the rotated "
        "x-axis with an uncaught ZeroDivisionError instead of rendering or "
        "raising a charted error. axes.py:608 computes "
        "'label.width / len(label.text)' which divides by len('')==0 once the "
        "axis is dense enough to rotate labels. Repro: "
        "ColumnChart([5.0]*20, labels=['abcdef']*10 + ['']*10, width=500, "
        "height=500). Affects ColumnChart and LineChart (rotated bottom axis); "
        "BarChart (horizontal) is unaffected."
    ),
    raises=ZeroDivisionError,
)
def test_known_bug_empty_label_zero_division() -> None:
    labels = ["abcdef"] * 10 + [""] * 10
    ColumnChart([5.0] * 20, labels=labels, width=500, height=500).to_svg()


def _text_in_frame_violations(svg: str, tol: float = 1.0) -> list[str]:
    parsed = parse_svg(svg)
    out: list[str] = []
    for el in parsed.elements:
        if el.tag != "text" or not (el.text and el.text.strip()):
            continue
        if not bbox_inside_viewbox(el, parsed.viewbox, tol=tol):
            out.append(f"{el.text!r} bbox={el.bbox()}")
    return out


@pytest.mark.xfail(
    strict=True,
    reason=(
        "GEOMETRY/LAYOUT BUG: on small canvases (height < ~400px) charted's "
        "fixed bottom-axis margin does not shrink, so the bottom value-axis "
        "tick labels overflow the viewBox by a few pixels. Repro: "
        "BarChart([5,10,15], labels=['a','b','c'], width=320, height=240) -> "
        "bottom tick-label baseline lands at absolute y=246 (viewBox bottom is "
        "240). Related to TODO.md #45 (long-label overflow)."
    ),
)
def test_known_bug_small_canvas_bottom_labels_overflow() -> None:
    values: list[float] = [5.0, 10.0, 15.0]
    svg = str(BarChart(values, labels=["a", "b", "c"], width=320, height=240).to_svg())
    violations = _text_in_frame_violations(svg)
    assert not violations, f"labels overflow small canvas: {violations}"
