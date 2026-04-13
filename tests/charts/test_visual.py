"""Visual regression tests for chart rendering using SVG structure comparison."""

from lxml import etree

from charted.charts.column import ColumnChart
from charted.charts.line import LineChart
from charted.charts.scatter import ScatterChart


# ============================================================
# SVG Structure Comparison (Cross-platform safe)
# ============================================================


def normalize_svg(svg_string: str) -> str:
    """Normalize SVG by removing whitespace and parsing."""
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.fromstring(svg_string.encode(), parser)
    return etree.tostring(tree, encoding="unicode")


def svgs_equal(svg1: str, svg2: str) -> bool:
    """Compare two SVG strings for structural equality."""
    try:
        norm1 = normalize_svg(svg1)
        norm2 = normalize_svg(svg2)
        return norm1 == norm2
    except Exception:
        return False


# ============================================================
# SVG Structure Tests (Cross-platform safe)
# ============================================================


def test_column_chart_basic():
    """Visual regression test for basic ColumnChart (SVG structure)."""
    chart = ColumnChart(data=[1, 2, 3], labels=["a", "b", "c"])
    baseline_svg = open("tests/baselines/column_basic.svg", "r").read()
    assert svgs_equal(chart.html, baseline_svg)


def test_line_chart_basic():
    """Visual regression test for basic LineChart (SVG structure)."""
    chart = LineChart(data=[1, 2, 3], labels=["a", "b", "c"])
    baseline_svg = open("tests/baselines/line_basic.svg", "r").read()
    assert svgs_equal(chart.html, baseline_svg)


def test_scatter_chart_basic():
    """Visual regression test for basic ScatterChart (SVG structure)."""
    chart = ScatterChart(x_data=[1, 2, 3], y_data=[1, 2, 3])
    baseline_svg = open("tests/baselines/scatter_basic.svg", "r").read()
    assert svgs_equal(chart.html, baseline_svg)


def test_column_chart_stacked():
    """Visual regression test for stacked ColumnChart (SVG structure)."""
    chart = ColumnChart(data=[[1, 2, 3], [2, 3, 4]], labels=["a", "b", "c"])
    baseline_svg = open("tests/baselines/column_stacked.svg", "r").read()
    assert svgs_equal(chart.html, baseline_svg)


def test_line_chart_multi_series():
    """Visual regression test for multi-series LineChart (SVG structure)."""
    chart = LineChart(
        data=[[1, 2, 3], [3, 2, 1]],
        labels=["a", "b", "c"],
        series_names=["Series 1", "Series 2"],
    )
    baseline_svg = open("tests/baselines/line_multi.svg", "r").read()
    assert svgs_equal(chart.html, baseline_svg)


def test_scatter_chart_multi_series():
    """Visual regression test for multi-series ScatterChart (SVG structure)."""
    chart = ScatterChart(
        x_data=[[1, 2, 3], [2, 3, 4]],
        y_data=[[1, 2, 3], [3, 2, 1]],
    )
    baseline_svg = open("tests/baselines/scatter_multi.svg", "r").read()
    assert svgs_equal(chart.html, baseline_svg)
