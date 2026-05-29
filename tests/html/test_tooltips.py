"""Tests for opt-in native SVG <title> tooltips in to_html().

File output (to_svg(), save()) must stay inert: no <title> elements on
data marks. Hover tooltips are an HTML-only, zero-JS feature.
"""

from __future__ import annotations

import re

from charted import ColumnChart, ScatterChart


def _make_column() -> ColumnChart:
    return ColumnChart(
        data=[10, 59, 30],
        labels=["Jan", "Feb", "Mar"],
        series_names=["Sales"],
    )


def test_to_svg_has_no_titles_by_default():
    """Plain to_svg() output must not contain any <title> elements."""
    chart = _make_column()
    svg = chart.to_svg()
    assert "<title>" not in svg
    # save() shares the same svg property, so it stays inert too.
    assert chart.svg == svg


def test_to_html_tooltips_opt_in():
    """to_html(tooltips=True) injects <title> marks; default does not."""
    chart = _make_column()

    plain = chart.to_html()
    assert "<title>" not in plain

    interactive = chart.to_html(tooltips=True)
    assert "<title>" in interactive
    # Requesting tooltips must not mutate the inert svg property.
    assert "<title>" not in chart.to_svg()


def test_tooltip_text_matches_data():
    """Tooltip text for a point equals '<label>: <value>'."""
    chart = _make_column()
    html = chart.to_html(tooltips=True)
    titles = re.findall(r"<title>(.*?)</title>", html)
    assert "Feb: 59" in titles
    assert "Jan: 10" in titles
    assert "Mar: 30" in titles


def test_tooltip_text_matches_data_scatter():
    """Scatter marks also carry series/value tooltips when requested."""
    chart = ScatterChart(
        x_data=[1, 2, 3],
        y_data=[4, 5, 6],
        series_names=["A"],
    )
    html = chart.to_html(tooltips=True)
    titles = re.findall(r"<title>(.*?)</title>", html)
    assert any("A:" in t for t in titles)
    assert chart.to_svg().count("<title>") == 0


def test_tooltips_no_javascript():
    """Emitted interactive HTML contains zero JavaScript."""
    chart = _make_column()
    html = chart.to_html(tooltips=True)
    assert "<script" not in html.lower()
    assert "onmouseover" not in html.lower()
    assert "onclick" not in html.lower()
