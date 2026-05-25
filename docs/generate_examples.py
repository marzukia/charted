"""Generate all baseline SVG examples for the charted documentation.

Run from the repo root:
    python docs/generate_examples.py

All output SVGs are written to docs/examples/.
"""

import math
import os
import random

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

# Single-series bar — app store ratings by category
save(
    "bar.svg",
    BarChart(
        title="Average App Rating by Category",
        data=[4.6, 4.2, 3.8, 4.5, 3.1, 4.0, 4.3],
        labels=["Games", "Social", "News", "Health", "Finance", "Music", "Photo"],
        x_label="Rating (out of 5)",
        width=600,
        height=400,
    ).html,
)

# Multi-series bar — city temperature ranges
save(
    "bar_multi.svg",
    BarChart(
        title="Summer vs Winter Avg. Temperature (°C)",
        data=[
            [35, 28, 22, 14, 8],
            [18, 12, 5, -2, -12],
        ],
        labels=["Dubai", "Sydney", "Tokyo", "London", "Moscow"],
        series_names=["Summer", "Winter"],
        x_label="Temperature (°C)",
        width=600,
        height=400,
    ).html,
)

# Stacked bar — marketing spend by channel
save(
    "bar_stacked.svg",
    BarChart(
        title="Marketing Spend by Channel ($K)",
        data=[
            [45, 60, 55, 70],
            [30, 25, 40, 35],
            [15, 20, 18, 22],
        ],
        labels=["Q1", "Q2", "Q3", "Q4"],
        series_names=["Digital", "Print", "Events"],
        x_stacked=True,
        x_label="Spend ($K)",
        width=600,
        height=350,
    ).html,
)

# Side-by-side bar — export vs import by country
save(
    "bar_sidebyside.svg",
    BarChart(
        title="Trade Balance: Exports vs Imports ($B)",
        data=[
            [320, 180, 95, 210],
            [-280, -195, -110, -165],
        ],
        labels=["China", "Germany", "Australia", "Japan"],
        series_names=["Exports", "Imports"],
        x_label="Value ($B)",
        width=600,
        height=350,
    ).html,
)

# ---------------------------------------------------------------------------
# Column charts
# ---------------------------------------------------------------------------

# Multi-series column (default stacking)
save(
    "column.svg",
    ColumnChart(
        title="Quarterly Revenue by Product Line ($M)",
        data=[
            [12, 18, 22, 28],
            [8, 10, 15, 19],
            [5, 7, 6, 11],
        ],
        labels=["Q1", "Q2", "Q3", "Q4"],
        series_names=["SaaS", "Consulting", "Hardware"],
        y_label="Revenue ($M)",
        width=600,
        height=400,
    ).html,
)

# Stacked column — website traffic sources
save(
    "column_stacked.svg",
    ColumnChart(
        title="Website Traffic by Source (K visits)",
        data=[
            [120, 140, 165, 180, 210],
            [80, 75, 90, 95, 100],
            [40, 55, 60, 70, 85],
        ],
        labels=["Jan", "Feb", "Mar", "Apr", "May"],
        series_names=["Organic", "Paid", "Referral"],
        y_label="Visits (K)",
        width=600,
        height=400,
    ).html,
)

# Side-by-side column — programming language popularity
save(
    "column_sidebyside.svg",
    ColumnChart(
        title="Developer Survey: Language Popularity (%)",
        data=[
            [67, 45, 38, 30, 22],
            [62, 48, 42, 35, 28],
        ],
        labels=["Python", "JavaScript", "Go", "Rust", "TypeScript"],
        series_names=["2024", "2025"],
        y_stacked=False,
        y_label="Respondents (%)",
        width=600,
        height=400,
    ).html,
)

# ---------------------------------------------------------------------------
# Line charts
# ---------------------------------------------------------------------------

# Multi-series line — stock price comparison (normalized)
save(
    "line.svg",
    LineChart(
        title="Stock Price (Normalized to 100)",
        data=[
            [100, 105, 98, 112, 120, 115, 125, 130, 128, 140, 138, 150],
            [100, 97, 102, 108, 104, 110, 115, 112, 118, 122, 125, 130],
            [100, 103, 106, 104, 108, 112, 110, 115, 120, 118, 122, 128],
        ],
        labels=[
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ],
        series_names=["ACME Corp", "Globex Inc", "Initech"],
        width=600,
        height=400,
    ).html,
)

