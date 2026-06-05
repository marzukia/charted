"""Tests for the opt-in value-label system (issue #59).

Covers the number/percent/currency formatter plus wiring into bar, column,
pie, scatter, bubble, histogram, and box charts. Default-off behaviour is
verified so existing renders are unchanged.
"""

from __future__ import annotations

from charted import (
    BarChart,
    BoxPlot,
    BubbleChart,
    ColumnChart,
    Histogram,
    PieChart,
    ScatterChart,
)
from charted.utils.value_format import format_value


class TestFormatValue:
    def test_number_grouping_and_trim(self):
        assert format_value(1234.0, "number") == "1,234"
        assert format_value(1234.5, "number") == "1,234.5"

    def test_percent_scales_by_default(self):
        assert format_value(0.25, "percent") == "25%"
        assert format_value(25, "percent", percent_scale=False) == "25%"

    def test_currency_symbol_and_decimals(self):
        assert format_value(1234.5, "currency", decimals=2) == "$1,234.50"
        assert format_value(50, "currency", currency_symbol="€") == "€50"

    def test_negative_sign_outside_symbol(self):
        assert format_value(-12.5, "currency") == "-$12.5"
        assert format_value(-0.1, "percent") == "-10%"

    def test_prefix_suffix(self):
        assert format_value(5, "number", prefix="~", suffix=" units") == "~5 units"

    def test_unknown_format_raises(self):
        import pytest

        with pytest.raises(ValueError):
            format_value(1, "binary")

    def test_extreme_magnitudes_use_scientific_notation(self):
        # Huge numbers (>= 1e6) collapse to a compact exponent.
        assert format_value(1_000_000_000, "number") == "1e9"
        assert format_value(999_999_999, "number") == "1e9"
        assert format_value(1_500_000_000, "number") == "1.5e9"
        assert format_value(1_000_000, "number") == "1e6"
        # Tiny non-zero decimals (< 1e-3) become sci-notation rather than 0.
        assert format_value(0.0002, "number") == "2e-4"
        assert format_value(0.00015, "number") == "1.5e-4"
        # Prefix/suffix still wrap the result.
        assert format_value(2e9, "number", prefix="~", suffix="x") == "~2e9x"

    def test_normal_range_unchanged_by_sci_notation(self):
        # Values between the thresholds keep grouped formatting unchanged.
        assert format_value(999_999, "number") == "999,999"
        assert format_value(0.001, "number") == "0"  # rounds at default precision
        assert format_value(0, "number") == "0"
        assert format_value(123_456, "number") == "123,456"


