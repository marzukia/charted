#!/usr/bin/env python3
"""Stress-test gauntlet for the charted library.

Throws extreme / edge-case data at every chart type, renders each, captures
failures, and writes a single self-contained HTML gallery.
"""
from __future__ import annotations

import html
import math
import re
import traceback
from dataclasses import dataclass, field

from charted.charts import (
    AreaChart,
    BarChart,
    BoxPlot,
    BubbleChart,
    ColumnChart,
    ComboChart,
    GanttChart,
    HeatmapChart,
    Histogram,
    LineChart,
    PieChart,
    PolarAreaChart,
    RadarChart,
    ScatterChart,
)
from charted.themes import Theme

DARK = Theme(
    background_color="#0d1b2a",
    root_color="#e0e1dd",
    grid_color="#415a77",
    title_color="#e0e1dd",
    legend_font_color="#e0e1dd",
)

LONG_LABEL = "Quarterly revenue from the Northern European distribution division (provisional)"
UNICODE_LABELS = ["日本語ラベル", "🚀 launch", "Ω≈ç√", "x"]


@dataclass
class Case:
    desc: str
    fn: object  # callable returning a chart
    suspect: bool = False  # spot-check candidate


@dataclass
class Result:
    desc: str
    suspect: bool
    svg: str | None = None
    error: str | None = None
    overflow: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Overflow detection: find <text> nodes whose x/y fall well outside viewBox.
# ---------------------------------------------------------------------------
def detect_overflow(svg: str) -> list[str]:
    m = re.search(r'viewBox="([\d.\- ]+)"', svg)
    if not m:
        return []
    parts = m.group(1).split()
    if len(parts) != 4:
        return []
    vx, vy, vw, vh = (float(p) for p in parts)
    minx, miny, maxx, maxy = vx, vy, vx + vw, vy + vh
    margin = 2.0  # px tolerance for anti-aliasing / stroke
    issues: list[str] = []
    for tm in re.finditer(r"<text\b([^>]*)>(.*?)</text>", svg, re.DOTALL):
        attrs, inner = tm.group(1), tm.group(2)
        xm = re.search(r'\bx="(-?[\d.]+)"', attrs)
        ym = re.search(r'\by="(-?[\d.]+)"', attrs)
        if not xm or not ym:
            continue
        x, y = float(xm.group(1)), float(ym.group(1))
        text = re.sub(r"<[^>]+>", "", inner).strip()
        label = (text[:24] + "…") if len(text) > 24 else text
        if x < minx - margin or x > maxx + margin or y < miny - margin or y > maxy + margin:
            issues.append(f'text "{label}" at ({x:.0f},{y:.0f}) outside viewBox {vw:.0f}x{vh:.0f}')
    return issues


def run_case(case: Case) -> Result:
    res = Result(desc=case.desc, suspect=case.suspect)
    try:
        chart = case.fn()
        svg = chart.svg
        res.svg = svg
        res.overflow = detect_overflow(svg)
    except Exception as e:  # noqa: BLE001 - we want to capture everything
        tb = traceback.format_exc().strip().splitlines()
        res.error = f"{type(e).__name__}: {e}"
        # keep last frame for context
        res.error += "\n" + "\n".join(tb[-3:])
    return res


# ---------------------------------------------------------------------------
# Case batteries per chart type. Each value is a list of Case.
# ---------------------------------------------------------------------------
def many(n: int) -> list[float]:
    return [round(50 + 40 * math.sin(i / 6.0) + (i % 7), 3) for i in range(n)]


def lbls(n: int) -> list[str]:
    return [f"c{i}" for i in range(n)]


BATTERIES: dict[str, list[Case]] = {}


def battery(name: str):
    def deco(fn):
        BATTERIES[name] = fn()
        return fn

    return deco


