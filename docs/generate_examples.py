"""Generate all baseline SVG examples for the charted documentation.

Run from the repo root:
    python docs/generate_examples.py

All output SVGs are written to docs/examples/.
"""

import math
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "examples")
os.makedirs(OUTPUT_DIR, exist_ok=True)

from charted.charts import BarChart, ColumnChart, LineChart, ScatterChart, PieChart


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
        labels=["North", "South", "East", "West", "Central", "Pacific", "Atlantic", "Mountain", "Plains", "Metro"],
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
            "padding": {
                "v_padding": 0.12,
                "h_padding": 0.10,
            }
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
anomalies = [-15, -5, 10, 20, 5, 25, 15, 30, 10, 20, 40, 25, 45, 30, 50, 35, 60, 55, 45, 70]
save(
    "xy_line.svg",
    LineChart(
        title="Temperature Anomaly vs Baseline (1990-2009)",
        data=[anomalies, [0] * len(years)],
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
        labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        series_names=["MAU"],
        width=700,
        height=400,
    ).html,
)

# ---------------------------------------------------------------------------
# Scatter charts
# ---------------------------------------------------------------------------

# Multi-series scatter
save(
    "scatter.svg",
    ScatterChart(
        title="Correlation Analysis",
        x_data=[[0, 10, 20, 30, 40, 50], [5, 15, 25, 35, 45, 55]],
        y_data=[[10, 20, 30, 40, 50, 60], [15, 25, 35, 50, 60, 70]],
        series_names=["Group A", "Group B"],
        width=700,
        height=400,
    ).html,
)

# Single-series scatter
save(
    "scatter_single.svg",
    ScatterChart(
        title="Height vs Weight Distribution",
        x_data=[160, 165, 170, 172, 175, 178, 180, 182, 185, 188, 190],
        y_data=[55, 60, 65, 68, 72, 75, 78, 80, 85, 88, 92],
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
        doughnut=True,
        inner_radius=0.5,
        width=600,
        height=500,
    ).html,
)

print("Done — all examples written to docs/examples/")
