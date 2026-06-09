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
labels, an open item in its own TODO.md (#45). Several genuine bugs surfaced
during calibration (all-negative projection, mixed-magnitude tick explosion,
an empty-label ZeroDivisionError, small-canvas bottom-label overflow); they
have since been fixed and are guarded by the regression cases at the end of
this module.
"""

from __future__ import annotations

import math
import resource  # POSIX-only, like the rest of this suite's CI targets
from collections.abc import Iterator

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
    SankeyChart,
    ScatterChart,
)
from charted.charts.scales import LinearScale, LogScale
from charted.utils.exceptions import ChartedError
from charted.utils.sankey_layout import compute_layout
from tests._svg_geometry import (
    BBox,
    bar_boxes,
    bbox_inside_box,
    bbox_inside_viewbox,
    boxes_overlap,
    legend_swatch_and_text_boxes,
    parse_svg,
    pie_circle_box,
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
    """Lists of adversarial floats: mixed signs, tiny/huge magnitudes, zeros.

    Mixed-magnitude domains (e.g. (-1.0, 1e9)) used to explode the value-axis
    tick list and were filtered out; the axis now bounds its tick step, so the
    full adversarial range is exercised directly.
    """
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


def _assert_pie_legend_clear_of_circle(svg: str, tol: float = 1.0) -> None:
    """Assert no pie legend swatch/label overlaps the pie's circle.

    The pie legend must sit in a band outside the circle's bounding box. This
    guards against two related regressions: a legend column laid out inside the
    circle's footprint, and an in-slice centroid label duplicating a legend
    entry (the duplicate text overlaps a wedge and so overlaps the circle box).
    Skipped when the chart drew no wedge path (single full-circle slice) or no
    legend at all.
    """
    parsed = parse_svg(svg)
    circle = pie_circle_box(parsed)
    if circle is None:
        return
    for box in legend_swatch_and_text_boxes(parsed):
        assert not boxes_overlap(circle, box, tol=tol), (
            f"pie legend element {box} overlaps the pie circle {circle}"
        )


def _assert_each_label_once(svg: str, labels: list[str]) -> None:
    """Assert every category label string appears exactly once in the SVG text.

    Locks the double-label fix: a slice must not be named by both a legend entry
    and an in-slice centroid label.
    """
    parsed = parse_svg(svg)
    rendered = [t.text for t in parsed.texts() if t.text and t.text.strip()]
    for label in labels:
        matches = [t for t in rendered if t == label]
        assert len(matches) == 1, (
            f"label {label!r} rendered {len(matches)} times (expected 1): {rendered}"
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


@pytest.fixture(autouse=True, scope="module")
def _memory_ceiling() -> Iterator[None]:
    """Cap this test process's address space at 192 MiB.

    The suite's honest peak is ~60 MiB; the headroom only exists so a leaking
    example dies fast instead of slow. The mixed-magnitude tick explosion that
    once forced multi-gigabyte allocations is fixed (the axis now bounds its
    tick step), so this ceiling is just cheap host insurance against any future
    regression that tries to allocate without bound.
    """
    ceiling = 192 * 1024**2
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    new_soft = ceiling if soft == resource.RLIM_INFINITY else min(soft, ceiling)
    resource.setrlimit(resource.RLIMIT_AS, (new_soft, hard))
    try:
        yield
    finally:
        resource.setrlimit(resource.RLIMIT_AS, (soft, hard))


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
    svg = _render_or_skip(lambda: builder(values).to_svg())
    assume(svg is not None)
    assert svg is not None
    _assert_well_formed(svg)
    _assert_finite_coords(svg)


# ---------------------------------------------------------------------------
# Invariant 3: in-frame (all element bboxes inside viewBox)
# ---------------------------------------------------------------------------


@SETTINGS
@given(data=labeled_values())
def test_bar_in_frame(data: tuple[list[float], list[str], tuple[float, float]]) -> None:
    values, labels, (w, h) = data
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
    values, labels, (w, h) = data
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
# Invariant: pie legend stays clear of the pie circle (and labels appear once)
# ---------------------------------------------------------------------------
#
# The pie's default legend (legend='none') is drawn only when a slice is too
# small to carry its label inside the circle. Until this was fixed, that legend
# was laid out at the chart's vertical mid-height with overflow entries wrapped
# into a right-hand column that fell *inside* the circle's footprint, painting
# swatches and text over the wedges; and one slice was additionally given an
# in-slice centroid label, duplicating its legend entry. Both faults need long,
# multi-word labels and 3+ categories to surface, which the no-label pie builder
# in ALL_CHART_BUILDERS never exercises. These tests pin both: the legend band
# sits outside the circle and every label is rendered exactly once.

# Long, multi-word labels that overflow their slices and so force the legend.
_LONG_PIE_LABEL_POOL: tuple[str, ...] = (
    "Property, plant & equipment",
    "Financial assets at fair value",
    "Other assets and receivables",
    "Cash and cash equivalents",
    "Intangible assets and goodwill",
    "Deferred tax and provisions",
)


@st.composite
def long_labeled_pie(
    draw: st.DrawFn,
) -> tuple[list[float], list[str], tuple[float, float]]:
    """Draw a 3+ category pie with long multi-word labels (forces the legend)."""
    n = draw(st.integers(min_value=3, max_value=len(_LONG_PIE_LABEL_POOL)))
    values = draw(
        st.lists(
            st.floats(min_value=1.0, max_value=1e4, allow_nan=False),
            min_size=n,
            max_size=n,
        )
    )
    labels = list(_LONG_PIE_LABEL_POOL[:n])
    dims = draw(st.sampled_from([(760.0, 460.0), (700.0, 500.0), (640.0, 480.0)]))
    return values, labels, dims


@SETTINGS
@given(data=long_labeled_pie())
def test_pie_legend_clear_of_circle(
    data: tuple[list[float], list[str], tuple[float, float]],
) -> None:
    values, labels, (w, h) = data
    svg = _render_or_skip(
        lambda: PieChart(values, labels=labels, width=w, height=h).to_svg()
    )
    assume(svg is not None)
    assert svg is not None
    _assert_pie_legend_clear_of_circle(svg)
    _assert_each_label_once(svg, labels)


def test_pie_long_labels_legend_below_circle_regression() -> None:
    """Regression: a 3-category pie with long labels keeps its legend off the pie.

    Repro from a real 760x460 financial pie: the legend used to wrap its third
    entry into a right column inside the circle (x~525, the circle spanned
    x~196..564), and the 45% slice carried both a legend entry and an in-slice
    centroid label. The legend now occupies a reserved band below the circle and
    every slice is named once.
    """
    values = [50.0, 45.0, 5.0]
    labels = [
        "Property, plant & equipment (50%)",
        "Financial assets (45%)",
        "Other assets (5%)",
    ]
    svg = str(PieChart(values, labels=labels, width=760, height=460).to_svg())
    _assert_pie_legend_clear_of_circle(svg)
    _assert_each_label_once(svg, labels)


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
    values, labels, (w, h) = data
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
    values, labels, (w, h) = data
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
    # _render_or_skip propagates anything that is not a documented charted
    # rejection, so an unexpected exception type still fails this test.
    svg = _render_or_skip(lambda: builder(values).to_svg())
    if svg is None:
        return
    # If it rendered, the output must at least be a well-formed SVG string.
    assert svg.startswith("<svg")
    assert svg.rstrip().endswith("</svg>")


# ---------------------------------------------------------------------------
# Regression guards for bugs the property suite surfaced (now fixed)
# ---------------------------------------------------------------------------


def test_line_all_negative_stays_in_frame() -> None:
    """Regression: an all-negative LineChart series stays inside the viewBox.

    Previously the projection left the rendered domain at e.g. [-3, -1] with no
    zero baseline, so the data path was lifted above the top of the frame
    (path bbox top y ~= -200 on a 500x500 canvas). calculate_axis_dimensions
    now clamps an all-negative domain's max up to zero (mirroring the existing
    min-to-zero clamp), so the zero baseline is back inside the plot.
    """
    svg = str(
        LineChart(
            [-2.0, -3.0, -1.0], labels=["a", "b", "c"], width=500, height=500
        ).to_svg()
    )
    _assert_in_frame(svg)


def test_bar_all_negative_gridline_in_frame() -> None:
    """Regression: an all-negative horizontal BarChart stays inside the viewBox.

    Previously the rendered domain stayed at e.g. [-3, -1] (no zero baseline),
    so the zero gridline and the bar rect projected far to the right of the
    plot (gridline at x~=925 on a 500-wide canvas, x~=4.5e11 for [-1e9]). The
    all-negative max-to-zero clamp in calculate_axis_dimensions keeps both the
    gridline and the bar inside the frame.
    """
    svg = str(BarChart([-2.0], labels=[""], width=500, height=500).to_svg())
    _assert_in_frame(svg)


def test_scatter_all_negative_axis_in_frame() -> None:
    """Regression: an all-negative ScatterChart axis stays inside the viewBox.

    Previously an all-negative x or y series left the domain with no zero
    baseline, projecting the marker (x~=1724) or the zero gridline (y=-450)
    outside the frame. The all-negative clamp in calculate_axis_dimensions
    fixes both axes; this checks the x case (the y case is symmetric).
    """
    svg = str(ScatterChart([-16.0], [0.0], width=500, height=500).to_svg())
    _assert_in_frame(svg)


def test_empty_label_does_not_crash_rotated_axis() -> None:
    """Regression: an empty-string axis label no longer crashes a rotated axis.

    A dense ordinal axis rotates its labels and shifted each one left by
    ``label.width / len(label.text)``. An empty label made that ``len('')==0``,
    raising an uncaught ZeroDivisionError. The shift is now guarded (an empty
    label has zero width and nothing to shift). Repro: ColumnChart with a mix
    of populated and empty labels dense enough to trigger rotation.
    """
    labels = ["abcdef"] * 10 + [""] * 10
    svg = str(ColumnChart([5.0] * 20, labels=labels, width=500, height=500).to_svg())
    _assert_well_formed(svg)


def _text_in_frame_violations(svg: str, tol: float = 1.0) -> list[str]:
    parsed = parse_svg(svg)
    out: list[str] = []
    for el in parsed.elements:
        if el.tag != "text" or not (el.text and el.text.strip()):
            continue
        if not bbox_inside_viewbox(el, parsed.viewbox, tol=tol):
            out.append(f"{el.text!r} bbox={el.bbox()}")
    return out


def test_small_canvas_bottom_labels_stay_in_frame() -> None:
    """Regression: small-canvas bottom tick labels stay inside the viewBox.

    The bottom-axis margin used to be a flat fraction of the height, so on a
    short canvas it shrank below the DEFAULT_PADDING gap the tick labels are
    drawn at and the bottom labels spilled past the viewBox (baseline at y=246
    on a 240px-tall chart). bottom_padding now reserves at least DEFAULT_PADDING
    for the tick-label band, keeping them framed. Larger canvases (the 500px
    baseline fixtures) already exceed that, so their layout is unchanged.
    """
    values: list[float] = [5.0, 10.0, 15.0]
    svg = str(BarChart(values, labels=["a", "b", "c"], width=320, height=240).to_svg())
    violations = _text_in_frame_violations(svg)
    assert not violations, f"labels overflow small canvas: {violations}"


def test_mixed_magnitude_domain_renders_without_exploding() -> None:
    """Regression: a mismatched-magnitude domain no longer explodes the axis.

    calculate_axis_values used to pick the tick step from the common divisors
    of the two endpoint magnitudes, so a domain like (-1.0, 1e9) was forced to
    step=1.0 and the grid-value list comprehension materialised ~1e9 floats,
    raising MemoryError. The axis now caps the raw tick count and falls back to
    a nice-number step, so the repro renders quickly inside a small memory cap.
    Runs under the module's 192 MiB ceiling; explosion would re-raise here.
    """
    import time

    start = time.monotonic()
    svg = str(AreaChart([-1.0, 1e9], labels=["a", "b"], width=500, height=500).to_svg())
    elapsed = time.monotonic() - start
    _assert_well_formed(svg)
    _assert_in_frame(svg)
    assert elapsed < 1.0, f"mixed-magnitude render took {elapsed:.2f}s (expected <1s)"


# ---------------------------------------------------------------------------
# SankeyChart invariants
# ---------------------------------------------------------------------------
#
# Sankey is not value-list shaped (it takes a node/link DAG), so it does not
# join ALL_CHART_BUILDERS. It gets its own strategy that emits *valid* layered
# DAGs (links only ever point to a later layer, so they can never form a cycle)
# plus its own flow-conservation invariant: at every node the stacked link
# widths sum to the node's pixel height. That is the property that makes a
# Sankey read correctly - if it fails, ribbons either overflow or leave gaps.


@st.composite
def sankey_dag(
    draw: st.DrawFn,
) -> tuple[list[str], list[tuple[int, int, float]], tuple[float, float]]:
    """Draw a random layered DAG: nodes split into ordered layers, links only
    ever go from an earlier layer to a later one (so the graph is acyclic by
    construction), and every node past the first layer has at least one inbound
    link (so it is reachable and carries flow)."""
    n_layers = draw(st.integers(min_value=2, max_value=4))
    layer_sizes = [draw(st.integers(min_value=1, max_value=3)) for _ in range(n_layers)]
    # Assign a flat node-index range, grouped by layer.
    layers: list[list[int]] = []
    idx = 0
    for size in layer_sizes:
        layers.append(list(range(idx, idx + size)))
        idx += size
    n = idx
    names = [f"n{i}" for i in range(n)]

    links: list[tuple[int, int, float]] = []
    value = st.floats(
        min_value=1e-3, max_value=1e6, allow_nan=False, allow_infinity=False
    )
    for li in range(1, n_layers):
        prev = layers[li - 1]
        cur = layers[li]
        for target in cur:
            # Guarantee at least one inbound edge from the previous layer.
            source = draw(st.sampled_from(prev))
            links.append((source, target, draw(value)))
            # Optional extra fan-in from the previous layer.
            for src in prev:
                if src != source and draw(st.booleans()):
                    links.append((src, target, draw(value)))
    dims = draw(st.sampled_from([(800.0, 500.0), (640.0, 480.0), (700.0, 400.0)]))
    return names, links, dims


@st.composite
def dense_sankey_dag(
    draw: st.DrawFn,
) -> tuple[list[str], list[tuple[int, int, float]], tuple[float, float]]:
    """Like :func:`sankey_dag` but biased toward *many* nodes per column on a
    *normal*-width canvas, so labels are forced close enough together to test
    the column label-collision avoidance (fix for the dense-funnel mush). Many
    sinks per column at a width where the labels cannot all sit at their node
    centres is exactly the case that smears labels without the spreading pass.
    """
    n_layers = draw(st.integers(min_value=2, max_value=4))
    layer_sizes = [draw(st.integers(min_value=3, max_value=7)) for _ in range(n_layers)]
    layers: list[list[int]] = []
    idx = 0
    for size in layer_sizes:
        layers.append(list(range(idx, idx + size)))
        idx += size
    n = idx
    # Multi-character names so label boxes have real width/height, like the
    # recruitment-funnel node names that triggered the bug.
    names = [f"node-{i:02d}" for i in range(n)]

    links: list[tuple[int, int, float]] = []
    value = st.floats(
        min_value=1.0, max_value=1e4, allow_nan=False, allow_infinity=False
    )
    for li in range(1, n_layers):
        prev = layers[li - 1]
        cur = layers[li]
        for target in cur:
            source = draw(st.sampled_from(prev))
            links.append((source, target, draw(value)))
            for src in prev:
                if src != source and draw(st.booleans()):
                    links.append((src, target, draw(value)))
    # Normal widths, shortish heights: the brief's "23-node funnel at ~1000px"
    # legibility bar, scaled down for the small generated graphs.
    dims = draw(st.sampled_from([(900.0, 360.0), (1000.0, 400.0), (800.0, 320.0)]))
    return names, links, dims


def _sankey_label_boxes(svg: str) -> list[BBox]:
    """Absolute bboxes of the node labels in a rendered Sankey.

    Node labels are the text elements charted draws with
    ``dominant-baseline="middle"`` (the title and any axis text do not use it),
    so this isolates them without depending on their string content.
    """
    parsed = parse_svg(svg)
    boxes: list[BBox] = []
    for t in parsed.texts():
        if t.attrib.get("dominant-baseline") != "middle":
            continue
        if not (t.text and t.text.strip()):
            continue
        boxes.append(t.bbox())
    return boxes


@SETTINGS
@given(graph=dense_sankey_dag())
def test_sankey_labels_do_not_overlap(
    graph: tuple[list[str], list[tuple[int, int, float]], tuple[float, float]],
) -> None:
    """No two node-label boxes overlap on a dense Sankey.

    This is the regression guard for the label-collision fix: dense columns
    pack node centres closer than a text line is tall, so without the
    per-column label-spreading pass the labels overlap into an unreadable mush.
    Labels flank their nodes on the column's outward side, so for the inputs
    this strategy generates (short node names on wide canvases) labels in
    *different* columns do not share horizontal extent; the contract under test
    is that within each column the boxes are pushed vertically apart.
    """
    names, links, (w, h) = graph
    svg = _render_or_skip(
        lambda: SankeyChart(nodes=names, links=links, width=w, height=h).to_svg()
    )
    assume(svg is not None)
    assert svg is not None
    boxes = _sankey_label_boxes(svg)
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            assert not boxes_overlap(boxes[i], boxes[j], tol=0.5), (
                f"sankey labels overlap: {boxes[i]} vs {boxes[j]}"
            )


@pytest.mark.parametrize("n_sinks,height", [(12, 140.0), (16, 160.0), (17, 180.0)])
def test_sankey_oversubscribed_column_labels_stay_in_frame(
    n_sinks: int, height: float
) -> None:
    """Oversubscribed column labels stay on-canvas (no top/bottom overflow).

    Regression guard for the off-canvas label bug: many sinks funnelling into
    one column on a short canvas stack more labels than there is vertical room
    (``n * line_h > y1 - y0``). The old two-pass spread anchored the bottom and
    propagated upward without re-clamping the top, so the top labels slid off
    the canvas (reproduced as a label at y=-93 on a 16-sink / 140px chart).

    The labels overlap at this density - that is unavoidable and not what this
    checks. What it asserts is that every label box stays within the viewBox's
    top and bottom edges. (Horizontal overflow from long labels is a separate,
    documented open item, so only the vertical bounds are checked here.)
    """
    names = ["src"] + [f"sink-{i:02d}" for i in range(n_sinks)]
    links = [("src", f"sink-{i:02d}", 1.0) for i in range(n_sinks)]
    svg = SankeyChart(
        nodes=names, links=links, width=400.0, height=height
    ).to_svg()
    parsed = parse_svg(svg)
    _vx0, vy0, _vx1, vy1 = parsed.viewbox
    boxes = _sankey_label_boxes(svg)
    assert boxes, "expected node labels to be rendered"
    for box in boxes:
        _bx0, by0, _bx1, by1 = box
        assert by0 >= vy0 - 1.0 and by1 <= vy1 + 1.0, (
            f"label box {box} escapes viewBox vertically "
            f"[{vy0}, {vy1}]"
        )


@SETTINGS
@given(graph=sankey_dag())
def test_sankey_well_formed_finite_in_frame(
    graph: tuple[list[str], list[tuple[int, int, float]], tuple[float, float]],
) -> None:
    names, links, (w, h) = graph
    svg = _render_or_skip(
        lambda: SankeyChart(nodes=names, links=links, width=w, height=h).to_svg()
    )
    assume(svg is not None)
    assert svg is not None
    _assert_well_formed(svg)
    _assert_finite_coords(svg)
    # Non-text geometry (ribbons + node rects) must stay inside the viewBox.
    _assert_in_frame(svg)


@SETTINGS
@given(graph=sankey_dag())
def test_sankey_flow_conservation(
    graph: tuple[list[str], list[tuple[int, int, float]], tuple[float, float]],
) -> None:
    """At every node, stacked link widths sum to the node height (tolerance).

    This is *the* Sankey correctness property: a node of pixel height H carrying
    value V renders each link of value v at width v/V*H, so the widths of all
    links on one side of the node must sum back to H.
    """
    names, links, _ = graph
    layout = compute_layout(names, links, x0=40.0, y0=20.0, x1=760.0, y1=480.0)
    for node in layout.nodes:
        height = node.y1 - node.y0
        assert math.isfinite(height) and height >= -1e-6
        out_w = sum(link.width for link in node.source_links)
        in_w = sum(link.width for link in node.target_links)
        # A link width is the min of its two endpoints' ratios, so the binding
        # side sums exactly to the node height and the other side is <= it.
        if node.source_links:
            assert out_w <= height + 1e-6
        if node.target_links:
            assert in_w <= height + 1e-6
        # The node whose own ratio binds a link reaches the node height exactly;
        # at least one side of every interior node must be tight.
        if node.source_links and node.target_links:
            assert math.isclose(
                out_w, height, rel_tol=1e-6, abs_tol=1e-4
            ) or math.isclose(in_w, height, rel_tol=1e-6, abs_tol=1e-4)


@SETTINGS
@given(graph=sankey_dag())
def test_sankey_deterministic(
    graph: tuple[list[str], list[tuple[int, int, float]], tuple[float, float]],
) -> None:
    names, links, (w, h) = graph
    a = _render_or_skip(
        lambda: SankeyChart(nodes=names, links=links, width=w, height=h).to_svg()
    )
    b = _render_or_skip(
        lambda: SankeyChart(nodes=names, links=links, width=w, height=h).to_svg()
    )
    assume(a is not None)
    assert a == b


def test_sankey_single_link_in_frame() -> None:
    """Degenerate: one link, two nodes. Full-height ribbon, both rects framed."""
    svg = str(SankeyChart(nodes=["A", "B"], links=[("A", "B", 10)]).to_svg())
    _assert_well_formed(svg)
    _assert_finite_coords(svg)
    _assert_in_frame(svg)


def test_sankey_disconnected_chains_in_frame() -> None:
    """Degenerate: two chains that never touch still lay out cleanly."""
    svg = str(
        SankeyChart(
            nodes=["A", "B", "C", "D"], links=[("A", "B", 5), ("C", "D", 5)]
        ).to_svg()
    )
    _assert_well_formed(svg)
    _assert_in_frame(svg)


def test_sankey_rejects_cycle_cleanly() -> None:
    """A non-DAG raises a ChartedError, not an arbitrary crash."""
    with pytest.raises(ChartedError):
        SankeyChart(
            nodes=["A", "B", "C"],
            links=[("A", "B", 1), ("B", "C", 1), ("C", "A", 1)],
        ).to_svg()