@battery("BarChart")
def _bar():
    return [
        Case("Huge numbers [1e9, 999999999, 1]", lambda: BarChart([1_000_000_000, 999_999_999, 1], ["a", "b", "c"], value_labels=True, title="Huge numbers")),
        Case("Tiny decimals [0.0001, 0.0002, 0.00015]", lambda: BarChart([0.0001, 0.0002, 0.00015], ["a", "b", "c"], value_labels=True)),
        Case("Extreme dynamic range [1,1000,1,5e6]", lambda: BarChart([1, 1000, 1, 5_000_000], ["a", "b", "c", "d"], value_labels=True), suspect=True),
        Case("All negative [-50,-30,-90]", lambda: BarChart([-50, -30, -90], ["a", "b", "c"], value_labels=True)),
        Case("Mixed pos/neg [-40,60,-20,80]", lambda: BarChart([-40, 60, -20, 80], ["a", "b", "c", "d"], value_labels=True)),
        Case("All zeros [0,0,0]", lambda: BarChart([0, 0, 0], ["a", "b", "c"])),
        Case("Single zero among values [10,0,30]", lambda: BarChart([10, 0, 30], ["a", "b", "c"], value_labels=True)),
        Case("Single data point [42]", lambda: BarChart([42], ["only"], value_labels=True)),
        Case("All identical [5,5,5,5]", lambda: BarChart([5, 5, 5, 5], ["a", "b", "c", "d"], value_labels=True)),
        Case("200 points (label thinning)", lambda: BarChart(many(200), lbls(200)), suspect=True),
        Case("Very long labels (80 char)", lambda: BarChart([3, 5, 2], [LONG_LABEL, LONG_LABEL, "short"]), suspect=True),
        Case("Unicode/emoji labels", lambda: BarChart([10, 20, 30, 5], UNICODE_LABELS)),
        Case("Two series wildly diff magnitudes", lambda: BarChart([[1, 2, 3], [1_000_000, 2_000_000, 3_000_000]], ["a", "b", "c"])),
        Case("Mismatched label count (SHOULD error?)", lambda: BarChart([1, 2, 3], ["only_one"])),
        Case("Dark theme variant", lambda: BarChart([5, 9, 3, 7], ["a", "b", "c", "d"], theme=DARK, value_labels=True, title="Dark bar"), suspect=True),
    ]


@battery("ColumnChart")
def _col():
    return [
        Case("Huge numbers", lambda: ColumnChart([1_000_000_000, 999_999_999, 1], ["a", "b", "c"], value_labels=True)),
        Case("Tiny decimals", lambda: ColumnChart([0.0001, 0.0002, 0.00015], ["a", "b", "c"])),
        Case("Extreme dynamic range", lambda: ColumnChart([1, 1000, 1, 5_000_000], ["a", "b", "c", "d"]), suspect=True),
        Case("All negative", lambda: ColumnChart([-50, -30, -90], ["a", "b", "c"], value_labels=True)),
        Case("Mixed pos/neg", lambda: ColumnChart([-40, 60, -20, 80], ["a", "b", "c", "d"], value_labels=True)),
        Case("All zeros", lambda: ColumnChart([0, 0, 0], ["a", "b", "c"])),
        Case("Single data point", lambda: ColumnChart([42], ["only"], value_labels=True)),
        Case("All identical", lambda: ColumnChart([5, 5, 5, 5], ["a", "b", "c", "d"])),
        Case("200 points", lambda: ColumnChart(many(200), lbls(200)), suspect=True),
        Case("Very long labels", lambda: ColumnChart([3, 5, 2], [LONG_LABEL, "short", "mid"])),
        Case("Two-series stacked wildly diff", lambda: ColumnChart([[1, 2, 3], [1_000_000, 2_000_000, 3_000_000]], ["a", "b", "c"], y_stacked=True)),
        Case("Dark theme", lambda: ColumnChart([5, 9, 3, 7], ["a", "b", "c", "d"], theme=DARK, title="Dark column")),
    ]


