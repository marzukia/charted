#!/usr/bin/env python3
"""
Regenerate test baselines and update MANIFEST.sha256.

Only run this when chart rendering changes are INTENTIONAL.
After running, commit both the updated SVGs and the new MANIFEST.

Usage:
    python scripts/update_baselines.py
"""
import hashlib
import json
import pathlib
import stat
import sys

# Ensure the package root is on the path.
ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from charted.charts.bar import BarChart
from charted.charts.column import ColumnChart
from charted.charts.line import LineChart
from charted.charts.pie import PieChart
from charted.charts.scatter import ScatterChart

BASELINES_DIR = ROOT / "tests" / "baselines"
MANIFEST_PATH = BASELINES_DIR / "MANIFEST.sha256"

CHARTS = {
    "bar_basic": BarChart(data=[1, 2, 3], labels=["a", "b", "c"]),
    "bar_multi": BarChart(data=[[1, 2, 3], [3, 2, 1]], labels=["a", "b", "c"]),
    "column_basic": ColumnChart(data=[1, 2, 3], labels=["a", "b", "c"]),
    "column_stacked": ColumnChart(data=[[1, 2, 3], [2, 3, 4]], labels=["a", "b", "c"]),
    "line_basic": LineChart(data=[1, 2, 3], labels=["a", "b", "c"]),
    "line_multi": LineChart(
        data=[[1, 2, 3], [3, 2, 1]],
        labels=["a", "b", "c"],
        series_names=["Series 1", "Series 2"],
    ),
    "pie_basic": PieChart(data=[10, 20, 30, 40]),
    "pie_doughnut": PieChart(data=[10, 20, 30, 40], doughnut=True, inner_radius=0.3),
    "scatter_basic": ScatterChart(x_data=[1, 2, 3], y_data=[1, 2, 3]),
    "scatter_multi": ScatterChart(
        x_data=[[1, 2, 3], [2, 3, 4]],
        y_data=[[1, 2, 3], [3, 2, 1]],
    ),
}


def make_writable(path: pathlib.Path) -> None:
    path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)


def make_readonly(path: pathlib.Path) -> None:
    path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)


def main():
    manifest = {}
    for name, chart in CHARTS.items():
        path = BASELINES_DIR / f"{name}.svg"
        if path.exists():
            make_writable(path)
        path.write_text(chart.html)
        h = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest[name + ".svg"] = h
        make_readonly(path)
        print(f"  updated {name}.svg ({h[:16]}...)")

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"\nMANIFEST.sha256 updated — commit baselines/ + MANIFEST together.")


if __name__ == "__main__":
    main()
