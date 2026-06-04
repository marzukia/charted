"""Tests for issue #67: colourblind-safe outlines, pattern fills, dash cycles.

Three redundant, colour-independent channels are added:

- a mandatory 1px contrasting outline on filled shapes in the high-contrast
  theme (columns, bars, pie/polar wedges, bubbles, box bodies),
- opt-in per-category hatch/pattern fills,
- an opt-in per-series dash cycle for line charts.

All three default to off so existing renders stay unchanged.
"""

from charted.charts.bar import BarChart
from charted.charts.box import BoxPlot
from charted.charts.bubble import BubbleChart
from charted.charts.column import ColumnChart
from charted.charts.line import LineChart
from charted.charts.pie import PieChart
from charted.charts.polar_area import PolarAreaChart
from charted.themes.core import Theme

HIGH_CONTRAST = Theme.from_preset("high-contrast")


# --- Theme token -----------------------------------------------------------


def test_high_contrast_theme_configures_shape_outline():
    stroke, width = HIGH_CONTRAST.filled_shape_outline
    assert stroke == "#000000"
    assert width == 1.0


def test_default_and_light_dark_have_no_shape_outline():
    for name in ("light", "dark"):
        stroke, _ = Theme.from_preset(name).filled_shape_outline
        assert stroke is None
    assert Theme().filled_shape_outline[0] is None


def test_invalid_shape_outline_color_rejected():
    import pytest

    with pytest.raises(ValueError):
        Theme(shape_outline_color="not-a-color")


# --- Outlines in high-contrast ---------------------------------------------


def test_column_high_contrast_outlines_bars():
    hc = ColumnChart(
        data=[[3, 5, 2], [4, 1, 6]],
        labels=["a", "b", "c"],
        series_names=["x", "y"],
        theme=HIGH_CONTRAST,
    )
    plain = ColumnChart(data=[[3, 5, 2], [4, 1, 6]], labels=["a", "b", "c"])
    assert 'stroke="#000000"' in hc.svg
    # The default theme leaves bar paths unstroked.
    assert 'stroke="#000000"' not in plain.representation.html


def test_pie_high_contrast_outlines_wedges():
    hc = PieChart(data=[30, 20, 50], labels=["a", "b", "c"], theme=HIGH_CONTRAST)
    plain = PieChart(data=[30, 20, 50], labels=["a", "b", "c"])
    assert 'stroke="#000000"' in hc.representation.html
    assert 'stroke="#000000"' not in plain.representation.html


def test_bar_polar_box_bubble_high_contrast_outlines():
    bar = BarChart(data=[3, 5, 2], labels=["a", "b", "c"], theme=HIGH_CONTRAST)
    polar = PolarAreaChart(data=[10, 20, 30], labels=["a", "b", "c"], theme=HIGH_CONTRAST)
    box = BoxPlot(data=[[1, 2, 3, 4, 5], [2, 4, 6, 8, 10]], theme=HIGH_CONTRAST)
    bubble = BubbleChart(
        x_data=[1, 2, 3], y_data=[4, 5, 6], sizes=[10, 20, 30], theme=HIGH_CONTRAST
    )
    for chart in (bar, polar, box, bubble):
        assert 'stroke="#000000"' in chart.representation.html


# --- Pattern fills (opt-in) ------------------------------------------------


def test_patterns_off_by_default():
    plain = ColumnChart(data=[3, 5, 2], labels=["a", "b", "c"])
    assert "<pattern" not in plain.svg
    assert "url(#chart-pattern" not in plain.svg


def test_column_category_patterns_emits_defs_and_refs():
    patterned = ColumnChart(
        data=[[3, 5, 2], [4, 1, 6]],
        labels=["a", "b", "c"],
        series_names=["x", "y"],
        category_patterns=True,
    )
    svg = patterned.svg
    assert "<pattern" in svg
    assert "url(#chart-pattern" in svg
    # One pattern def per category colour the chart resolved.
    assert svg.count("<pattern ") >= 2


def test_pie_category_patterns():
    patterned = PieChart(data=[30, 20, 50], labels=["a", "b", "c"], category_patterns=True)
    assert "<pattern" in patterned.svg
    assert "url(#chart-pattern" in patterned.svg


def test_custom_pattern_list_is_respected():
    chart = ColumnChart(
        data=[5, 3, 8, 2],
        labels=["a", "b", "c", "d"],
        category_patterns=["dots"],
    )
    # A single-pattern cycle still emits one def per colour, all "dots"
    # (drawn with circles).
    assert "<pattern" in chart.svg
    assert "<circle" in chart.svg


# --- Line dash cycle (opt-in) ----------------------------------------------


def test_line_dash_cycle_off_by_default():
    plain = LineChart(data=[[1, 2, 3], [3, 2, 1]])
    # The line series group itself carries no dash (grid lines are separate).
    assert "stroke-dasharray" not in plain.representation.html


def test_line_dash_cycle_distinguishes_series():
    chart = LineChart(
        data=[[1, 2, 3], [3, 2, 1], [2, 2, 2]],
        series_names=["a", "b", "c"],
        dash_cycle=True,
    )
    # First series is solid (leads the cycle), later series get dash patterns.
    assert "stroke-dasharray" in chart.representation.html


def test_line_explicit_dasharray_wins_over_cycle():
    chart = LineChart(
        data=[[1, 2, 3], [3, 2, 1]],
        series_styles=[{"stroke_dasharray": "9,9"}, None],
        dash_cycle=True,
    )
    assert "9,9" in chart.representation.html