@battery("LineChart")
def _line():
    return [
        Case("Huge numbers", lambda: LineChart([1_000_000_000, 999_999_999, 1], labels=["a", "b", "c"], markers=True)),
        Case("Tiny decimals", lambda: LineChart([0.0001, 0.0002, 0.00015], labels=["a", "b", "c"])),
        Case("Extreme dynamic range", lambda: LineChart([1, 1000, 1, 5_000_000], labels=["a", "b", "c", "d"]), suspect=True),
        Case("All negative", lambda: LineChart([-50, -30, -90], labels=["a", "b", "c"])),
        Case("Mixed pos/neg", lambda: LineChart([-40, 60, -20, 80], labels=["a", "b", "c", "d"])),
        Case("All zeros", lambda: LineChart([0, 0, 0], labels=["a", "b", "c"])),
        Case("Single data point", lambda: LineChart([42], labels=["only"]), suspect=True),
        Case("All identical (flat line)", lambda: LineChart([5, 5, 5, 5], labels=["a", "b", "c", "d"])),
        Case("300 points (crowding)", lambda: LineChart(many(300), labels=lbls(300)), suspect=True),
        Case("Very long labels", lambda: LineChart([3, 5, 2], labels=[LONG_LABEL, "b", "c"])),
        Case("Two series wildly diff", lambda: LineChart([[1, 2, 3], [1_000_000, 2_000_000, 3_000_000]], labels=["a", "b", "c"])),
        Case("Dark theme", lambda: LineChart([3, 7, 4, 9, 2], labels=lbls(5), theme=DARK, markers=True, title="Dark line")),
    ]


@battery("AreaChart")
def _area():
    return [
        Case("Huge numbers", lambda: AreaChart([1_000_000_000, 999_999_999, 1], labels=["a", "b", "c"])),
        Case("Tiny decimals", lambda: AreaChart([0.0001, 0.0002, 0.00015], labels=["a", "b", "c"])),
        Case("Extreme dynamic range", lambda: AreaChart([1, 1000, 1, 5_000_000], labels=["a", "b", "c", "d"]), suspect=True),
        Case("All negative", lambda: AreaChart([-50, -30, -90], labels=["a", "b", "c"])),
        Case("Mixed pos/neg", lambda: AreaChart([-40, 60, -20, 80], labels=["a", "b", "c", "d"])),
        Case("All zeros", lambda: AreaChart([0, 0, 0], labels=["a", "b", "c"])),
        Case("Single data point", lambda: AreaChart([42], labels=["only"])),
        Case("All identical", lambda: AreaChart([5, 5, 5, 5], labels=["a", "b", "c", "d"])),
        Case("200 points", lambda: AreaChart(many(200), labels=lbls(200))),
        Case("Two-series stacked wildly diff", lambda: AreaChart([[1, 2, 3], [1_000_000, 2_000_000, 3_000_000]], labels=["a", "b", "c"])),
        Case("Dark theme", lambda: AreaChart([3, 7, 4, 9, 2], labels=lbls(5), theme=DARK, title="Dark area")),
    ]


@battery("PieChart")
def _pie():
    return [
        Case("Huge numbers", lambda: PieChart([1_000_000_000, 999_999_999, 1], ["a", "b", "c"])),
        Case("Tiny decimals", lambda: PieChart([0.0001, 0.0002, 0.00015], ["a", "b", "c"])),
        Case("Extreme dynamic range", lambda: PieChart([1, 1000, 1, 5_000_000], ["a", "b", "c", "d"])),
        Case("All zeros (SHOULD error)", lambda: PieChart([0, 0, 0], ["a", "b", "c"])),
        Case("Single zero among values", lambda: PieChart([10, 0, 30], ["a", "b", "c"])),
        Case("Contains negative (SHOULD error?)", lambda: PieChart([-50, 30, 90], ["a", "b", "c"])),
        Case("Single data point", lambda: PieChart([42], ["only"])),
        Case("All identical", lambda: PieChart([5, 5, 5, 5], ["a", "b", "c", "d"])),
        Case("Many slices (40)", lambda: PieChart(list(range(1, 41)), lbls(40)), suspect=True),
        Case("Very long labels", lambda: PieChart([3, 5, 2], [LONG_LABEL, "b", "c"])),
        Case("Unicode labels", lambda: PieChart([10, 20, 30, 5], UNICODE_LABELS)),
        Case("Dark theme", lambda: PieChart([5, 9, 3, 7], ["a", "b", "c", "d"], theme=DARK, title="Dark pie")),
    ]


