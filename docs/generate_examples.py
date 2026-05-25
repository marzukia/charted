"""Generate all baseline SVG examples for the charted documentation.

Run from the repo root:
    python docs/generate_examples.py

All output SVGs are written to docs/examples/.
"""

import math
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "examples")
os.makedirs(OUTPUT_DIR, exist_ok=True)

from charted.charts import (
    AreaChart,
    BarChart,
    BoxPlot,
    ColumnChart,
    GanttChart,
    HeatmapChart,
    Histogram,
    LineChart,
    PieChart,
    RadarChart,
    ScatterChart,
)


def save(name: str, svg: str) -> None:
    path = os.path.join(OUTPUT_DIR, name)
    with open(path, "w") as f:
        f.write(svg)
    print(f"  wrote {name}")


# ---------------------------------------------------------------------------
# Bar charts
# ---------------------------------------------------------------------------

# Single-series bar
save(
    "bar.svg",
    BarChart(
        title="Profit/Loss by Region ($M)",
        data=[-12, 34, -8, 52, -5, 28, 41, -19, 15, 60],
        labels=[
            "North",
            "South",
            "East",
            "West",
            "Central",
            "Pacific",
            "Atlantic",
            "Mountain",
            "Plains",
            "Metro",
        ],
        width=700,
        height=500,
    ).html,
)

# Multi-series bar (grouped / side-by-side)
save(
    "bar_multi.svg",
    BarChart(
        title="Revenue vs Expenses by Quarter ($K)",
        data=[
            [120, -45, 180, -30, 210, -60],
            [-80, -20, -95, -15, -110, -25],
        ],
        labels=["Q1 Prod", "Q1 Ops", "Q2 Prod", "Q2 Ops", "Q3 Prod", "Q3 Ops"],
        width=700,
        height=500,
    ).html,
)

# Stacked bar
save(
    "bar_stacked.svg",
    BarChart(
        title="Budget by Department ($K)",
        data=[
            [100, -50, 120],
            [80, 60, -40],
        ],
        labels=["Q1", "Q2", "Q3"],
        series_names=["Revenue", "Expenses"],
        x_stacked=True,
        width=700,
        height=400,
    ).html,
)

# Side-by-side bar
save(
    "bar_sidebyside.svg",
    BarChart(
        title="Revenue vs Expenses by Quarter ($K)",
        data=[
            [120, 180, 210],
            [-80, -95, -110],
        ],
        labels=["Q1", "Q2", "Q3"],
        series_names=["Revenue", "Expenses"],
        width=700,
        height=400,
    ).html,
)

# ---------------------------------------------------------------------------
# Column charts
# ---------------------------------------------------------------------------

# Multi-series column (default stacking)
save(
    "column.svg",
    ColumnChart(
        title="Year-over-Year Growth Rate (%) by Segment",
        data=[
            [12, -8, 22, 18, -5, 30],
            [-3, -15, 5, -2, -20, 8],
            [9, -23, 17, 16, -25, 38],
        ],
        labels=["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"],
        width=700,
        height=500,
        theme={
            "v_padding": 0.12,
            "h_padding": 0.10,
        },
    ).html,
)

# Stacked column
save(
    "column_stacked.svg",
    ColumnChart(
        title="Year-over-Year Growth by Segment",
        data=[
            [12, 22, 30],
            [-8, -15, -20],
            [4, 7, 10],
        ],
        labels=["Q1", "Q2", "Q3"],
        series_names=["Revenue", "Costs", "Net"],
        width=700,
        height=400,
    ).html,
)

# Side-by-side column
save(
    "column_sidebyside.svg",
    ColumnChart(
        title="Sales Performance by Region",
        data=[
            [45, 52, 38, 61],
            [38, 46, 52, 49],
            [52, 39, 46, 51],
        ],
        labels=["Q1", "Q2", "Q3", "Q4"],
        series_names=["North", "South", "East"],
        width=700,
        height=400,
        y_stacked=False,
    ).html,
)

# ---------------------------------------------------------------------------
# Line charts
# ---------------------------------------------------------------------------

n = 20

