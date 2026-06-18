"""
Generate all landing page charts for charted's redesigned index.
Outputs SVGs to docs/_static/landing/.
Run from repo root: python docs/_scripts/generate_landing_charts.py
"""
import math
import random
import sys
import os

sys.path.insert(0, os.path.abspath("."))

from charted.charts import (
    ColumnChart, BarChart, LineChart, ScatterChart, PieChart,
    RadarChart, AreaChart, BubbleChart, ComboChart, HeatmapChart,
    GanttChart, Histogram, PolarAreaChart, BoxPlot,
)

OUT = "docs/_static/landing"
os.makedirs(OUT, exist_ok=True)

# Brand palette theme — vivid but cohesive
BRAND_COLORS = ["#5fab9e", "#db504a", "#f7dd72", "#f58b51", "#2e4756", "#7ec8bc", "#e87a74", "#f9e99a"]

BASE_THEME = {
    "colors": BRAND_COLORS,
    "background_color": "#ffffff",
    "grid_color": "#e8edf0",
    "title_color": "#2e4756", "root_color": "#2e4756", "legend_font_color": "#2e4756",
    "title_font_size": 15,
    "axis_label_font_size": 11,
}

def t(**overrides):
    d = dict(BASE_THEME)
    d.update(overrides)
    return d

# ─── HERO: Multi-series AreaChart — monthly active users by plan ───────────
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
free_mau    = [1200, 1380, 1520, 1740, 1900, 2100, 2280, 2450, 2600, 2830, 3050, 3400]
pro_mau     = [340,  420,  500,  610,  720,  860,  980, 1090, 1240, 1380, 1520, 1710]
ent_mau     = [45,   62,   78,   95,  115,  138,  162,  189,  218,  250,  285,  325]

chart = AreaChart(
    title="Monthly Active Users by Plan",
    data=[free_mau, pro_mau, ent_mau],
    labels=months,
    series_names=["Free", "Pro", "Enterprise"],
    width=820, height=420,
    theme=t(),
)
chart.save(f"{OUT}/hero.svg")
print("hero.svg ok")

# ─── CODE DEMO 1: BarChart (single series, 3 lines of code) ─────────────────
chart = BarChart(
    title="Revenue by Region ($M)",
    data=[4.2, 7.8, 6.1, 9.3, 5.5, 8.7],
    labels=["APAC", "North Am", "Europe", "LatAm", "MEA", "ANZ"],
    width=560, height=340,
    theme=t(),
)
chart.save(f"{OUT}/demo_bar.svg")
print("demo_bar.svg ok")

# ─── CODE DEMO 2: LineChart (multi-series) ───────────────────────────────────
n = 12
api_p50  = [42, 45, 41, 48, 52, 49, 44, 47, 53, 50, 46, 43]
api_p95  = [88, 94, 87, 102, 118, 107, 91, 98, 122, 115, 95, 89]
api_p99  = [165, 182, 155, 198, 247, 223, 171, 188, 261, 234, 192, 168]

chart = LineChart(
    title="API Latency Percentiles (ms)",
    data=[api_p50, api_p95, api_p99],
    labels=months,
    series_names=["p50", "p95", "p99"],
    width=560, height=340,
    theme=t(),
)
chart.save(f"{OUT}/demo_line.svg")
print("demo_line.svg ok")

# ─── CODE DEMO 3: ComboChart (column + line) ─────────────────────────────────
chart = ComboChart(
    title="Revenue vs Net Margin",
    series=[
        {"data": [2.1, 2.8, 3.4, 2.9, 3.8, 4.2, 3.9, 4.7], "type": "column", "name": "Revenue ($M)"},
        {"data": [8.2, 11.4, 13.8, 10.2, 15.1, 17.3, 14.9, 19.2], "type": "line", "name": "Margin %", "axis": "secondary"},
    ],
    labels=["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8"],
    width=560, height=340,
    theme=t(),
)
chart.save(f"{OUT}/demo_combo.svg")
print("demo_combo.svg ok")

# ─── GALLERY 1: ColumnChart — quarterly sales by segment ─────────────────────
chart = ColumnChart(
    title="Quarterly Sales by Segment ($M)",
    data=[
        [12.4, 15.8, 18.2, 21.1],
        [8.7, 10.2, 11.9, 14.3],
        [4.1, 5.6, 7.2, 8.8],
    ],
    labels=["Q1", "Q2", "Q3", "Q4"],
    series_names=["Enterprise", "Mid-Market", "SMB"],
    width=560, height=360,
    theme=t(),
)
chart.save(f"{OUT}/gallery_column.svg")
print("gallery_column.svg ok")