@battery("ScatterChart")
def _scatter():
    return [
        Case("Huge numbers", lambda: ScatterChart([1e9, 9.99e8, 1], [1e9, 1, 5e8])),
        Case("Tiny decimals", lambda: ScatterChart([0.0001, 0.0002, 0.00015], [0.0003, 0.0001, 0.0002])),
        Case("Extreme dynamic range x", lambda: ScatterChart([1, 1000, 1, 5_000_000], [1, 2, 3, 4]), suspect=True),
        Case("All negative", lambda: ScatterChart([-50, -30, -90], [-10, -20, -30])),
        Case("Mixed pos/neg (quadrants)", lambda: ScatterChart([-40, 60, -20, 80], [-40, 60, 20, -80])),
        Case("All zeros", lambda: ScatterChart([0, 0, 0], [0, 0, 0])),
        Case("Single point", lambda: ScatterChart([42], [42]), suspect=True),
        Case("All identical (collapsed)", lambda: ScatterChart([5, 5, 5, 5], [5, 5, 5, 5])),
        Case("300 points", lambda: ScatterChart(many(300), many(300)[::-1])),
        Case("Mismatched x/y len (SHOULD error)", lambda: ScatterChart([1, 2, 3], [1, 2])),
        Case("Dark theme", lambda: ScatterChart([1, 2, 3, 4], [4, 1, 3, 2], theme=DARK, title="Dark scatter")),
    ]


@battery("BubbleChart")
def _bubble():
    return [
        Case("Huge numbers", lambda: BubbleChart([1e9, 9.99e8, 1], [1e9, 1, 5e8], [10, 20, 30])),
        Case("Tiny decimals", lambda: BubbleChart([0.0001, 0.0002, 0.00015], [0.0003, 0.0001, 0.0002], [1, 2, 3])),
        Case("Extreme size range", lambda: BubbleChart([1, 2, 3, 4], [1, 2, 3, 4], [1, 1000, 1, 5_000_000]), suspect=True),
        Case("Negative sizes (SHOULD error?)", lambda: BubbleChart([1, 2, 3], [1, 2, 3], [-10, -20, -30])),
        Case("All zero sizes", lambda: BubbleChart([1, 2, 3], [1, 2, 3], [0, 0, 0])),
        Case("Single point", lambda: BubbleChart([42], [42], [10])),
        Case("All identical", lambda: BubbleChart([5, 5, 5], [5, 5, 5], [5, 5, 5])),
        Case("Mismatched sizes len (SHOULD error)", lambda: BubbleChart([1, 2, 3], [1, 2, 3], [10, 20])),
        Case("Dark theme", lambda: BubbleChart([1, 2, 3, 4], [4, 1, 3, 2], [5, 10, 15, 8], theme=DARK, title="Dark bubble")),
    ]


@battery("RadarChart")
def _radar():
    return [
        Case("Huge numbers", lambda: RadarChart([1_000_000_000, 999_999_999, 1], ["a", "b", "c"])),
        Case("Tiny decimals", lambda: RadarChart([0.0001, 0.0002, 0.00015], ["a", "b", "c"])),
        Case("Extreme dynamic range", lambda: RadarChart([1, 1000, 1, 5_000_000], ["a", "b", "c", "d"]), suspect=True),
        Case("All negative", lambda: RadarChart([-50, -30, -90], ["a", "b", "c"])),
        Case("Mixed pos/neg", lambda: RadarChart([-40, 60, -20, 80], ["a", "b", "c", "d"])),
        Case("All zeros", lambda: RadarChart([0, 0, 0], ["a", "b", "c"])),
        Case("Single axis [42]", lambda: RadarChart([42], ["only"]), suspect=True),
        Case("Two axes", lambda: RadarChart([10, 20], ["a", "b"])),
        Case("All identical", lambda: RadarChart([5, 5, 5, 5], ["a", "b", "c", "d"])),
        Case("Many axes (30)", lambda: RadarChart(list(range(1, 31)), lbls(30)), suspect=True),
        Case("Unicode labels", lambda: RadarChart([10, 20, 30, 5], UNICODE_LABELS)),
        Case("Two series", lambda: RadarChart([[10, 20, 30], [30, 10, 20]], ["a", "b", "c"])),
        Case("Dark theme", lambda: RadarChart([5, 9, 3, 7, 6], lbls(5), theme=DARK, title="Dark radar")),
    ]