# XY mode line (temperature anomaly)
years = list(range(1990, 2010))
anomalies = [
    -15, -5, 10, 20, 5, 25, 15, 30, 10, 20,
    40, 25, 45, 30, 50, 35, 60, 55, 45, 70,
]
baseline = [round(5 + 2 * math.sin(i * 0.4) + i * 0.5, 1) for i in range(len(years))]
save(
    "xy_line.svg",
    LineChart(
        title="Temperature Anomaly vs 5-Year Rolling Baseline (1990-2009)",
        data=[anomalies, baseline],
        x_data=years,
        labels=[str(y) for y in years],
        width=600,
        height=400,
    ).html,
)


# Single-series line — monthly coffee shop revenue
save(
    "line_single.svg",
    LineChart(
        title="Monthly Revenue — Corner Coffee Co. ($K)",
        data=[[18, 22, 19, 25, 28, 32, 35, 38, 30, 27, 24, 42]],
        labels=[
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ],
        series_names=["Revenue"],
        y_label="Revenue ($K)",
        h_lines=[28.3],
        data_labels=[
            "", "", "", "", "", "",
            "", "", "", "", "", "$42K",
        ],
        width=600,
        height=400,
    ).html,
)

# ---------------------------------------------------------------------------
# Scatter charts
# ---------------------------------------------------------------------------

# Multi-series scatter — employee performance quadrant analysis
random.seed(42)
# High performers
hp_x = [round(65 + random.gauss(0, 8), 1) for _ in range(12)]
hp_y = [round(70 + random.gauss(0, 10), 1) for _ in range(12)]
# Growth potential
gp_x = [round(35 + random.gauss(0, 8), 1) for _ in range(12)]
gp_y = [round(65 + random.gauss(0, 10), 1) for _ in range(12)]
# Steady contributors
sc_x = [round(60 + random.gauss(0, 10), 1) for _ in range(12)]
sc_y = [round(35 + random.gauss(0, 8), 1) for _ in range(12)]

save(
    "scatter.svg",
    ScatterChart(
        title="Employee Performance Quadrant",
        x_data=[hp_x, gp_x, sc_x],
        y_data=[hp_y, gp_y, sc_y],
        series_names=["High Performers", "Growth Potential", "Steady Contributors"],
        x_label="Skills Score",
        y_label="Engagement Score",
        h_lines=[50.0],
        v_lines=[50.0],
        quadrant_labels=[
            "Disengaged Experts",
            "Stars",
            "At Risk",
            "Rising Talent",
        ],
        width=600,
        height=500,
    ).html,
)

# Single-series scatter — house price vs square footage with data labels
random.seed(7)
cities = [
    "Austin", "Denver", "Portland", "Nashville", "Raleigh",
    "Boise", "Tampa", "Phoenix", "Atlanta", "Seattle",
]
sqft = [1200, 1450, 1600, 1800, 2000, 2200, 2500, 2800, 3100, 3500]
prices = [round(180 + (s - 1200) * 0.12 + random.gauss(0, 30), 0) for s in sqft]
save(
    "scatter_single.svg",
    ScatterChart(
        title="Home Price vs Size — Mid-Market Cities",
        x_data=sqft,
        y_data=prices,
        series_names=["Median Price"],
        data_labels=cities,
        x_label="Square Footage",
        y_label="Price ($K)",
        width=600,
        height=450,
    ).html,
)

# ---------------------------------------------------------------------------
# Pie / Doughnut charts
# ---------------------------------------------------------------------------

# Basic pie
save(
    "pie.svg",
    PieChart(
        title="Global Cloud Market Share (2025)",
        data=[33, 22, 10, 8, 27],
        labels=["AWS", "Azure", "GCP", "Alibaba", "Others"],
        width=550,
        height=450,
    ).html,
)

