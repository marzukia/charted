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

from charted.charts.area import AreaChart
from charted.charts.bar import BarChart
from charted.charts.box import BoxPlot
from charted.charts.bubble import BubbleChart
from charted.charts.column import ColumnChart
from charted.charts.combo import ComboChart
from charted.charts.gantt import GanttChart
from charted.charts.heatmap import HeatmapChart
from charted.charts.histogram import Histogram
from charted.charts.line import LineChart
from charted.charts.pie import PieChart
from charted.charts.polar_area import PolarAreaChart
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


# ============================================================
# Gantt Chart Visual Regression Tests
# ============================================================


def test_gantt_chart_basic():
    """Visual regression test for basic GanttChart (SVG structure)."""
    chart = GanttChart(
        data=[(1, 3), (3, 5), (5, 7)],
        labels=["Design", "Development", "Testing"],
    )
    baseline_path = BASELINES_DIR / "gantt_basic.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_gantt_chart_basic_png():
    """Visual regression test for basic GanttChart (PNG pixel-perfect)."""
    chart = GanttChart(
        data=[(1, 3), (3, 5), (5, 7)],
        labels=["Design", "Development", "Testing"],
    )
    compare_png_baseline(chart, "gantt_basic", tolerance=5)


def test_gantt_chart_dependencies():
    """Visual regression test for GanttChart with dependencies (SVG structure)."""
    chart = GanttChart(
        data=[(1, 4), (3, 6), (5, 8)],
        labels=["A", "B", "C"],
        dependencies=[(0, 1), (1, 2)],
        series_names=["Phase 1"],
    )
    baseline_path = BASELINES_DIR / "gantt_dependencies.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_gantt_chart_dependencies_png():
    """Visual regression test for GanttChart with dependencies (PNG pixel-perfect)."""
    chart = GanttChart(
        data=[(1, 4), (3, 6), (5, 8)],
        labels=["A", "B", "C"],
        dependencies=[(0, 1), (1, 2)],
        series_names=["Phase 1"],
    )
    compare_png_baseline(chart, "gantt_dependencies", tolerance=5)


def test_gantt_chart_multi_series():
    """Visual regression test for multi-series GanttChart (SVG structure)."""
    chart = GanttChart(
        data=[
            [(1, 3), (4, 6)],
            [(2, 5), (6, 8)],
        ],
        labels=["Phase 1 Task A", "Phase 1 Task B", "Phase 2 Task A", "Phase 2 Task B"],
        series_names=["Phase 1", "Phase 2"],
    )
    baseline_path = BASELINES_DIR / "gantt_multi.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_gantt_chart_multi_series_png():
    """Visual regression test for multi-series GanttChart (PNG pixel-perfect)."""
    chart = GanttChart(
        data=[
            [(1, 3), (4, 6)],
            [(2, 5), (6, 8)],
        ],
        labels=["Phase 1 Task A", "Phase 1 Task B", "Phase 2 Task A", "Phase 2 Task B"],
        series_names=["Phase 1", "Phase 2"],
    )
    compare_png_baseline(chart, "gantt_multi", tolerance=5)


def test_heatmap_chart_basic():
    """Visual regression test for basic HeatmapChart (SVG structure)."""
    chart = HeatmapChart(
        data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        x_labels=["A", "B", "C"],
        y_labels=["X", "Y", "Z"],
    )
    baseline_path = BASELINES_DIR / "heatmap_basic.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_heatmap_chart_basic_png():
    """Visual regression test for basic HeatmapChart (PNG pixel-perfect)."""
    chart = HeatmapChart(
        data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        x_labels=["A", "B", "C"],
        y_labels=["X", "Y", "Z"],
    )
    compare_png_baseline(chart, "heatmap_basic", tolerance=5)


def test_heatmap_chart_rectangular():
    """Visual regression test for rectangular HeatmapChart (SVG structure)."""
    chart = HeatmapChart(
        data=[[1, 2, 3, 4], [5, 6, 7, 8]],
        x_labels=["A", "B", "C", "D"],
        y_labels=["X", "Y"],
    )
    baseline_path = BASELINES_DIR / "heatmap_rectangular.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_heatmap_chart_rectangular_png():
    """Visual regression test for rectangular HeatmapChart (PNG pixel-perfect)."""
    chart = HeatmapChart(
        data=[[1, 2, 3, 4], [5, 6, 7, 8]],
        x_labels=["A", "B", "C", "D"],
        y_labels=["X", "Y"],
    )
    compare_png_baseline(chart, "heatmap_rectangular", tolerance=5)