@battery("PolarAreaChart")
def _polar():
    return [
        Case("Huge numbers", lambda: PolarAreaChart([1_000_000_000, 999_999_999, 1], ["a", "b", "c"])),
        Case("Tiny decimals", lambda: PolarAreaChart([0.0001, 0.0002, 0.00015], ["a", "b", "c"])),
        Case("Extreme dynamic range", lambda: PolarAreaChart([1, 1000, 1, 5_000_000], ["a", "b", "c", "d"]), suspect=True),
        Case("All zeros", lambda: PolarAreaChart([0, 0, 0], ["a", "b", "c"])),
        Case("Negative (SHOULD error?)", lambda: PolarAreaChart([-50, 30, 90], ["a", "b", "c"])),
        Case("Single data point", lambda: PolarAreaChart([42], ["only"])),
        Case("All identical", lambda: PolarAreaChart([5, 5, 5, 5], ["a", "b", "c", "d"])),
        Case("Many slices (40)", lambda: PolarAreaChart(list(range(1, 41)), lbls(40))),
        Case("Unicode labels", lambda: PolarAreaChart([10, 20, 30, 5], UNICODE_LABELS)),
        Case("Dark theme", lambda: PolarAreaChart([5, 9, 3, 7], ["a", "b", "c", "d"], theme=DARK, title="Dark polar")),
    ]


@battery("Histogram")
def _hist():
    return [
        Case("Huge numbers", lambda: Histogram([1e9, 9.99e8, 1, 5e8, 3e8, 7e8])),
        Case("Tiny decimals", lambda: Histogram([0.0001, 0.0002, 0.00015, 0.0003, 0.00012])),
        Case("Extreme dynamic range", lambda: Histogram([1, 1000, 1, 5_000_000, 2, 3, 4]), suspect=True),
        Case("All negative", lambda: Histogram([-50, -30, -90, -10, -70, -40])),
        Case("Mixed pos/neg", lambda: Histogram([-40, 60, -20, 80, 0, 10, -5])),
        Case("All zeros", lambda: Histogram([0, 0, 0, 0, 0])),
        Case("Single data point", lambda: Histogram([42]), suspect=True),
        Case("All identical", lambda: Histogram([5, 5, 5, 5, 5, 5])),
        Case("300 points normal-ish", lambda: Histogram(many(300))),
        Case("Many bins requested (100)", lambda: Histogram(list(range(200)), bins=100)),
        Case("Dark theme", lambda: Histogram([1, 2, 2, 3, 3, 3, 4, 4, 5], theme=DARK, title="Dark histogram")),
    ]


@battery("BoxPlot")
def _box():
    return [
        Case("Huge numbers", lambda: BoxPlot([[1e9, 9.99e8, 1, 5e8, 3e8]], ["a"])),
        Case("Tiny decimals", lambda: BoxPlot([[0.0001, 0.0002, 0.00015, 0.0003]], ["a"])),
        Case("Extreme dynamic range", lambda: BoxPlot([[1, 1000, 1, 5_000_000, 2]], ["a"]), suspect=True),
        Case("All negative", lambda: BoxPlot([[-50, -30, -90, -10, -70]], ["a"])),
        Case("Mixed pos/neg", lambda: BoxPlot([[-40, 60, -20, 80, 0]], ["a"])),
        Case("All zeros", lambda: BoxPlot([[0, 0, 0, 0, 0]], ["a"])),
        Case("Single value per box", lambda: BoxPlot([[42]], ["a"]), suspect=True),
        Case("All identical", lambda: BoxPlot([[5, 5, 5, 5, 5]], ["a"])),
        Case("Many groups (20)", lambda: BoxPlot([[i, i + 5, i + 10, i + 2, i + 8] for i in range(20)], lbls(20)), suspect=True),
        Case("Mismatched labels (SHOULD error?)", lambda: BoxPlot([[1, 2, 3], [4, 5, 6]], ["only_one"])),
        Case("Dark theme", lambda: BoxPlot([[1, 2, 3, 4, 5], [2, 4, 6, 8, 10]], ["a", "b"], theme=DARK, title="Dark box")),
    ]


