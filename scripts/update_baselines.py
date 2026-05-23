#!/usr/bin/env python3
"""
Regenerate test baselines and update MANIFEST.sha256 for both SVG and PNG.

Only run this when chart rendering changes are INTENTIONAL.
After running, commit both the updated baselines and the new MANIFEST.

Usage:
    # Update all baselines (SVG + PNG)
    python scripts/update_baselines.py

    # Update only specific chart
    python scripts/update_baselines.py column_basic

    # Update only SVGs (skip PNG generation)
    python scripts/update_baselines.py --svg-only

    # Update only PNGs (skip SVG regeneration)
    python scripts/update_baselines.py --png-only

PNG baselines require dev dependencies:
    pip install 'pillow>=10.0.0' 'numpy>=1.24.0' 'cairosvg>=2.7.0'
"""

import hashlib
import json
import pathlib
import stat
import sys
from typing import Optional

# Ensure the package root is on the path.
ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from charted.charts.bar import BarChart
from charted.charts.column import ColumnChart
from charted.charts.gantt import GanttChart
from charted.charts.heatmap import HeatmapChart
from charted.charts.line import LineChart
from charted.charts.pie import PieChart
from charted.charts.radar import RadarChart
from charted.charts.scatter import ScatterChart

BASELINES_DIR = ROOT / "tests" / "baselines"
DIFFS_DIR = ROOT / "tests" / "diffs"
MANIFEST_PATH = BASELINES_DIR / "MANIFEST.sha256"
PNG_MANIFEST_PATH = BASELINES_DIR / "PNG_MANIFEST.sha256"

CHARTS = {
    # Bar charts
    "bar_basic": BarChart(data=[1, 2, 3], labels=["a", "b", "c"]),
    "bar_multi": BarChart(
        data=[[1, 2, 3], [3, 2, 1]], labels=["a", "b", "c"], x_stacked=True
    ),
    "bar_stacked": BarChart(
        data=[[1, 2, 3], [3, 2, 1]], labels=["a", "b", "c"], x_stacked=True
    ),
    # Bar charts with negative values (zero line tests)
    "bar_negative": BarChart(data=[-20, 10, 30], labels=["A", "B", "C"]),
    "bar_stacked_negative": BarChart(
        data=[[-10, 20], [5, 15]], labels=["A", "B"], x_stacked=True
    ),
    # Column charts
    "column_basic": ColumnChart(data=[1, 2, 3], labels=["a", "b", "c"]),
    "column_stacked": ColumnChart(data=[[1, 2, 3], [2, 3, 4]], labels=["a", "b", "c"]),
    # Column charts with negative values (zero line tests)
    "column_negative": ColumnChart(data=[-10, 5, 20], labels=["X", "Y", "Z"]),
    "column_stacked_negative": ColumnChart(
        data=[[-5, 10], [3, 8]], labels=["X", "Y"], y_stacked=True
    ),
    "column_sidebyside": ColumnChart(
        data=[[1, 2, 3], [3, 2, 1]], labels=["a", "b", "c"], y_stacked=False
    ),
    # Line charts
    "line_basic": LineChart(data=[1, 2, 3], labels=["a", "b", "c"]),
    "line_multi": LineChart(
        data=[[1, 2, 3], [3, 2, 1]],
        labels=["a", "b", "c"],
        series_names=["Series 1", "Series 2"],
    ),
    # Pie charts
    "pie": PieChart(
        data=[45, 30, 15, 10], labels=["Electronics", "Clothing", "Food", "Other"]
    ),
    "pie_doughnut": PieChart(
        data=[30, 40, 30], labels=["A", "B", "C"], inner_radius=0.5
    ),
    # Scatter charts
    "scatter_basic": ScatterChart(x_data=[1, 2, 3], y_data=[1, 2, 3]),
    "scatter_multi": ScatterChart(
        x_data=[[1, 2, 3], [2, 3, 4]],
        y_data=[[1, 2, 3], [3, 2, 1]],
    ),
    # Gantt charts
    "gantt_basic": GanttChart(
        data=[(1, 3), (3, 5), (5, 7)],
        labels=["Design", "Development", "Testing"],
    ),
    "gantt_dependencies": GanttChart(
        data=[(1, 4), (3, 6), (5, 8)],
        labels=["A", "B", "C"],
        dependencies=[(0, 1), (1, 2)],
        series_names=["Phase 1"],
    ),
    "gantt_multi": GanttChart(
        data=[
            [(1, 3), (4, 6)],
            [(2, 5), (6, 8)],
        ],
        labels=["Phase 1 Task A", "Phase 1 Task B", "Phase 2 Task A", "Phase 2 Task B"],
        series_names=["Phase 1", "Phase 2"],
    ),
    # Heatmap charts
    "heatmap_basic": HeatmapChart(
        data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        x_labels=["A", "B", "C"],
        y_labels=["X", "Y", "Z"],
    ),
    "heatmap_rectangular": HeatmapChart(
        data=[[1, 2, 3, 4], [5, 6, 7, 8]],
        x_labels=["A", "B", "C", "D"],
        y_labels=["X", "Y"],
    ),
    # Radar charts
    "radar": RadarChart(
        data=[8, 7, 6, 9, 5],
        labels=["Speed", "Power", "Range", "Armor", "Stealth"],
    ),
    "radar_multi": RadarChart(
        data=[
            [8, 7, 6, 9, 5],
            [6, 9, 8, 5, 8],
        ],
        labels=["Speed", "Power", "Range", "Armor", "Stealth"],
        series_names=["Unit A", "Unit B"],
    ),
}


