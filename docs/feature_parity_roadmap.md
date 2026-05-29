# Feature parity roadmap

A scope-and-sequencing doc for closing the legitimate feature gaps charted has
against Chart.js and D3, written as a test-driven plan. It is a roadmap, not the
implementation. Each feature lists the failing tests to write first (Red), the
minimal code to make them pass (Green), and what "done" means (Acceptance).

## Scope and non-goals

charted's niche is static, zero-dependency, publication-quality SVG/PNG from
Python, a CLI, SQL via DuckDB, or an LLM via MCP. Everything here has to fit
that niche: no browser runtime, no required third-party dependency in core, and
no break to the one-call API.

In scope, ordered by value:

1. Log and time scales (currently linear only)
2. A mixed chart type (bar + line on shared axes)
3. Curve interpolation for line and area (step, basis/cardinal spline)
4. Bubble and polar area chart types
5. A small annotation primitive (generalize the reference-line code into boxes, labels, line segments)
6. Opt-in interactivity in `to_html()` only (SVG `<title>` tooltips as the zero-JS baseline)
7. Continuous sequential/diverging color interpolation

Explicitly out of scope (rejected in the gap analysis, do not build): a plugin
architecture, Canvas/WebGL, default animations, full responsive resize, D3's
selection/data-binding model, force simulation, geo projections.

## How the codebase is laid out (the parts that change)

- `charted/charts/chart.py` is the base `Chart(Svg)`. It owns construction, the
  `reproject` plumbing through `XAxis`/`YAxis`, `to_html()`, `to_config()`,
  `describe()`, reference-line rendering (`_render_reference_lines`), and the
  abstract `representation` property each chart subclass implements.
- `charted/charts/axes.py` holds `Axis`, `XAxis`, `YAxis`. The linear mapping
  lives in the classmethod `Axis._reproject` and the tick math in
  `calculate_axis_values` / `calculate_axis_dimensions`. This is the only place
  value-to-pixel mapping happens, so scales hook in here.
- Chart subclasses (`line.py`, `area.py`, `scatter.py`, `pie.py`, `column.py`,
  `bar.py`, etc.) each implement `representation`. Line/area delegate to
  `charted/utils/line_renderer.py`.
- `charted/chart_config.py` holds the `*Config` dataclasses (`LineChartConfig`,
  `ScatterChartConfig`, `PieChartConfig`, ...). New per-chart options get a
  field here.
- `charted/themes/core.py` holds the `Theme` dataclass, `NAMED_PALETTES`, and
  `resolve_palette`. `charted/utils/colors.py` holds color parsing/interpolation
  primitives (`_parse_color_to_rgb`, `hex_to_rgb`, `rgb_to_hex`,
  `calculate_contrast_ratio`).
- Surfaces that must stay in sync when a new chart type lands: the exports in
  `charted/charts/__init__.py` (`__all__` and `_CHART_CLASSES`), `charted/__init__.py`,
  and the MCP server maps `CHART_TYPE_MAP` / `CHART_DESCRIPTIONS` in
  `mcp_server/tools.py`.
- Tests live under `tests/charts/` (per-chart), `tests/themes/`, `tests/utils/`,
  `tests/accessibility/`, `tests/properties/` (hypothesis-style), `tests/visual/`
  (SVG-structure regression), `tests/html/`, and `tests/cli/`. Shared fixtures
  are in `tests/conftest.py`; assertion helpers in `tests/helpers/svg_assertions.py`.

---

## 1. Log and time scales

Highest value. Today the only mapping is the linear `Axis._reproject`
(`(value - min) / (max - min) * length`) and the tick generation in
`calculate_axis_values`. A scale is two things: a value-to-pixel transform and a
tick generator. The cleanest fit is a small `Scale` abstraction that `XAxis`/`YAxis`
delegate to, with `LinearScale` as the existing behavior, plus `LogScale` and
`TimeScale`.

**Red** (write first, in a new `tests/charts/test_scales.py`):

- `test_linear_scale_matches_current_reproject` — a `LinearScale(min=0, max=100)`
  over length 400 maps 50 to 200.0; pins existing behavior before refactor.
- `test_log_scale_maps_decades` — a `LogScale(min=1, max=1000)` over length 300
  places 1, 10, 100, 1000 at evenly spaced pixel positions (0, 100, 200, 300);
  asserts the spacing between decade ticks is equal.