@battery("HeatmapChart")
def _heat():
    return [
        Case("Huge numbers", lambda: HeatmapChart([[1e9, 999_999_999], [1, 5e8]], ["x1", "x2"], ["y1", "y2"])),
        Case("Tiny decimals", lambda: HeatmapChart([[0.0001, 0.0002], [0.00015, 0.0003]], ["x1", "x2"], ["y1", "y2"])),
        Case("Extreme dynamic range", lambda: HeatmapChart([[1, 1000], [1, 5_000_000]], ["x1", "x2"], ["y1", "y2"]), suspect=True),
        Case("All negative", lambda: HeatmapChart([[-50, -30], [-90, -10]], ["x1", "x2"], ["y1", "y2"])),
        Case("Mixed pos/neg", lambda: HeatmapChart([[-40, 60], [-20, 80]], ["x1", "x2"], ["y1", "y2"])),
        Case("All zeros", lambda: HeatmapChart([[0, 0], [0, 0]], ["x1", "x2"], ["y1", "y2"])),
        Case("Single cell", lambda: HeatmapChart([[42]], ["x1"], ["y1"])),
        Case("All identical", lambda: HeatmapChart([[5, 5], [5, 5]], ["x1", "x2"], ["y1", "y2"])),
        Case("Large grid 20x20", lambda: HeatmapChart([[(i * j) % 50 for j in range(20)] for i in range(20)], lbls(20), lbls(20)), suspect=True),
        Case("Very long labels", lambda: HeatmapChart([[1, 2], [3, 4]], [LONG_LABEL, "x2"], [LONG_LABEL, "y2"])),
        Case("Ragged rows (SHOULD error?)", lambda: HeatmapChart([[1, 2, 3], [4, 5]], ["x1", "x2", "x3"], ["y1", "y2"])),
        Case("Dark theme", lambda: HeatmapChart([[1, 2, 3], [4, 5, 6], [7, 8, 9]], lbls(3), lbls(3), theme=DARK, title="Dark heatmap")),
    ]


@battery("GanttChart")
def _gantt():
    return [
        Case("Simple int ranges", lambda: GanttChart([(0, 5), (3, 8), (6, 10)], ["Design", "Build", "Ship"])),
        Case("Huge int range", lambda: GanttChart([(0, 1_000_000_000), (1, 999_999_999)], ["a", "b"]), suspect=True),
        Case("Tiny decimal ranges", lambda: GanttChart([(0.0001, 0.0002), (0.0002, 0.0003)], ["a", "b"])),
        Case("Zero-length task (start==end)", lambda: GanttChart([(5, 5), (3, 8)], ["instant", "normal"])),
        Case("Reversed (end<start, SHOULD error?)", lambda: GanttChart([(8, 3)], ["backwards"])),
        Case("Negative times", lambda: GanttChart([(-10, -5), (-5, 0)], ["a", "b"])),
        Case("Single task", lambda: GanttChart([(0, 5)], ["only"])),
        Case("Date ranges", lambda: GanttChart([("2026-01-01", "2026-03-01"), ("2026-02-01", "2026-06-01")], ["Q1", "H1"])),
        Case("Many tasks (40)", lambda: GanttChart([(i, i + 3) for i in range(40)], lbls(40)), suspect=True),
        Case("Very long labels", lambda: GanttChart([(0, 5), (2, 7)], [LONG_LABEL, "short"])),
        Case("Dark theme", lambda: GanttChart([(0, 5), (3, 8), (6, 10)], ["A", "B", "C"], theme=DARK, title="Dark gantt")),
    ]


