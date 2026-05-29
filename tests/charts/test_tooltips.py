"""Tests for opt-in native SVG ``<title>`` tooltips and XML escaping.

Covers:
- XML escaping of label/value/title text at the serialization sink
- Tooltip presence in side-by-side (``y_stacked=False``) column charts
- Multi-series tooltip distinguishability
- Inertness of ``to_svg()`` (no titles, unchanged output)
"""

import re
from xml.etree import ElementTree

import pytest

from charted.charts.column import ColumnChart


def _extract_svg(html: str) -> str:
    """Pull the ``<svg>...</svg>`` fragment out of an HTML wrapper."""
    match = re.search(r"<svg.*</svg>", html, re.DOTALL)
    assert match, "no <svg> element found in output"
    return match.group(0)


class TestXmlEscaping:
    """Label/value text containing &, <, > must produce valid XML."""

    def test_svg_with_special_chars_in_label_parses(self):
        chart = ColumnChart(data=[10, 20], labels=["A & B", "C < D"])
        svg = chart.to_svg()
        # Raw special chars must be escaped (no bare & or stray < in text).
        assert "A &amp; B" in svg
        assert "C &lt; D" in svg
        # Whole SVG must parse as valid XML.
        ElementTree.fromstring(svg)

    def test_html_tooltips_with_special_chars_parses(self):
        chart = ColumnChart(data=[10, 20], labels=["A & B", "C < D"])
        html = chart.to_html(tooltips=True)
        svg = _extract_svg(html)
        ElementTree.fromstring(svg)
        # The escaped label text must appear inside a <title> tooltip.
        root = ElementTree.fromstring(svg)
        titles = [el.text for el in root.iter() if el.tag.endswith("title") and el.text]
        assert any("A & B" in t for t in titles)
        assert any("C < D" in t for t in titles)

    def test_no_double_escaping(self):
        chart = ColumnChart(data=[10], labels=["A & B"])
        svg = chart.to_svg()
        assert "&amp;amp;" not in svg


class TestSideBySideTooltips:
    """y_stacked=False must still attach tooltips (regression for the
    side-by-side and per-bar branches that previously got none)."""

    def _titles(self, chart):
        svg = _extract_svg(chart.to_html(tooltips=True))
        root = ElementTree.fromstring(svg)
        return [el.text for el in root.iter() if el.tag.endswith("title") and el.text]

    def test_side_by_side_multi_series_has_titles(self):
        chart = ColumnChart(
            data=[[10, 20], [30, 40]],
            labels=["Q1", "Q2"],
            series_names=["North", "South"],
            y_stacked=False,
        )
        titles = self._titles(chart)
        assert titles, "side-by-side chart produced no tooltips"
        # Correct text for the points.
        assert any("Q1" in t and "10" in t for t in titles)
        assert any("Q2" in t and "40" in t for t in titles)

    def test_side_by_side_single_series_has_titles(self):
        chart = ColumnChart(data=[10, 20, 30], labels=["a", "b", "c"], y_stacked=False)
        titles = self._titles(chart)
        assert titles, "single-series side-by-side chart produced no tooltips"
        assert any("a" in t and "10" in t for t in titles)

    def test_per_bar_multicolor_has_titles(self):
        # Single series + multiple colors => per_bar branch.
        chart = ColumnChart(
            data=[10, 20, 30],
            labels=["a", "b", "c"],
            colors=["#f00", "#0f0", "#00f"],
            y_stacked=False,
        )
        titles = self._titles(chart)
        assert titles, "per-bar multicolor chart produced no tooltips"
        assert any("b" in t and "20" in t for t in titles)


class TestMultiSeriesDistinguishable:
    """Two series sharing an x-label must produce distinct tooltip text."""

    def test_two_series_distinguishable(self):
        chart = ColumnChart(
            data=[[10, 20], [10, 20]],
            labels=["Q1", "Q2"],
            series_names=["North", "South"],
        )
        svg = _extract_svg(chart.to_html(tooltips=True))
        root = ElementTree.fromstring(svg)
        titles = [el.text for el in root.iter() if el.tag.endswith("title") and el.text]
        # Same label "Q1" and value 10 in both series, but series name
        # disambiguates them.
        north_q1 = [t for t in titles if "North" in t and "Q1" in t]
        south_q1 = [t for t in titles if "South" in t and "Q1" in t]
        assert north_q1, f"missing North Q1 tooltip in {titles}"
        assert south_q1, f"missing South Q1 tooltip in {titles}"
        assert north_q1[0] != south_q1[0]

    def test_single_series_label_unchanged(self):
        chart = ColumnChart(data=[10, 20], labels=["Q1", "Q2"])
        svg = _extract_svg(chart.to_html(tooltips=True))
        root = ElementTree.fromstring(svg)
        titles = [el.text for el in root.iter() if el.tag.endswith("title") and el.text]
        # Single series keeps the simple "<label>: <value>" form.
        assert any(t == "Q1: 10" for t in titles), titles


class TestToSvgInert:
    """to_svg() must never carry <title> tooltips and must equal repeated
    calls byte-for-byte even after to_html(tooltips=True)."""

    def test_to_svg_has_no_titles(self):
        chart = ColumnChart(
            data=[[10, 20], [30, 40]],
            labels=["Q1", "Q2"],
            series_names=["N", "S"],
            y_stacked=False,
        )
        assert "<title>" not in chart.to_svg()

    def test_to_svg_unchanged_after_tooltip_render(self):
        chart = ColumnChart(
            data=[[10, 20], [30, 40]], labels=["Q1", "Q2"], y_stacked=False
        )
        before = chart.to_svg()
        _ = chart.to_html(tooltips=True)
        after = chart.to_svg()
        assert before == after
        assert "<title>" not in after


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