def test_heatmap_chart_continuous():
    """Visual regression test for continuous color_scale HeatmapChart (SVG)."""
    chart = HeatmapChart(
        data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        x_labels=["A", "B", "C"],
        y_labels=["X", "Y", "Z"],
        color_scale="viridis",
    )
    baseline_path = BASELINES_DIR / "heatmap_continuous.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_heatmap_chart_continuous_png():
    """Visual regression test for continuous color_scale HeatmapChart (PNG)."""
    chart = HeatmapChart(
        data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        x_labels=["A", "B", "C"],
        y_labels=["X", "Y", "Z"],
        color_scale="viridis",
    )
    compare_png_baseline(chart, "heatmap_continuous", tolerance=5)


# ============================================================
# New Chart Type Tests: Area, BoxPlot, Histogram
# ============================================================


def test_area_chart_basic():
    """Visual regression test for basic AreaChart (SVG structure)."""
    chart = AreaChart(
        data=[15, 30, 45, 70, 55, 80, 75, 90, 85, 95],
        labels=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
    )
    baseline_path = BASELINES_DIR / "area_basic.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_area_chart_basic_png():
    """Visual regression test for basic AreaChart (PNG pixel-perfect)."""
    chart = AreaChart(
        data=[15, 30, 45, 70, 55, 80, 75, 90, 85, 95],
        labels=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
    )
    compare_png_baseline(chart, "area_basic", tolerance=5)


def test_boxplot_chart_basic():
    """Visual regression test for basic BoxPlot (SVG structure)."""
    chart = BoxPlot(
        data=[
            [3, 5, 7, 9, 10, 12, 14, 16, 18, 20],
            [4, 6, 8, 10, 11, 13, 15, 17, 19, 21],
            [2, 4, 6, 8, 9, 11, 13, 15, 17, 19],
        ],
        labels=["Series A", "Series B", "Series C"],
    )
    baseline_path = BASELINES_DIR / "boxplot_basic.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_boxplot_chart_basic_png():
    """Visual regression test for basic BoxPlot (PNG pixel-perfect)."""
    chart = BoxPlot(
        data=[
            [3, 5, 7, 9, 10, 12, 14, 16, 18, 20],
            [4, 6, 8, 10, 11, 13, 15, 17, 19, 21],
            [2, 4, 6, 8, 9, 11, 13, 15, 17, 19],
        ],
        labels=["Series A", "Series B", "Series C"],
    )
    compare_png_baseline(chart, "boxplot_basic", tolerance=5)


def test_histogram_chart_basic():
    """Visual regression test for basic Histogram (SVG structure)."""
    import random

    random.seed(42)
    data = [random.gauss(50, 15) for _ in range(200)]
    chart = Histogram(data=data)
    baseline_path = BASELINES_DIR / "histogram_basic.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_histogram_chart_basic_png():
    """Visual regression test for basic Histogram (PNG pixel-perfect)."""
    import random

    random.seed(42)
    data = [random.gauss(50, 15) for _ in range(200)]
    chart = Histogram(data=data)
    compare_png_baseline(chart, "histogram_basic", tolerance=5)


# ============================================================
# Matplotlib Parity Feature Tests (data labels, axis titles,
# quadrant labels, reference lines, pie percentages)
# ============================================================


def test_scatter_data_labels():
    """Visual regression test for ScatterChart with data labels (SVG structure)."""
    chart = ScatterChart(
        x_data=[0, 2, 4, 6],
        y_data=[0, 8, 16, 20],
        data_labels=["origin", "alpha", "beta", "peak"],
    )
    baseline_path = BASELINES_DIR / "scatter_data_labels.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_scatter_data_labels_png():
    """Visual regression test for ScatterChart with data labels (PNG pixel-perfect)."""
    chart = ScatterChart(
        x_data=[0, 2, 4, 6],
        y_data=[0, 8, 16, 20],
        data_labels=["origin", "alpha", "beta", "peak"],
    )
    compare_png_baseline(chart, "scatter_data_labels", tolerance=5)