- `test_log_scale_rejects_nonpositive` — `LogScale(min=0, ...)` or data
  containing <= 0 raises `ValueError` (log undefined at/below zero).
- `test_log_scale_ticks_are_powers` — generated ticks for [1, 1000] are
  [1, 10, 100, 1000].
- `test_time_scale_maps_dates` — a `TimeScale` over
  `[date(2024,1,1), date(2024,12,31)]` maps the midpoint date to ~length/2;
  accepts `datetime`/`date` and ISO strings.
- `test_time_scale_nice_ticks` — a one-year span produces month-or-quarter
  boundary ticks (clean dates, not arbitrary epochs).
- In `tests/charts/test_line.py` / `test_scatter.py`:
  `test_line_chart_log_y_scale` and `test_scatter_log_x_scale` — passing
  `y_scale="log"` (or `x_scale="log"`) produces a chart whose SVG renders and
  whose y tick labels are decade values; `test_line_chart_time_x_axis` — passing
  date-typed `x_data` with `x_scale="time"` renders without error and labels are
  formatted dates.
- In `tests/properties/`: a hypothesis test that for any positive min/max and
  value in range, `LogScale.reproject` returns a value within [0, length] and is
  monotonic.

**Green:**

- Add `charted/charts/scales.py` with a `Scale` protocol/base exposing
  `reproject(value) -> float`, `reverse(pixel) -> float`, and `ticks() -> list`.
  Implement `LinearScale` (lift the current `_reproject` math), `LogScale`
  (`log10`-based, validate positivity), `TimeScale` (normalize date/datetime/ISO
  to epoch seconds, linear in that space, date-aware tick generation).
- In `axes.py`, have `XAxis`/`YAxis` hold a `scale` instance and delegate
  `reproject` / `reverse` / tick values to it. Keep `LinearScale` the default so
  existing behavior and all current tests stay green.
- Thread a `x_scale` / `y_scale` argument (string `"linear"|"log"|"time"` or a
  `Scale` instance) through `Chart.__init__` and the relevant subclass
  constructors (`LineChart`, `ScatterChart`, `AreaChart`, `ColumnChart`).
- Add `x_scale` / `y_scale` fields to the corresponding configs in
  `chart_config.py`.

**Acceptance:**

- `LineChart`, `ScatterChart`, `AreaChart`, `ColumnChart` accept `x_scale` /
  `y_scale`; default stays linear and is byte-for-byte unchanged (visual
  regression baselines untouched).
- Log axis tick labels render as decade values; time axis labels render as
  formatted dates; both respect the active theme's label color/font.
- `to_config()` round-trips the scale choice (serialized and replayable via
  `from_config()`).
- `describe()` reports the scale type per axis.
- Positivity and date-parsing errors raise clear `ValueError`s with messages.
- No new core dependency; date handling uses stdlib `datetime`.

**Effort:** large. **Dependencies:** none; this is the foundation and should
land first because the mixed chart (feature 2) wants a shared axis built on it.

---

## 2. Mixed chart type (bar + line on shared axes)

Each chart class is currently a single representation. A mixed chart composes a
column/bar representation and a line representation against one shared
coordinate system (shared x, optionally a secondary y).

**Red** (`tests/charts/test_combo.py`):

- `test_combo_renders_bars_and_line` — `ComboChart` with one bar series and one
  line series produces SVG containing both `<rect>` (or column path) and a line
  `<path>`; both present.
- `test_combo_shares_x_axis` — bar centers and line points line up on the same x
  tick positions for the same labels.
- `test_combo_secondary_y_axis` — when a series is assigned to a secondary y
  axis, a second set of y tick labels renders on the right and that series is
  scaled to its own range, not the primary range.
- `test_combo_legend_lists_all_series` — legend has one entry per series with the
  correct per-series color.
- `test_combo_describe` — `describe()` reports `series_count == 2` and each
  series' type.
- Sad path: `test_combo_requires_at_least_two_series` raises on a single series.

**Green:**

- Add `charted/charts/combo.py` with `ComboChart(Chart)`. Accept a list of
  series each tagged with a type (`"bar"|"column"|"line"|"area"`) and an optional
  `axis="primary"|"secondary"`. Reuse existing renderers: instantiate/borrow the
  column and line representation logic rather than reimplementing.