# Multi-series line
save(
    "line.svg",
    LineChart(
        title="Signal Analysis: Raw vs Filtered vs Baseline",
        data=[
            [math.sin(i * 0.5) * 30 + (i % 7 - 3) * 5 for i in range(n)],
            [math.sin(i * 0.5) * 25 for i in range(n)],
            [math.sin(i * 0.5) * 10 - 5 for i in range(n)],
        ],
        labels=[str(i) for i in range(n)],
        width=700,
        height=400,
    ).html,
)

# XY mode line (temperature anomaly)
years = list(range(1990, 2010))
anomalies = [
    -15,
    -5,
    10,
    20,
    5,
    25,
    15,
    30,
    10,
    20,
    40,
    25,
    45,
    30,
    50,
    35,
    60,
    55,
    45,
    70,
]
# Baseline as a moving average trend instead of flat zero
baseline = [round(5 + 2 * math.sin(i * 0.4) + i * 0.5, 1) for i in range(len(years))]
save(
    "xy_line.svg",
    LineChart(
        title="Temperature Anomaly vs 5-Year Rolling Baseline (1990-2009)",
        data=[anomalies, baseline],
        x_data=years,
        labels=[str(y) for y in years],
        width=700,
        height=400,
    ).html,
)


# Single-series line
save(
    "line_single.svg",
    LineChart(
        title="Monthly Active Users (K)",
        data=[[42, 48, 55, 61, 58, 70, 80, 78, 85, 92, 88, 100]],
        labels=[
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ],
        series_names=["MAU"],
        width=700,
        height=400,
    ).html,
)

# ---------------------------------------------------------------------------
# Scatter charts
# ---------------------------------------------------------------------------

# Multi-series scatter — two distinct clusters with noise
import random

random.seed(42)
cluster_a_x = [30 + random.gauss(0, 8) for _ in range(20)]
cluster_a_y = [40 + random.gauss(0, 8) for _ in range(20)]
cluster_b_x = [70 + random.gauss(0, 10) for _ in range(20)]
cluster_b_y = [20 + random.gauss(0, 10) for _ in range(20)]
save(
    "scatter.svg",
    ScatterChart(
        title="Cluster Analysis — Two Distinct Populations",
        x_data=[cluster_a_x, cluster_b_x],
        y_data=[cluster_a_y, cluster_b_y],
        series_names=["Cluster A", "Cluster B"],
        width=700,
        height=400,
    ).html,
)

# Single-series scatter — quadratic relationship with spread
random.seed(1)
x_vals = [i for i in range(5, 95, 5)]
y_vals = [round(10 + (v - 50) ** 2 / 50 + random.gauss(0, 4), 1) for v in x_vals]
save(
    "scatter_single.svg",
    ScatterChart(
        title="U-Shaped Response Curve — Signal vs Input",
        x_data=x_vals,
        y_data=y_vals,
        series_names=["Observations"],
        width=700,
        height=400,
    ).html,
)

# ---------------------------------------------------------------------------
# Pie / Doughnut charts
# ---------------------------------------------------------------------------

# Basic pie
save(
    "pie.svg",
    PieChart(
        title="Market Share by Product Line",
        data=[35, 28, 18, 12, 7],
        labels=["Product A", "Product B", "Product C", "Product D", "Other"],
        width=600,
        height=500,
    ).html,
)

# Doughnut
save(
    "pie_doughnut.svg",
    PieChart(
        title="Operating System Market Share",
        data=[72, 15, 8, 5],
        labels=["Windows", "macOS", "Linux", "Other"],
        inner_radius=0.5,
        width=600,
        height=500,
    ).html,
)

# ---------------------------------------------------------------------------
# Radar charts
# ---------------------------------------------------------------------------

# Single-series radar
save(
    "radar.svg",
    RadarChart(
        title="Character Stats Comparison",
        data=[20, 35, 30, 45, 25],
        labels=["Speed", "Power", "Endurance", "Defense", "Skill"],
        width=600,
        height=500,
    ).html,
)