def test_scatter_quadrant_labels():
    """Visual regression test for ScatterChart with quadrant labels (SVG structure)."""
    chart = ScatterChart(
        x_data=[1, 2, 4, 5],
        y_data=[4, 16, 8, 20],
        quadrant_labels=["Top Left", "Top Right", "Bottom Left", "Bottom Right"],
    )
    baseline_path = BASELINES_DIR / "scatter_quadrant_labels.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_scatter_quadrant_labels_png():
    """Visual regression test for ScatterChart with quadrant labels (PNG pixel-perfect)."""
    chart = ScatterChart(
        x_data=[1, 2, 4, 5],
        y_data=[4, 16, 8, 20],
        quadrant_labels=["Top Left", "Top Right", "Bottom Left", "Bottom Right"],
    )
    compare_png_baseline(chart, "scatter_quadrant_labels", tolerance=5)


def test_line_data_labels():
    """Visual regression test for LineChart with data labels (SVG structure)."""
    chart = LineChart(
        data=[0, 8, 16],
        labels=["Q1", "Q2", "Q3"],
        data_labels=["low", "mid", "high"],
    )
    baseline_path = BASELINES_DIR / "line_data_labels.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_line_data_labels_png():
    """Visual regression test for LineChart with data labels (PNG pixel-perfect)."""
    chart = LineChart(
        data=[0, 8, 16],
        labels=["Q1", "Q2", "Q3"],
        data_labels=["low", "mid", "high"],
    )
    compare_png_baseline(chart, "line_data_labels", tolerance=5)


def test_bar_data_labels():
    """Visual regression test for BarChart with data labels (SVG structure)."""
    chart = BarChart(
        data=[30, 90, 150],
        labels=["X", "Y", "Z"],
        data_labels=["30u", "90u", "150u"],
    )
    baseline_path = BASELINES_DIR / "bar_data_labels.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_bar_data_labels_png():
    """Visual regression test for BarChart with data labels (PNG pixel-perfect)."""
    chart = BarChart(
        data=[30, 90, 150],
        labels=["X", "Y", "Z"],
        data_labels=["30u", "90u", "150u"],
    )
    compare_png_baseline(chart, "bar_data_labels", tolerance=5)


def test_column_data_labels():
    """Visual regression test for ColumnChart with data labels (SVG structure)."""
    chart = ColumnChart(
        data=[4, 12, 20],
        labels=["A", "B", "C"],
        data_labels=["four", "twelve", "twenty"],
    )
    baseline_path = BASELINES_DIR / "column_data_labels.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_column_data_labels_png():
    """Visual regression test for ColumnChart with data labels (PNG pixel-perfect)."""
    chart = ColumnChart(
        data=[4, 12, 20],
        labels=["A", "B", "C"],
        data_labels=["four", "twelve", "twenty"],
    )
    compare_png_baseline(chart, "column_data_labels", tolerance=5)


def test_scatter_axis_titles():
    """Visual regression test for ScatterChart with axis titles (SVG structure)."""
    chart = ScatterChart(
        x_data=[0, 2, 4, 6],
        y_data=[0, 8, 16, 20],
        x_label="Velocity",
        y_label="Altitude",
    )
    baseline_path = BASELINES_DIR / "scatter_axis_titles.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_scatter_axis_titles_png():
    """Visual regression test for ScatterChart with axis titles (PNG pixel-perfect)."""
    chart = ScatterChart(
        x_data=[0, 2, 4, 6],
        y_data=[0, 8, 16, 20],
        x_label="Velocity",
        y_label="Altitude",
    )
    compare_png_baseline(chart, "scatter_axis_titles", tolerance=5)


def test_scatter_reference_lines():
    """Visual regression test for ScatterChart with reference lines (SVG structure)."""
    chart = ScatterChart(
        x_data=[0, 2, 4, 6],
        y_data=[0, 8, 16, 20],
        h_lines=[8.0, 16.0],
        v_lines=[2.0, 4.0],
    )
    baseline_path = BASELINES_DIR / "scatter_reference_lines.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_scatter_reference_lines_png():
    """Visual regression test for ScatterChart with reference lines (PNG pixel-perfect)."""
    chart = ScatterChart(
        x_data=[0, 2, 4, 6],
        y_data=[0, 8, 16, 20],
        h_lines=[8.0, 16.0],
        v_lines=[2.0, 4.0],
    )
    compare_png_baseline(chart, "scatter_reference_lines", tolerance=5)