- Add optional secondary-axis support in `axes.py` (a second `YAxis` with its own
  `axis_dimension`) or a lightweight secondary `Scale`, rendered on the right.
- Add `ComboChartConfig` to `chart_config.py`.
- Register in `charts/__init__.py` (`__all__`, `_CHART_CLASSES`),
  `charted/__init__.py`, and add `"combo"` to `CHART_TYPE_MAP` /
  `CHART_DESCRIPTIONS` in `mcp_server/tools.py`.

**Acceptance:**

- A bar+line combo with shared x renders correctly; optional secondary y axis
  scales its series independently and labels on the right.
- Theming, legend, axis titles, and accessibility contrast checks all apply.
- Exposed via Python API, CLI (`charted create --type combo ...` accepts it), and
  MCP (`list_chart_types` includes it).
- `to_config()` / `from_config()` round-trip the per-series types and axis
  assignment.

**Effort:** large. **Dependencies:** secondary axis benefits from feature 1's
`Scale` abstraction; build after scales.

---

## 3. Curve interpolation for line and area

Lines are polylines today (`LineRenderer` emits straight `L` segments). Add a
`curve=` option that changes how consecutive points are joined: `"linear"`
(default), `"step"` (before/after), and a smooth spline (`"basis"` or
`"cardinal"`). This is a path-generation change, not a data change.

**Red** (`tests/charts/test_curve_interpolation.py`):

- `test_linear_curve_is_default_polyline` — default output uses `L` commands
  only; pins current behavior.
- `test_step_curve_emits_horizontal_then_vertical` — `curve="step"` produces a
  path whose segments are axis-aligned (only `H`/`V` or `L` along one axis at a
  time between points).
- `test_cardinal_curve_emits_cubic_beziers` — `curve="basis"`/`"cardinal"`
  produces a path containing `C` (cubic Bezier) commands and still starts/ends at
  the first/last data point.
- `test_curve_passes_through_endpoints` — for every curve type the path's first
  and last coordinates equal the first and last data points (cardinal must
  interpolate endpoints; basis may approximate, assert documented behavior).
- `test_area_curve_matches_line_curve` — `AreaChart(curve="cardinal")` fills
  under the same smoothed boundary the line would draw.
- Sad path: `test_invalid_curve_raises` — unknown curve name raises `ValueError`.
- A hypothesis property in `tests/properties/`: a curved path emits the same
  number of vertices as input points (no point dropped) for step and cardinal.

**Green:**

- Add a curve module (e.g. `charted/utils/curves.py`) with pure functions that
  take a list of `(x, y)` points and return an SVG path `d` string:
  `linear_path`, `step_path`, `cardinal_path`/`basis_path` (cardinal spline with a
  default tension).
- In `charted/utils/line_renderer.py`, branch on the chart's `curve` attribute
  when building the line path; reuse the same generated boundary for the area
  fill in `area.py`.
- Add `curve: str = "linear"` to `LineChartConfig` (and an area equivalent) in
  `chart_config.py`; thread it through `LineChart.__init__` / `AreaChart.__init__`.

**Acceptance:**

- `LineChart(..., curve="step"|"cardinal"|"basis")` and the area equivalent
  render valid SVG; default `"linear"` output is unchanged (baselines intact).
- Markers and data labels still sit on the original data points regardless of
  curve.
- `to_config()` round-trips `curve`.

**Effort:** medium. **Dependencies:** none; independent of scales. Can run in
parallel with feature 1.

---

## 4. Bubble and polar area chart types

Both are cheap given existing machinery. Bubble is a scatter where marker radius
encodes a third value. Polar area is a pie where every slice has the same angle
but radius encodes value.

**Red** (`tests/charts/test_bubble.py`, `tests/charts/test_polar_area.py`):

- `test_bubble_radius_encodes_third_dim` — `BubbleChart` with `sizes=[...]`
  renders `<circle>` elements whose `r` is monotonic in the size value (largest
  size -> largest radius).
- `test_bubble_radius_within_bounds` — all radii fall within a configured
  `[min_radius, max_radius]` range.
- `test_bubble_reuses_scatter_positioning` — point centers match what a
  `ScatterChart` with the same x/y would produce.
- `test_polar_area_equal_angles` — `PolarAreaChart` with N values produces N
  slices each spanning 360/N degrees.