@battery("ComboChart")
def _combo():
    return [
        Case("Bar + line basic", lambda: ComboChart([{"data": [1, 2, 3], "type": "column"}, {"data": [3, 2, 1], "type": "line"}], ["a", "b", "c"])),
        Case("Huge numbers", lambda: ComboChart([{"data": [1e9, 9.99e8, 1], "type": "column"}, {"data": [1, 2, 3], "type": "line"}], ["a", "b", "c"])),
        Case("Tiny decimals", lambda: ComboChart([{"data": [0.0001, 0.0002, 0.00015], "type": "column"}], ["a", "b", "c"])),
        Case("Extreme dynamic range", lambda: ComboChart([{"data": [1, 1000, 1, 5_000_000], "type": "line"}], ["a", "b", "c", "d"]), suspect=True),
        Case("Wildly diff via secondary axis", lambda: ComboChart([{"data": [1, 2, 3], "type": "column", "axis": "primary"}, {"data": [1e6, 2e6, 3e6], "type": "line", "axis": "secondary"}], ["a", "b", "c"]), suspect=True),
        Case("All zeros", lambda: ComboChart([{"data": [0, 0, 0], "type": "column"}], ["a", "b", "c"])),
        Case("Mixed pos/neg", lambda: ComboChart([{"data": [-40, 60, -20], "type": "column"}, {"data": [10, -5, 30], "type": "line"}], ["a", "b", "c"])),
        Case("Single point", lambda: ComboChart([{"data": [42], "type": "column"}], ["only"])),
        Case("Empty series list (SHOULD error?)", lambda: ComboChart([], ["a", "b"])),
        Case("Area type", lambda: ComboChart([{"data": [3, 7, 4, 9], "type": "area"}, {"data": [9, 4, 7, 3], "type": "line"}], lbls(4))),
        Case("Dark theme", lambda: ComboChart([{"data": [1, 2, 3], "type": "column"}, {"data": [3, 2, 1], "type": "line"}], ["a", "b", "c"], theme=DARK, title="Dark combo")),
    ]


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------
def esc(s: str) -> str:
    return html.escape(s)