class TestValueLabelsWiring:
    def test_column_value_labels_appear(self):
        chart = ColumnChart(data=[10, 25, 40], value_labels="number")
        svg = chart.svg
        assert ">10<" in svg and ">25<" in svg and ">40<" in svg

    def test_column_off_by_default_unchanged(self):
        plain = ColumnChart(data=[10, 25, 40]).svg
        # No synthesized value text when value_labels is omitted.
        assert ">25<" not in plain

    def test_bar_currency_labels(self):
        chart = BarChart(data=[100, 250], value_labels="currency")
        svg = chart.svg
        assert "$100" in svg and "$250" in svg

    def test_pie_percent_labels(self):
        chart = PieChart(data=[25, 75], value_labels="percent")
        svg = chart.svg
        # 25 of 100 => 25%, shown inside the slice.
        assert "25%" in svg

    def test_scatter_number_labels(self):
        chart = ScatterChart(
            x_data=[1, 2, 3], y_data=[10, 20, 30], value_labels="number"
        )
        svg = chart.svg
        assert ">10<" in svg

    def test_bubble_inherits_value_labels(self):
        chart = BubbleChart(
            x_data=[1, 2],
            y_data=[5, 15],
            sizes=[3, 8],
            value_labels="number",
        )
        svg = chart.svg
        assert ">15<" in svg

    def test_histogram_value_labels(self):
        chart = Histogram(data=[1, 1, 2, 3, 3, 3], bins=3, value_labels="number")
        svg = chart.svg
        # The tallest bin (value 3 appears 3 times) shows a "3" count label.
        assert ">3<" in svg

    def test_box_median_label(self):
        chart = BoxPlot(data=[[1, 2, 3, 4, 5]], value_labels="number")
        svg = chart.svg
        # Median of 1..5 is 3.
        assert ">3<" in svg

    def test_dict_config_decimals(self):
        chart = ColumnChart(
            data=[10.5], value_labels={"format": "currency", "decimals": 2}
        )
        assert "$10.50" in chart.svg

    def test_collision_auto_hide(self):
        # Many near-equal values in a narrow chart force label collisions; the
        # auto-hide drops some so the rendered count is below the data count.
        data = [50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
        chart = ColumnChart(data=data, width=200, height=200, value_labels="number")
        rendered = chart.svg.count(">50<")
        assert 0 < rendered < len(data)


def _abs_text_coords(
    svg: str,
) -> tuple[tuple[float, float], list[tuple[str, float, float]]]:
    """Parse a rendered SVG and return (viewBox WH, [(text, abs_x, abs_y), ...]).

    Composes the full chain of ancestor ``transform`` attributes for every
    ``<text>`` element so the reported coordinate is the absolute viewBox
    position, matching how a browser clips inline SVG (cairosvg PNG export does
    not clip, so a PNG check alone would miss off-viewBox labels).
    """
    import math
    import re
    import xml.etree.ElementTree as ET

    ns = "{http://www.w3.org/2000/svg}"

    def mat_mul(
        m1: tuple[float, ...], m2: tuple[float, ...]
    ) -> tuple[float, float, float, float, float, float]:
        a1, b1, c1, d1, e1, f1 = m1
        a2, b2, c2, d2, e2, f2 = m2
        return (
            a1 * a2 + c1 * b2,
            b1 * a2 + d1 * b2,
            a1 * c2 + c1 * d2,
            b1 * c2 + d1 * d2,
            a1 * e2 + c1 * f2 + e1,
            b1 * e2 + d1 * f2 + f1,
        )

    def parse(t: str | None) -> tuple[float, float, float, float, float, float]:
        m: tuple[float, float, float, float, float, float] = (1, 0, 0, 1, 0, 0)
        if not t:
            return m
        for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", t):
            nums = [float(x) for x in re.split(r"[\s,]+", args.strip()) if x]
            if name == "translate":
                tx = nums[0]
                ty = nums[1] if len(nums) > 1 else 0.0
                m = mat_mul(m, (1, 0, 0, 1, tx, ty))
            elif name == "scale":
                sx = nums[0]
                sy = nums[1] if len(nums) > 1 else sx
                m = mat_mul(m, (sx, 0, 0, sy, 0, 0))
            elif name == "rotate":
                a = math.radians(nums[0])
                ca, sa = math.cos(a), math.sin(a)
                if len(nums) == 3:
                    cx, cy = nums[1], nums[2]
                    m = mat_mul(m, (1, 0, 0, 1, cx, cy))
                    m = mat_mul(m, (ca, sa, -sa, ca, 0, 0))
                    m = mat_mul(m, (1, 0, 0, 1, -cx, -cy))
                else:
                    m = mat_mul(m, (ca, sa, -sa, ca, 0, 0))
        return m

    root = ET.fromstring(svg)
    vb = root.get("viewBox") or "0 0 0 0"
    parts = [float(x) for x in re.split(r"[\s,]+", vb.strip())]
    wh = (parts[2], parts[3])
    out: list[tuple[str, float, float]] = []

    def walk(el: ET.Element, parent: tuple[float, ...]) -> None:
        cur = mat_mul(parent, parse(el.get("transform")))
        if el.tag.replace(ns, "") == "text":
            x = float(el.get("x", 0))
            y = float(el.get("y", 0))
            a, b, c, d, e, f = cur
            out.append(
                ("".join(el.itertext()).strip(), a * x + c * y + e, b * x + d * y + f)
            )
        for child in el:
            walk(child, cur)

    walk(root, (1, 0, 0, 1, 0, 0))
    return wh, out


class TestValueLabelPlacement:
    """Placement, clamping, and dark-theme contrast for value labels."""

    def _value_labels_inside_viewbox(self, chart) -> None:
        (w, h), texts = _abs_text_coords(chart.svg)
        for txt, ax, ay in texts:
            assert -0.5 <= ax <= w + 0.5, f"{txt!r} x={ax} outside [0,{w}]"
            assert -0.5 <= ay <= h + 0.5, f"{txt!r} y={ay} outside [0,{h}]"

    def test_negative_values_stay_in_viewbox(self):
        chart = ColumnChart(
            data=[-50, 100, -20, 80],
            labels=["A", "B", "C", "D"],
            value_labels="number",
            width=600,
            height=400,
        )
        self._value_labels_inside_viewbox(chart)

    def test_extreme_dynamic_range_stays_in_viewbox(self):
        chart = ColumnChart(
            data=[1, 1000, 5, 2],
            labels=["A", "B", "C", "D"],
            value_labels="number",
            width=600,
            height=400,
        )
        self._value_labels_inside_viewbox(chart)

    def test_label_sits_above_short_positive_bar(self):
        # A short bar leaves room above it, so its label goes OUTSIDE (above the
        # bar top), not jammed inside. Data labels carry the flip transform
        # ``scale(1,-1)`` which y-axis tick labels do not, so isolate them.
        import re

        chart = ColumnChart(
            data=[20, 100],
            labels=["short", "tall"],
            value_labels="number",
            width=600,
            height=400,
        )
        # Pull the data-label "20" element (the one with the scale(1,-1) flip).
        match = re.search(r"<text[^>]*scale\(1,-1\)[^>]*>20<", chart.svg)
        assert match is not None
        # Its tick-label twin sits at the value-20 gridline. The data label must
        # sit above the bar top, i.e. higher on screen (smaller absolute y) than
        # that gridline tick. Compare via absolute coords.
        (_w, _h), texts = _abs_text_coords(chart.svg)
        ys_for_20 = sorted(ay for txt, _ax, ay in texts if txt == "20")
        # Two "20" texts: the data label (above the bar) and the axis tick (on
        # the gridline). The data label is the higher (smaller-y) one.
        assert len(ys_for_20) == 2
        data_label_y, tick_y = ys_for_20
        assert data_label_y < tick_y

    def test_tall_bar_label_clamped_inside(self):
        # The tallest bar is pinned to the top edge: placing the label outside
        # (above) would clip the viewBox, so it must drop inside and remain in
        # the viewBox.
        chart = ColumnChart(
            data=[100],
            labels=["max"],
            value_labels="number",
            width=600,
            height=400,
        )
        self._value_labels_inside_viewbox(chart)

    def test_dark_theme_outside_label_is_light(self):
        from charted.themes.core import Theme

        # Two bars so the shorter one has headroom: its label sits OUTSIDE
        # (above the bar) and must use the light, background-contrasting
        # data-label colour to stay legible on the dark background, not a dark
        # inside-bar contrast colour.
        chart = ColumnChart(
            data=[50, 100],
            labels=["A", "B"],
            value_labels="number",
            theme=Theme.from_preset("dark"),
            width=600,
            height=400,
        )
        svg = chart.svg
        import re

        match = re.search(r'fill="(#[0-9a-fA-F]+)"[^>]*>50<', svg)
        assert match is not None
        assert match.group(1).lower() == "#ffffff"