- `test_polar_area_radius_encodes_value` — slice radius is monotonic in value;
  largest value -> outermost slice.
- Sad paths: negative sizes / negative polar values raise `ValueError`.

**Green:**

- `charted/charts/bubble.py`: `BubbleChart(ScatterChart)` adding a `sizes`
  argument and a size-to-radius scale (`min_radius`/`max_radius`), overriding only
  marker radius.
- `charted/charts/polar_area.py`: `PolarAreaChart(PieChart)` (or sharing pie's
  arc-path helper) with equal angular slices and a value-to-radius mapping.
- Add `BubbleChartConfig` / `PolarAreaChartConfig` to `chart_config.py`.
- Register both in `charts/__init__.py`, `charted/__init__.py`, and
  `CHART_TYPE_MAP` / `CHART_DESCRIPTIONS` in `mcp_server/tools.py`.

**Acceptance:**

- Bubble and polar area available via Python, CLI, and MCP; theming, legend, and
  accessibility checks apply.
- `auto()` chart-type inference (`charted/utils/data_input.py`) optionally
  recognizes a third numeric dimension as a bubble candidate (stretch).
- `to_config()` / `from_config()` round-trip both, including `sizes` and radius
  bounds.

**Effort:** medium. **Dependencies:** bubble benefits from but does not require
feature 1 (size scale can be linear initially). Build after scatter/pie are
understood; independent of features 1-3.

---

## 5. Annotation primitive

Today annotations are limited to horizontal/vertical reference lines
(`Chart._render_reference_lines`, driven by `h_lines` / `v_lines`) plus scatter
quadrant labels. Generalize this into a small annotation layer: line segments,
boxes (shaded value ranges), and point/text labels, positioned in data
coordinates and reprojected through the axes.

**Red** (`tests/charts/test_annotations.py`):

- `test_line_annotation_renders_segment` — a `LineAnnotation((x0,y0),(x1,y1))`
  draws a `<path>`/`<line>` between the reprojected data coordinates.
- `test_box_annotation_renders_rect` — a `BoxAnnotation(x_range, y_range)` draws a
  shaded `<rect>` covering the reprojected data range.
- `test_label_annotation_renders_text` — a `LabelAnnotation((x,y), "text")`
  renders `<text>` at the reprojected point.
- `test_existing_h_lines_still_work` — `h_lines=[...]` / `v_lines=[...]` keep
  producing the same dashed reference lines (back-compat pin).
- `test_h_lines_implemented_via_annotations` — internally the legacy reference
  lines are expressed as annotations (refactor check, optional).
- `test_annotations_clipped_to_plot` — annotations render inside the plot area
  group, not over the axes.

**Green:**

- Add `charted/charts/annotations.py` with small dataclasses:
  `LineAnnotation`, `BoxAnnotation`, `LabelAnnotation`, each with a
  `render(chart) -> Element` that reprojects its data coordinates via
  `chart.x_axis.reproject` / `chart.y_axis.reproject`.
- Add an `annotations: list[Annotation]` argument to `Chart.__init__`; render them
  in the same plot-area group as `_render_reference_lines`.
- Refactor `_render_reference_lines` to build `LineAnnotation`s from `h_lines` /
  `v_lines` so there's one code path (keep the old kwargs as sugar).

**Acceptance:**

- Charts accept `annotations=[...]`; line/box/label types render in data
  coordinates and respect theme colors.
- Legacy `h_lines` / `v_lines` behavior is byte-for-byte unchanged.
- `to_config()` round-trips annotations.

**Effort:** medium. **Dependencies:** annotations reproject through the axes, so
once feature 1 lands they automatically work on log/time axes; no hard ordering,
but landing after scales avoids reworking coordinate handling.

---

## 6. Opt-in interactivity in `to_html()` (SVG `<title>` tooltips)

Keep file output (`to_svg()`, `save()`) inert. The zero-JS baseline is native
SVG `<title>` elements: hovering a data element shows the browser's built-in
tooltip, no script. `to_html()` gains an opt-in flag to include them.

**Red** (`tests/html/test_tooltips.py`, plus `tests/html/test_formatter.py`):

- `test_to_svg_has_no_titles_by_default` — plain `to_svg()` output contains no
  `<title>` elements (file output stays inert).
- `test_to_html_tooltips_opt_in` — `to_html(tooltips=True)` injects `<title>`
  children inside data marks (`<rect>`/`<circle>`/path groups) with the
  series/value text; `to_html()` without the flag does not.