def test_pie_percentages():
    """Visual regression test for PieChart with percentages (SVG structure)."""
    chart = PieChart(
        data=[25, 25, 50],
        labels=["A", "B", "C"],
        show_percentages=True,
    )
    baseline_path = BASELINES_DIR / "pie_percentages.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_pie_percentages_png():
    """Visual regression test for PieChart with percentages (PNG pixel-perfect)."""
    chart = PieChart(
        data=[25, 25, 50],
        labels=["A", "B", "C"],
        show_percentages=True,
    )
    compare_png_baseline(chart, "pie_percentages", tolerance=5)


# ============================================================
# Bubble and Polar Area Chart Visual Regression Tests
# ============================================================


def test_bubble_chart_basic():
    """Visual regression test for basic BubbleChart (SVG structure)."""
    chart = BubbleChart(
        x_data=[1, 2, 3, 4, 5],
        y_data=[10, 25, 15, 30, 20],
        sizes=[5, 30, 12, 45, 18],
    )
    baseline_path = BASELINES_DIR / "bubble_basic.svg"
# Combo Chart Visual Regression Tests (mixed bar + line)
# ============================================================


def test_combo_chart_basic():
    """Visual regression test for basic ComboChart (SVG structure)."""
    chart = ComboChart(
        series=[
            {"data": [10, 20, 30], "type": "bar", "name": "Revenue"},
            {"data": [3, 6, 9], "type": "line", "name": "Margin"},
        ],
        labels=["Q1", "Q2", "Q3"],
    )
    baseline_path = BASELINES_DIR / "combo_basic.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_bubble_chart_basic_png():
    """Visual regression test for basic BubbleChart (PNG pixel-perfect)."""
    chart = BubbleChart(
        x_data=[1, 2, 3, 4, 5],
        y_data=[10, 25, 15, 30, 20],
        sizes=[5, 30, 12, 45, 18],
    )
    compare_png_baseline(chart, "bubble_basic", tolerance=5)


def test_polar_area_chart_basic():
    """Visual regression test for basic PolarAreaChart (SVG structure)."""
    chart = PolarAreaChart(
        data=[10, 20, 30, 15, 25],
        labels=["A", "B", "C", "D", "E"],
    )
    baseline_path = BASELINES_DIR / "polar_area_basic.svg"
def test_combo_chart_basic_png():
    """Visual regression test for basic ComboChart (PNG pixel-perfect)."""
    chart = ComboChart(
        series=[
            {"data": [10, 20, 30], "type": "bar", "name": "Revenue"},
            {"data": [3, 6, 9], "type": "line", "name": "Margin"},
        ],
        labels=["Q1", "Q2", "Q3"],
    )
    compare_png_baseline(chart, "combo_basic", tolerance=5)


def test_combo_chart_secondary_axis():
    """Visual regression test for ComboChart with secondary axis (SVG structure)."""
    chart = ComboChart(
        series=[
            {"data": [120, 180, 150], "type": "bar", "name": "Units"},
            {
                "data": [2.5, 3.1, 2.8],
                "type": "line",
                "name": "Conversion %",
                "axis": "secondary",
            },
        ],
        labels=["Jan", "Feb", "Mar"],
    )
    baseline_path = BASELINES_DIR / "combo_secondary_axis.svg"
    with open(baseline_path, "r") as f:
        baseline_svg = f.read()
    assert svgs_equal(chart.html, baseline_svg)


def test_polar_area_chart_basic_png():
    """Visual regression test for basic PolarAreaChart (PNG pixel-perfect)."""
    chart = PolarAreaChart(
        data=[10, 20, 30, 15, 25],
        labels=["A", "B", "C", "D", "E"],
    )
    compare_png_baseline(chart, "polar_area_basic", tolerance=5)
def test_combo_chart_secondary_axis_png():
    """Visual regression test for ComboChart with secondary axis (PNG pixel-perfect)."""
    chart = ComboChart(
        series=[
            {"data": [120, 180, 150], "type": "bar", "name": "Units"},
            {
                "data": [2.5, 3.1, 2.8],
                "type": "line",
                "name": "Conversion %",
                "axis": "secondary",
            },
        ],
        labels=["Jan", "Feb", "Mar"],
    )
    compare_png_baseline(chart, "combo_secondary_axis", tolerance=5)