def build_html(results: dict[str, list[Result]]) -> str:
    total = sum(len(v) for v in results.values())
    rendered = sum(1 for v in results.values() for r in v if r.error is None)
    errored = total - rendered
    overflow_cases = [
        (t, r) for t, v in results.items() for r in v if r.error is None and r.overflow
    ]
    error_cases = [(t, r) for t, v in results.items() for r in v if r.error is not None]

    parts: list[str] = []
    parts.append("""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>charted gauntlet</title>
<style>
  :root { color-scheme: light dark; }
  body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 0; background:#f5f6f8; color:#1a1a1a; }
  header { background:#0d1b2a; color:#e0e1dd; padding:24px 32px; }
  header h1 { margin:0 0 4px; font-size:22px; }
  header p { margin:0; opacity:.8; font-size:14px; }
  .summary { padding:20px 32px; background:#fff; border-bottom:1px solid #e0e0e0; }
  .stats { display:flex; gap:24px; flex-wrap:wrap; margin-bottom:12px; }
  .stat { font-size:15px; }
  .stat b { font-size:24px; display:block; }
  .ok { color:#1a7f37; } .err { color:#c0392b; } .warn { color:#b8860b; }
  details { margin:6px 0; } summary { cursor:pointer; font-weight:600; }
  .summary ul { margin:6px 0 0; font-size:13px; font-family:ui-monospace, monospace; }
  section { padding:8px 32px 32px; }
  section h2 { border-bottom:2px solid #0d1b2a; padding-bottom:6px; }
  .grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(320px,1fr)); gap:16px; }
  .card { background:#fff; border:1px solid #ddd; border-radius:8px; padding:12px; box-shadow:0 1px 2px rgba(0,0,0,.05); }
  .card.errored { border-color:#c0392b; }
  .card.overflow { border-color:#b8860b; }
  .card .desc { font-size:13px; font-weight:600; margin-bottom:8px; }
  .card .svgwrap { background:#fafafa; border-radius:4px; overflow:auto; text-align:center; }
  .card svg { max-width:100%; height:auto; }
  .card .errmsg { color:#c0392b; font-family:ui-monospace, monospace; font-size:12px; white-space:pre-wrap; background:#fdf0ef; padding:8px; border-radius:4px; }
  .card .of { color:#b8860b; font-size:11px; font-family:ui-monospace, monospace; margin-top:6px; }
  .badge { font-size:10px; padding:2px 6px; border-radius:10px; color:#fff; margin-left:6px; }
  .badge.e { background:#c0392b; } .badge.o { background:#b8860b; } .badge.s { background:#555; }
  nav { padding:8px 32px; background:#fff; border-bottom:1px solid #e0e0e0; font-size:13px; }
  nav a { margin-right:12px; text-decoration:none; color:#0d1b2a; }
</style></head><body>""")

    parts.append(
        f'<header><h1>charted gauntlet</h1>'
        f'<p>Extreme / edge-case stress test across 14 chart types. '
        f'Branch fix/dark-theme-and-ytitle. {total} cases.</p></header>'
    )

    # summary
    parts.append('<div class="summary"><div class="stats">')
    parts.append(f'<div class="stat ok"><b>{rendered}</b>rendered</div>')
    parts.append(f'<div class="stat err"><b>{errored}</b>errored</div>')
    parts.append(f'<div class="stat warn"><b>{len(overflow_cases)}</b>possible overflow</div>')
    parts.append('</div>')

    parts.append('<details open><summary>Errored cases ({})</summary><ul>'.format(len(error_cases)))
    for t, r in error_cases:
        first_line = r.error.splitlines()[0] if r.error else ""
        parts.append(f'<li><b>{esc(t)}</b> — {esc(r.desc)}: <span class="err">{esc(first_line)}</span></li>')
    parts.append('</ul></details>')

    parts.append('<details><summary>Possible visual overflow (text outside viewBox) ({})</summary><ul>'.format(len(overflow_cases)))
    for t, r in overflow_cases:
        parts.append(f'<li><b>{esc(t)}</b> — {esc(r.desc)}: <span class="warn">{esc("; ".join(r.overflow[:3]))}</span></li>')
    parts.append('</ul></details></div>')

    # nav
    parts.append('<nav>' + ' '.join(f'<a href="#{esc(t)}">{esc(t)}</a>' for t in results) + '</nav>')

    # sections
    for t, v in results.items():
        sec_err = sum(1 for r in v if r.error)
        parts.append(f'<section id="{esc(t)}"><h2>{esc(t)} <small style="font-weight:400;font-size:13px;color:#666">({len(v)} cases, {sec_err} errored)</small></h2><div class="grid">')
        for r in v:
            cls = "card"
            badges = ""
            if r.error:
                cls += " errored"
                badges += '<span class="badge e">ERROR</span>'
            if r.overflow:
                cls += " overflow"
                badges += '<span class="badge o">OVERFLOW</span>'
            if r.suspect:
                badges += '<span class="badge s">spot-checked</span>'
            parts.append(f'<div class="{cls}"><div class="desc">{esc(r.desc)}{badges}</div>')
            if r.error:
                parts.append(f'<div class="errmsg">{esc(r.error)}</div>')
            else:
                parts.append(f'<div class="svgwrap">{r.svg}</div>')
                if r.overflow:
                    parts.append('<div class="of">' + esc("; ".join(r.overflow[:4])) + '</div>')
            parts.append('</div>')
        parts.append('</div></section>')

    parts.append('</body></html>')
    return "".join(parts)


def main():
    results: dict[str, list[Result]] = {}
    for name, cases in BATTERIES.items():
        results[name] = [run_case(c) for c in cases]

    out = build_html(results)
    with open("/home/blanky/charted-gauntlet.html", "w", encoding="utf-8") as f:
        f.write(out)

    total = sum(len(v) for v in results.values())
    rendered = sum(1 for v in results.values() for r in v if r.error is None)
    errored = total - rendered
    print(f"TOTAL={total} RENDERED={rendered} ERRORED={errored}")
    print("\n=== ERRORED CASES ===")
    for t, v in results.items():
        for r in v:
            if r.error:
                print(f"[{t}] {r.desc}\n    {r.error.splitlines()[0]}")
    print("\n=== OVERFLOW CASES ===")
    for t, v in results.items():
        for r in v:
            if r.error is None and r.overflow:
                print(f"[{t}] {r.desc}: {r.overflow[0]}")


if __name__ == "__main__":
    main()