- `test_tooltip_text_matches_data` — tooltip text for a point equals its label
  and value (e.g. `"Feb: 59"`).
- `test_tooltips_no_javascript` — the emitted HTML contains no `<script>` tag
  (zero-JS guarantee).
- Accessibility: `test_tooltip_titles_are_accessible` in
  `tests/accessibility/` — `<title>` provides an accessible name for the mark.

**Green:**

- Add a `Title` element to `charted/html/element.py` (renders `<title>...</title>`).
- Give chart representations an opt-in hook to attach a `<title>` child to each
  data mark carrying `"<series>: <value>"` (or label/value), gated so it only
  fires when requested.
- Add a `tooltips: bool = False` parameter to `Chart.to_html()` (and thread an
  internal flag the representation reads). Keep `to_svg()`/`save()` output free of
  titles.
- Update `generate_html_wrapper` in `charted/utils/rendering.py` if the SVG needs
  regenerating with titles for the HTML path.

**Acceptance:**

- `to_html(tooltips=True)` produces hoverable native tooltips with no JavaScript;
  default `to_html()` and all file output stay inert and unchanged.
- Tooltip text is correct per data point and accessible.

**Effort:** medium. **Dependencies:** none functionally, but tooltip text reads
nicer once scales/time formatting exist; can build independently.

---

## 7. Continuous sequential/diverging color interpolation

charted already ships discrete palettes (viridis, inferno, ocean, ...). Expose
continuous interpolation so a value in [0,1] (or a domain) maps to a color along
a gradient. Most useful for heatmaps and bubble fills.

**Red** (`tests/themes/test_color_interpolation.py`, plus `tests/properties/`):

- `test_interpolate_sequential_endpoints` — `interpolate("viridis", 0.0)` equals
  the palette's first color and `interpolate("viridis", 1.0)` equals the last.
- `test_interpolate_midpoint_between_stops` — `interpolate(["#000000","#ffffff"], 0.5)`
  returns mid-gray (`#7f7f7f`-ish within tolerance).
- `test_diverging_scale_center` — a diverging scale built from
  (low, mid, high) returns `mid` at the domain center and the endpoints at the
  extremes.
- `test_interpolate_clamps_out_of_range` — t < 0 clamps to the first color, t > 1
  to the last.
- A hypothesis property: for any t in [0,1] the result is a valid hex color
  parseable by `_parse_color_to_rgb`.
- Integration `tests/charts/test_heatmap.py::test_heatmap_continuous_color` — a
  heatmap built with a continuous scale colors cells by value along the gradient
  (min value -> first stop, max -> last stop).

**Green:**

- Add interpolation helpers to `charted/utils/colors.py` (reuse
  `_parse_color_to_rgb` / `rgb_to_hex`): `interpolate_color(a, b, t)` and
  `interpolate_palette(palette_or_list, t)`; add a small `ColorScale` /
  `diverging_scale(low, mid, high, domain)` in `themes/core.py` next to
  `resolve_palette`.
- Let `HeatmapChart` (and optionally `BubbleChart`) accept a continuous color
  scale instead of only discrete buckets.

**Acceptance:**

- `interpolate_palette("viridis", t)` returns smooth intermediate colors;
  diverging scales center correctly.
- Heatmap can color by a continuous scale; existing discrete behavior unchanged.
- Output still passes the WCAG-AA contrast check where contrast applies.

**Effort:** small-to-medium. **Dependencies:** pairs naturally with feature 4
(bubble fills) and improves heatmaps; independent of scales.

---

## Suggested sequence

1. **Scales** (feature 1) first; it is the foundation the mixed chart and
   annotation reprojection lean on.
2. **Curve interpolation** (3) and **color interpolation** (7) in parallel; both
   are self-contained and low-risk.
3. **Bubble + polar area** (4), then **mixed chart** (2) once scales and a
   secondary axis exist.
4. **Annotations** (5) after scales so they reproject through any axis type.
5. **Tooltips** (6) any time; it only touches the HTML output path.

Every feature keeps the default output byte-for-byte unchanged so the visual
regression baselines in `tests/visual/` stay valid, and every new chart type must
be wired into the Python exports, the CLI, and the MCP `CHART_TYPE_MAP` before it
counts as done.