def make_writable(path: pathlib.Path) -> None:
    path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)


def make_readonly(path: pathlib.Path) -> None:
    path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)


def generate_png_from_chart(
    chart, name: str, width: int = 500, height: int = 500
) -> Optional[pathlib.Path]:
    """
    Generate PNG from chart SVG. Returns path to generated PNG or None on failure.
    """
    try:
        import cairosvg
    except ImportError as e:
        print(f"  ⚠ Skipping PNG for {name}: {e}")
        return None

    try:
        # Get SVG data from chart
        if hasattr(chart, "html"):
            svg_data = chart.html
        elif hasattr(chart, "svg"):
            svg_data = chart.svg
        else:
            print(f"  ⚠ Chart {name} has no html/svg attribute")
            return None

        # Convert SVG to PNG
        png_data = cairosvg.svg2png(
            bytestring=svg_data.encode("utf-8"),
            output_width=width,
            output_height=height,
            scale=2,  # High resolution for better accuracy
        )

        # Save PNG
        png_path = BASELINES_DIR / f"{name}.png"
        png_path.write_bytes(png_data)

        return png_path
    except Exception as e:
        print(f"  ⚠ Failed to generate PNG for {name}: {e}")
        return None


def main():
    # Parse arguments
    args = sys.argv[1:]
    specific_name = None
    svg_only = "--svg-only" in args
    png_only = "--png-only" in args

    if "--svg-only" in args:
        args.remove("--svg-only")
    if "--png-only" in args:
        args.remove("--png-only")

    if args:
        specific_name = args[0]

    # Filter charts if specific name provided
    charts_to_update = (
        {specific_name: CHARTS[specific_name]} if specific_name else CHARTS
    )

    svg_manifest = {}
    png_manifest = {}

    print("Updating baselines...")
    print()

    # Update SVG baselines
    if not png_only:
        print("📄 SVG Baselines:")
        for name, chart in charts_to_update.items():
            path = BASELINES_DIR / f"{name}.svg"
            if path.exists():
                make_writable(path)
            path.write_text(chart.html)
            h = hashlib.sha256(path.read_bytes()).hexdigest()
            svg_manifest[name + ".svg"] = h
            make_readonly(path)
            print(f"  ✓ updated {name}.svg ({h[:16]}...)")
        print()

    # Update PNG baselines
    if not svg_only:
        print("🖼️  PNG Baselines:")
        for name, chart in charts_to_update.items():
            png_path = generate_png_from_chart(chart, name)
            if png_path and png_path.exists():
                h = hashlib.sha256(png_path.read_bytes()).hexdigest()
                png_manifest[name + ".png"] = h
                print(f"  ✓ updated {name}.png ({h[:16]}...)")
            else:
                print(f"  ⚠ skipped {name}.png (dependencies missing?)")
        print()

    # Update manifests
    if not png_only:
        MANIFEST_PATH.write_text(json.dumps(svg_manifest, indent=2) + "\n")
        print("✓ MANIFEST.sha256 updated")

    if not svg_only:
        PNG_MANIFEST_PATH.write_text(json.dumps(png_manifest, indent=2) + "\n")
        print("✓ PNG_MANIFEST.sha256 updated")

    print()
    print("=" * 60)
    print("Commit both baselines/ and MANIFEST files together:")
    print("  git add tests/baselines/")
    print("  git commit -m 'refactor: update visual baselines'")
    print("=" * 60)


if __name__ == "__main__":
    main()
