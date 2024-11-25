"""Visual regression tests for chart rendering using both SVG structure and PNG pixel comparison.

This module implements a hybrid testing approach:
1. **SVG structural tests**: Verify correct DOM elements, attributes, and structure
2. **PNG pixel-perfect tests**: Prevent AI agents from easily mutating visual output

The combination makes it much harder for AI to "cheat" by only satisfying structural checks
while producing visually incorrect output.

============================================================
HOW TO UPDATE BASELINES
============================================================
When chart rendering legitimately changes (bug fixes, features), update baselines:

1. Find the failing test (e.g., test_column_chart_basic)
2. Generate the new SVG baseline:
    from charted.charts.column import ColumnChart
    chart = ColumnChart({'A': 10, 'B': 20, 'C': 30})
    with open('tests/baselines/column_basic.svg', 'w') as f:
        f.write(chart.to_string())

3. Generate the new PNG baseline:
    python scripts/update_baselines.py --png-only column_basic

4. Re-run the test to verify it passes

Only update baselines when visual changes are INTENTIONAL.
============================================================
"""

from pathlib import Path

import pytest
from lxml import etree

from charted.charts.bar import BarChart
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
DIFFS_DIR = Path(__file__).parent.parent / "diffs"


# ============================================================
# PNG Image Comparison (Pixel-perfect visual testing)
# ============================================================


def compare_png_baseline(
    chart, baseline_name: str, tolerance: int = 5, width: int = 500, height: int = 500
):
    """
    Compare chart rendering against PNG baseline with pixel-perfect accuracy.

    Args:
        chart: Chart object with .html attribute containing SVG
        baseline_name: Name of baseline file (e.g., "column_basic")
        tolerance: Max pixel difference per channel (0-255).
                  5 allows minor anti-aliasing differences
        width: Output image width
        height: Output image height

    Raises:
        AssertionError: If images don't match within tolerance
    """
    # Lazy import to avoid runtime dependency
    try:
        from tests.utils.image_comparison import (
            compare_images,
            render_chart_to_png,
        )
    except ImportError as e:
        pytest.skip(f"PNG testing dependencies not installed: {e}")

    # Generate PNG from chart
    try:
        actual_png = render_chart_to_png(chart, width, height)
    except ImportError as e:
        pytest.skip(f"Cannot render to PNG: {e}")

    # Save temporary actual image
    temp_actual = DIFFS_DIR / f"{baseline_name}_actual.png"
    DIFFS_DIR.mkdir(exist_ok=True)
    actual_png.save(temp_actual)

    # Check if baseline exists
    baseline_png = BASELINES_DIR / f"{baseline_name}.png"
    if not baseline_png.exists():
        pytest.fail(
            f"PNG baseline missing: {baseline_png}\n"
            f"Run: python scripts/update_baselines.py {baseline_name}"
        )

    # Compare with baseline
    is_match, diff_image = compare_images(temp_actual, baseline_png, tolerance)

    if not is_match:
        # Save diff for debugging
        diff_path = DIFFS_DIR / f"{baseline_name}_diff.png"
        if diff_image:
            diff_image.save(diff_path)

        pytest.fail(
            f"Visual mismatch for {baseline_name}\n"
            f"Diff saved to: {diff_path}\n"
            f"Tolerance: {tolerance} pixels\n"
            f"Run 'python scripts/update_baselines.py {baseline_name}' to update baseline"
        )

    # Clean up temp file
    temp_actual.unlink(missing_ok=True)


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


def test_column_chart_basic_png():
    """Visual regression test for basic ColumnChart (PNG pixel-perfect)."""
    chart = ColumnChart(data=[1, 2, 3], labels=["a", "b", "c"])
    compare_png_baseline(chart, "column_basic", tolerance=5)


def test_line_chart_basic():
    """Visual regression test for basic LineChart (SVG structure)."""
    chart = LineChart(data=[1, 2, 3], labels=["a", "b", "c"])
    baseline_path = BASELINES_DIR / "line_basic.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_line_chart_basic_png():
    """Visual regression test for basic LineChart (PNG pixel-perfect)."""
    chart = LineChart(data=[1, 2, 3], labels=["a", "b", "c"])
    compare_png_baseline(chart, "line_basic", tolerance=5)


def test_scatter_chart_basic():
    """Visual regression test for basic ScatterChart (SVG structure)."""
    chart = ScatterChart(x_data=[1, 2, 3], y_data=[1, 2, 3])
    baseline_path = BASELINES_DIR / "scatter_basic.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_scatter_chart_basic_png():
    """Visual regression test for basic ScatterChart (PNG pixel-perfect)."""
    chart = ScatterChart(x_data=[1, 2, 3], y_data=[1, 2, 3])
    compare_png_baseline(chart, "scatter_basic", tolerance=5)