# ─── GALLERY 2: BarChart — latency by service ────────────────────────────────
chart = BarChart(
    title="P95 Latency by Service (ms)",
    data=[12, 38, 24, 67, 19, 88, 31, 45, 15, 72],
    labels=["auth", "search", "recommend", "media", "notify", "ml-infer", "checkout", "payment", "cdn", "analytics"],
    width=560, height=360,
    theme=t(),
)
chart.save(f"{OUT}/gallery_bar.svg")
print("gallery_bar.svg ok")

# ─── GALLERY 3: LineChart — stock index performance ──────────────────────────
random.seed(7)
weeks = [f"W{i+1}" for i in range(24)]
idx_a = [100]
idx_b = [100]
idx_c = [100]
for _ in range(23):
    idx_a.append(round(idx_a[-1] * (1 + random.gauss(0.008, 0.025)), 2))
    idx_b.append(round(idx_b[-1] * (1 + random.gauss(0.004, 0.018)), 2))
    idx_c.append(round(idx_c[-1] * (1 + random.gauss(0.012, 0.035)), 2))

chart = LineChart(
    title="Index Performance (rebased 100)",
    data=[idx_a, idx_b, idx_c],
    labels=weeks,
    series_names=["Growth", "Blend", "Aggressive"],
    width=560, height=360,
    theme=t(),
)
chart.save(f"{OUT}/gallery_line.svg")
print("gallery_line.svg ok")

# ─── GALLERY 4: ScatterChart — engineering effort vs impact ──────────────────
random.seed(42)
effort_a = [random.uniform(5, 40) for _ in range(18)]
impact_a = [e * 1.8 + random.gauss(0, 12) for e in effort_a]
effort_b = [random.uniform(30, 90) for _ in range(18)]
impact_b = [e * 0.9 + random.gauss(0, 15) for e in effort_b]

chart = ScatterChart(
    title="Engineering Effort vs Business Impact",
    x_data=[effort_a, effort_b],
    y_data=[impact_a, impact_b],
    series_names=["Quick wins", "Large projects"],
    width=560, height=360,
    theme=t(),
)
chart.save(f"{OUT}/gallery_scatter.svg")
print("gallery_scatter.svg ok")

# ─── GALLERY 5: PieChart — cloud spend by provider ───────────────────────────
chart = PieChart(
    title="Cloud Spend by Provider",
    data=[44, 31, 14, 8, 3],
    labels=["AWS", "GCP", "Azure", "Self-hosted", "Other"],
    width=520, height=380,
    theme=t(),
)
chart.save(f"{OUT}/gallery_pie.svg")
print("gallery_pie.svg ok")

# ─── GALLERY 6: RadarChart — product team competencies ───────────────────────
chart = RadarChart(
    title="Team Competency Profile",
    data=[
        [82, 91, 74, 88, 79, 95],
        [68, 75, 92, 70, 88, 72],
    ],
    labels=["Delivery", "Quality", "Security", "Perf", "UX", "Collab"],
    series_names=["Frontend", "Backend"],
    width=520, height=380,
    theme=t(),
)
chart.save(f"{OUT}/gallery_radar.svg")
print("gallery_radar.svg ok")

# ─── GALLERY 7: AreaChart — web traffic by channel ───────────────────────────
chart = AreaChart(
    title="Daily Web Traffic by Channel (K sessions)",
    data=[
        [18, 22, 19, 26, 31, 28, 24, 29, 35, 32, 27, 33],
        [8, 10, 9, 12, 14, 13, 11, 13, 16, 15, 12, 14],
        [4, 5, 4, 6, 7, 7, 6, 7, 8, 8, 6, 7],
    ],
    labels=months,
    series_names=["Organic", "Paid", "Referral"],
    width=560, height=360,
    theme=t(),
)
chart.save(f"{OUT}/gallery_area.svg")
print("gallery_area.svg ok")

# ─── GALLERY 8: BubbleChart — market size vs growth vs penetration ───────────
chart = BubbleChart(
    title="Market Segments: Size vs Growth vs Penetration",
    x_data=[12, 28, 45, 18, 72, 35, 58, 22],
    y_data=[18, 32, 8, 45, 12, 28, 22, 38],
    sizes=[120, 280, 450, 90, 680, 210, 380, 150],
    series_names=["Segments"],
    width=560, height=360,
    theme=t(),
)
chart.save(f"{OUT}/gallery_bubble.svg")
print("gallery_bubble.svg ok")

