"""Visual regression tests for chart rendering using SVG structure comparison."""
# ============================================================
# HOW TO UPDATE BASELINES
# ============================================================
# When chart rendering legitimately changes (bug fixes, features), update baselines:
#
# 1. Find the failing test (e.g., test_column_chart_basic)
# 2. Generate the new SVG:
#    from charted.charts.column import ColumnChart
#    chart = ColumnChart({'A': 10, 'B': 20, 'C': 30})
#    with open('tests/baselines/column_basic.svg', 'w') as f:
#        f.write(chart.to_string())
# 3. Re-run the test to verify it passes
#
# Only update baselines when visual changes are INTENTIONAL.
# ============================================================

from pathlib import Path

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
    except Exception as e:
        raise RuntimeError(f"SVG comparison failed: {e}") from e


# Baseline path is at tests/baselines/, one level up from tests/charts/
BASELINES_DIR = Path(__file__).parent.parent / "baselines"


# ============================================================
# Visual Regression Tests (SVG structure comparison)
# ============================================================


def test_column_chart_basic():
    """Visual regression test for basic ColumnChart (SVG structure)."""
    chart = ColumnChart(data=[1, 2, 3], labels=["a", "b", "c"])
    baseline_path = BASELINES_DIR / "column_basic.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_line_chart_basic():
    """Visual regression test for basic LineChart (SVG structure)."""
    chart = LineChart(data=[1, 2, 3], labels=["a", "b", "c"])
    baseline_path = BASELINES_DIR / "line_basic.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_scatter_chart_basic():
    """Visual regression test for basic ScatterChart (SVG structure)."""
    chart = ScatterChart(x_data=[1, 2, 3], y_data=[1, 2, 3])
    baseline_path = BASELINES_DIR / "scatter_basic.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_column_chart_stacked():
    """Visual regression test for stacked ColumnChart (SVG structure)."""
    chart = ColumnChart(data=[[1, 2, 3], [2, 3, 4]], labels=["a", "b", "c"])
    baseline_path = BASELINES_DIR / "column_stacked.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_line_chart_multi_series():
    """Visual regression test for multi-series LineChart (SVG structure)."""
    chart = LineChart(
        data=[[1, 2, 3], [3, 2, 1]],
        labels=["a", "b", "c"],
        series_names=["Series 1", "Series 2"],
    )
    baseline_path = BASELINES_DIR / "line_multi.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_scatter_chart_multi_series():
    """Visual regression test for multi-series ScatterChart (SVG structure)."""
    chart = ScatterChart(
        x_data=[[1, 2, 3], [2, 3, 4]],
        y_data=[[1, 2, 3], [3, 2, 1]],
    )
    baseline_path = BASELINES_DIR / "scatter_multi.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


# ============================================================
# Edge Case Tests (exception handling)
# ============================================================


def test_column_chart_empty_data():
    """Test ColumnChart with empty data raises an exception."""
    import pytest

    with pytest.raises(Exception, match="No data was provided"):
        ColumnChart(data=[], labels=[])


def test_line_chart_empty_data():
    """Test LineChart with empty data raises an exception."""
    import pytest

    with pytest.raises(Exception, match="No data was provided"):
        LineChart(data=[], labels=[])


def test_scatter_chart_empty_data():
    """Test ScatterChart with empty data raises an exception."""
    import pytest

    with pytest.raises(Exception, match="No data was provided"):
        ScatterChart(x_data=[], y_data=[])