def test_column_chart_stacked():
    """Visual regression test for stacked ColumnChart (SVG structure)."""
    chart = ColumnChart(data=[[1, 2, 3], [2, 3, 4]], labels=["a", "b", "c"])
    baseline_path = BASELINES_DIR / "column_stacked.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_column_chart_stacked_png():
    """Visual regression test for stacked ColumnChart (PNG pixel-perfect)."""
    chart = ColumnChart(data=[[1, 2, 3], [2, 3, 4]], labels=["a", "b", "c"])
    compare_png_baseline(chart, "column_stacked", tolerance=5)


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


def test_line_chart_multi_series_png():
    """Visual regression test for multi-series LineChart (PNG pixel-perfect)."""
    chart = LineChart(
        data=[[1, 2, 3], [3, 2, 1]],
        labels=["a", "b", "c"],
        series_names=["Series 1", "Series 2"],
    )
    compare_png_baseline(chart, "line_multi", tolerance=5)


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


def test_scatter_chart_multi_series_png():
    """Visual regression test for multi-series ScatterChart (PNG pixel-perfect)."""
    chart = ScatterChart(
        x_data=[[1, 2, 3], [2, 3, 4]],
        y_data=[[1, 2, 3], [3, 2, 1]],
    )
    compare_png_baseline(chart, "scatter_multi", tolerance=5)


def test_bar_chart_basic():
    """Visual regression test for basic BarChart (SVG structure)."""
    chart = BarChart(data=[1, 2, 3], labels=["a", "b", "c"])
    baseline_path = BASELINES_DIR / "bar_basic.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_bar_chart_basic_png():
    """Visual regression test for basic BarChart (PNG pixel-perfect)."""
    chart = BarChart(data=[1, 2, 3], labels=["a", "b", "c"])
    compare_png_baseline(chart, "bar_basic", tolerance=5)


def test_bar_chart_multi_series():
    """Visual regression test for multi-series BarChart (SVG structure)."""
    chart = BarChart(
        data=[[1, 2, 3], [3, 2, 1]],
        labels=["a", "b", "c"],
        x_stacked=True,  # Multi-series stacks along X axis for bar charts
    )
    baseline_path = BASELINES_DIR / "bar_multi.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_bar_chart_multi_series_png():
    """Visual regression test for multi-series BarChart (PNG pixel-perfect)."""
    chart = BarChart(
        data=[[1, 2, 3], [3, 2, 1]],
        labels=["a", "b", "c"],
        x_stacked=True,
    )
    compare_png_baseline(chart, "bar_multi", tolerance=5)


def test_bar_chart_negative_values():
    """Visual regression test for BarChart with negative values (zero line)."""
    chart = BarChart(data=[-20, 10, 30], labels=["A", "B", "C"])
    compare_png_baseline(chart, "bar_negative", tolerance=5)


def test_bar_chart_stacked_negative_values():
    """Visual regression test for stacked BarChart with negative values (zero line)."""
    chart = BarChart(data=[[-10, 20], [5, 15]], labels=["A", "B"], x_stacked=True)
    compare_png_baseline(chart, "bar_stacked_negative", tolerance=5)


def test_column_chart_negative_values():
    """Visual regression test for ColumnChart with negative values (zero line)."""
    chart = ColumnChart(data=[-10, 5, 20], labels=["X", "Y", "Z"])
    compare_png_baseline(chart, "column_negative", tolerance=5)


def test_column_chart_stacked_negative_values():
    """Visual regression test for stacked ColumnChart with negative values (zero line)."""
    chart = ColumnChart(data=[[-5, 10], [3, 8]], labels=["X", "Y"], y_stacked=True)
    compare_png_baseline(chart, "column_stacked_negative", tolerance=5)


# ============================================================
# Edge Case Tests (exception handling)
# ============================================================


def test_column_chart_empty_data():
    """Test ColumnChart with empty data raises an exception."""
    with pytest.raises(Exception, match="No data was provided"):
        ColumnChart(data=[], labels=[])


def test_line_chart_empty_data():
    """Test LineChart with empty data raises an exception."""
    with pytest.raises(Exception, match="No data was provided"):
        LineChart(data=[], labels=[])


def test_scatter_chart_empty_data():
    """Test ScatterChart with empty data raises an exception."""
    with pytest.raises(Exception, match="No data was provided"):
        ScatterChart(x_data=[], y_data=[])