# ─── GALLERY 9: ComboChart — revenue + margin ────────────────────────────────
chart = ComboChart(
    title="Quarterly Revenue & Gross Margin",
    series=[
        {"data": [8.2, 9.7, 11.4, 10.8, 12.9, 14.2, 13.1, 15.8], "type": "column", "name": "Revenue ($M)"},
        {"data": [38.2, 41.5, 44.1, 42.8, 46.3, 48.9, 45.7, 51.2], "type": "line", "name": "Gross Margin %", "axis": "secondary"},
    ],
    labels=["Q1 '23", "Q2 '23", "Q3 '23", "Q4 '23", "Q1 '24", "Q2 '24", "Q3 '24", "Q4 '24"],
    width=560, height=360,
    theme=t(),
)
chart.save(f"{OUT}/gallery_combo.svg")
print("gallery_combo.svg ok")

# ─── GALLERY 10: HeatmapChart — API error rates by hour/day ─────────────────
random.seed(99)
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
hours = [f"{h:02d}:00" for h in range(0, 24, 2)]
heatmap_data = []
for d in range(7):
    row = []
    for h in range(12):
        base = 0.2 if (d >= 5) else (0.8 if (7 <= h <= 10) else 0.3)
        row.append(round(base + random.uniform(-0.15, 0.25), 2))
    heatmap_data.append(row)

chart = HeatmapChart(
    title="API Error Rate (%) by Day & Hour",
    data=heatmap_data,
    x_labels=hours,
    y_labels=days,
    width=580, height=360,
    low_color="#e8f5f2",
    high_color="#db504a",
    show_values=True,
    value_format=".2f",
    theme=t(background_color="#ffffff"),
)
chart.save(f"{OUT}/gallery_heatmap.svg")
print("gallery_heatmap.svg ok")

# ─── GALLERY 11: GanttChart — product launch timeline ────────────────────────
chart = GanttChart(
    title="Product Launch Timeline: Q3–Q4 2026",
    data=[(0, 3), (1, 5), (2, 7), (4, 9), (6, 10), (8, 11), (9, 12)],
    labels=["Discovery", "Design", "Engineering", "Alpha", "Beta", "QA", "Launch"],
    width=580, height=360,
    dependencies=[(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)],
    show_today_line=True,
    x_position=7.5,
    theme=t(),
)
chart.save(f"{OUT}/gallery_gantt.svg")
print("gallery_gantt.svg ok")

# ─── GALLERY 12: Histogram — response time distribution ──────────────────────
random.seed(22)
response_times = (
    [random.gauss(120, 25) for _ in range(400)]
    + [random.gauss(280, 40) for _ in range(80)]
    + [random.gauss(500, 60) for _ in range(20)]
)

chart = Histogram(
    title="HTTP Response Time Distribution (ms)",
    data=response_times,
    bins=16,
    width=560, height=360,
    theme=t(),
)
chart.save(f"{OUT}/gallery_histogram.svg")
print("gallery_histogram.svg ok")

# ─── GALLERY 13: PolarAreaChart — NPS score distribution ─────────────────────
chart = PolarAreaChart(
    title="NPS Score Distribution",
    data=[42, 28, 18, 32, 55, 61, 49, 38, 72, 84, 91],
    labels=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
    width=520, height=380,
    theme=t(),
)
chart.save(f"{OUT}/gallery_polar.svg")
print("gallery_polar.svg ok")

# ─── GALLERY 14: BoxPlot — deployment duration by environment ────────────────
random.seed(55)
prod_times   = sorted([round(abs(random.gauss(8.5, 2.1)), 1) for _ in range(60)])
staging_times = sorted([round(abs(random.gauss(4.2, 1.4)), 1) for _ in range(60)])
dev_times    = sorted([round(abs(random.gauss(2.1, 0.8)), 1) for _ in range(60)])

chart = BoxPlot(
    title="Deployment Duration by Environment (min)",
    data=[prod_times, staging_times, dev_times],
    labels=["Production", "Staging", "Development"],
    width=560, height=360,
    theme=t(),
)
chart.save(f"{OUT}/gallery_boxplot.svg")
print("gallery_boxplot.svg ok")

print(f"\nAll charts saved to {OUT}/")