# Multi-series radar
save(
    "radar_multi.svg",
    RadarChart(
        title="Player Comparison",
        data=[[20, 35, 30, 45, 25], [30, 25, 40, 35, 30]],
        labels=["Speed", "Power", "Endurance", "Defense", "Skill"],
        series_names=["Player A", "Player B"],
        width=600,
        height=500,
    ).html,
)

# ---------------------------------------------------------------------------
# Area charts
# ---------------------------------------------------------------------------

# Single-series area — CPU temperature over a day
temps = [42 + 10 * math.sin(i * 0.6) + (hash(str(i)) % 5 - 2) * 1.5 for i in range(24)]
save(
    "area.svg",
    AreaChart(
        title="CPU Temperature (°C) — 24-hour Cycle",
        data=[round(t, 1) for t in temps],
        labels=[f"{h}:00" for h in range(24)],
        width=700,
        height=400,
    ).html,
)

# Multi-series area
save(
    "area_multi.svg",
    AreaChart(
        title="Multi-series Area — Revenue by Channel",
        data=[
            [30, 50, 45, 60, 70, 80, 65, 55],
            [20, 35, 30, 45, 50, 55, 40, 35],
        ],
        labels=["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8"],
        series_names=["Online", "Retail"],
        width=700,
        height=400,
    ).html,
)

# ---------------------------------------------------------------------------
# Box plot
# ---------------------------------------------------------------------------

# Box plot with clear quartiles and outliers
random.seed(42)
box_a = [round(random.gauss(50, 10), 1) for _ in range(50)] + [95, 5, 102]
box_b = [round(random.gauss(70, 15), 1) for _ in range(50)] + [120, 30, 130]
box_c = [round(random.gauss(30, 8), 1) for _ in range(50)] + [55, 8, 60]
save(
    "boxplot.svg",
    BoxPlot(
        title="Test Scores by Group — with Outliers",
        data=[box_a, box_b, box_c],
        labels=["Group A", "Group B", "Group C"],
        width=700,
        height=400,
    ).html,
)

# ---------------------------------------------------------------------------
# Histogram
# ---------------------------------------------------------------------------

# Histogram — 10-bin normal distribution (bell curve)
random.seed(42)
hist_data = [random.gauss(50, 15) for _ in range(500)]
save(
    "histogram.svg",
    Histogram(
        title="Exam Scores — Normal Distribution (500 Students, 10 Bins)",
        data=hist_data,
        bins=10,
        width=700,
        height=400,
    ).html,
)

# ---------------------------------------------------------------------------
# Heatmap
# ---------------------------------------------------------------------------

# Heatmap — monthly temperature matrix (°C)
save(
    "heatmap.svg",
    HeatmapChart(
        title="Average Temperature (°C) — Monthly by City",
        data=[
            [35, 36, 38, 40, 43, 45, 47, 46, 44, 41, 38, 36],
            [22, 24, 28, 32, 36, 40, 42, 41, 38, 33, 27, 23],
            [15, 18, 22, 27, 32, 37, 40, 39, 35, 29, 22, 17],
            [5, 8, 14, 20, 26, 32, 35, 34, 29, 22, 14, 7],
            [-2, 2, 10, 18, 25, 31, 34, 33, 27, 19, 10, 3],
        ],
        x_labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        y_labels=["Dubai", "Sydney", "Tokyo", "Berlin", "Moscow"],
        width=700,
        height=450,
        low_color="#21639e",
        high_color="#f97316",
        show_values=True,
        value_format=".0f",
    ).html,
)

# ---------------------------------------------------------------------------
# Gantt chart
# ---------------------------------------------------------------------------

# Gantt — software project timeline
save(
    "gantt.svg",
    GanttChart(
        title="Software Project Timeline — Q1 2026",
        data=[(0, 2), (1, 4), (3, 6), (5, 8), (6, 9)],
        labels=["Design", "Frontend", "Backend", "Testing", "Deployment"],
        width=700,
        height=400,
        dependencies=[(0, 1), (0, 2), (2, 3), (3, 4)],
        show_today_line=True,
        x_position=4.5,
    ).html,
)

print("Done — all examples written to docs/examples/")