# Doughnut
save(
    "pie_doughnut.svg",
    PieChart(
        title="Time Spent Per Day (hours)",
        data=[8, 7, 2, 3, 2, 2],
        labels=["Sleep", "Work", "Exercise", "Commute", "Cooking", "Leisure"],
        inner_radius=0.5,
        width=550,
        height=450,
    ).html,
)

# ---------------------------------------------------------------------------
# Radar charts
# ---------------------------------------------------------------------------

# Single-series radar
save(
    "radar.svg",
    RadarChart(
        title="Frontend Framework Evaluation",
        data=[85, 70, 90, 60, 75, 80],
        labels=["Performance", "Ecosystem", "DX", "Bundle Size", "TypeScript", "Community"],
        width=550,
        height=450,
    ).html,
)

# Multi-series radar — comparing two athletes
save(
    "radar_multi.svg",
    RadarChart(
        title="Athlete Comparison: Sprint vs Endurance",
        data=[[92, 65, 55, 80, 70], [60, 90, 95, 65, 85]],
        labels=["Speed", "Stamina", "Recovery", "Power", "Agility"],
        series_names=["Sprinter", "Marathoner"],
        width=550,
        height=450,
    ).html,
)

# ---------------------------------------------------------------------------
# Area charts
# ---------------------------------------------------------------------------

# Single-series area — daily step count over a month
random.seed(99)
steps = [round(6000 + 4000 * math.sin(i * 0.45) + random.gauss(0, 800)) for i in range(30)]
save(
    "area.svg",
    AreaChart(
        title="Daily Step Count — April 2025",
        data=steps,
        labels=[str(d + 1) for d in range(30)],
        width=600,
        height=380,
    ).html,
)

# Multi-series area — energy production by source
save(
    "area_multi.svg",
    AreaChart(
        title="Energy Production by Source (GWh)",
        data=[
            [120, 125, 130, 140, 155, 170, 180, 190],
            [80, 90, 95, 100, 110, 115, 125, 135],
            [60, 55, 50, 48, 45, 40, 38, 35],
        ],
        labels=["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"],
        series_names=["Solar", "Wind", "Coal"],
        width=600,
        height=400,
    ).html,
)

# ---------------------------------------------------------------------------
# Box plot
# ---------------------------------------------------------------------------

random.seed(42)
box_a = [round(random.gauss(50, 10), 1) for _ in range(50)] + [95, 5, 102]
box_b = [round(random.gauss(70, 15), 1) for _ in range(50)] + [120, 30, 130]
box_c = [round(random.gauss(30, 8), 1) for _ in range(50)] + [55, 8, 60]
save(
    "boxplot.svg",
    BoxPlot(
        title="Response Time by Server Region (ms)",
        data=[box_a, box_b, box_c],
        labels=["US-East", "EU-West", "AP-South"],
        width=600,
        height=400,
    ).html,
)

# ---------------------------------------------------------------------------
# Histogram
# ---------------------------------------------------------------------------

random.seed(42)
hist_data = [random.gauss(50, 15) for _ in range(500)]
save(
    "histogram.svg",
    Histogram(
        title="Exam Score Distribution (500 Students)",
        data=hist_data,
        bins=10,
        width=600,
        height=400,
    ).html,
)

# ---------------------------------------------------------------------------
# Heatmap
# ---------------------------------------------------------------------------

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
        x_labels=[
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ],
        y_labels=["Dubai", "Sydney", "Tokyo", "Berlin", "Moscow"],
        width=600,
        height=400,
        low_color="#21639e",
        high_color="#f97316",
        show_values=True,
        value_format=".0f",
    ).html,
)

# ---------------------------------------------------------------------------
# Gantt chart
# ---------------------------------------------------------------------------

save(
    "gantt.svg",
    GanttChart(
        title="Product Launch Timeline — Q1 2026",
        data=[(0, 2), (1, 4), (3, 6), (5, 8), (6, 9)],
        labels=["Research", "Design", "Development", "QA", "Launch"],
        width=600,
        height=380,
        dependencies=[(0, 1), (0, 2), (2, 3), (3, 4)],
        show_today_line=True,
        x_position=4.5,
    ).html,
)

print("Done — all examples written to docs/examples/")
