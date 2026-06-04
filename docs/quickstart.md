# Quick Start

Get up and running with Charted in 5 minutes.

## Installation

```bash
pip install charted
```

**Requirements:** Python 3.10+

## Your First Chart

Create a bar chart in 3 lines:

```python
from charted import BarChart

chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    title="Sales by Quarter"
)
chart.save("sales.svg")
```

That's it! You now have a `sales.svg` file ready to use in presentations, websites, or documentation.

## Try Different Chart Types

Charted supports 14 chart types with a consistent API:

```python
from charted import BarChart, ColumnChart, LineChart, PieChart, RadarChart

# Bar chart (horizontal bars)
BarChart(data=[120, 180, 210], labels=["A", "B", "C"]).save("bar.svg")

# Column chart (vertical bars)
ColumnChart(data=[120, 180, 210], labels=["A", "B", "C"]).save("column.svg")

# Line chart
LineChart(data=[120, 180, 210], labels=["A", "B", "C"]).save("line.svg")

# Pie chart
PieChart(data=[120, 180, 210], labels=["A", "B", "C"]).save("pie.svg")

# Radar chart
RadarChart(data=[120, 180, 210], labels=["A", "B", "C"]).save("radar.svg")
```

## Multi-Series Charts

Compare multiple data series:

```python
from charted import ColumnChart

data = [
    [120, 180, 210, 150],  # 2023
    [130, 190, 220, 160],  # 2024
]

chart = ColumnChart(
    data=data,
    labels=["Q1", "Q2", "Q3", "Q4"],
    series_names=["2023", "2024"],
    title="Sales Comparison"
)
chart.save("multi.svg")
```

## Load Data from CSV

No pandas needed:

```python
from charted import load_csv, BarChart

x, y, labels = load_csv("sales.csv", x_col="Quarter", y_col="Revenue")
chart = BarChart(data=y, labels=x, title=labels[0])
chart.save("sales.svg")
```

**CSV Format:**

```text
Quarter,Revenue
Q1,120
Q2,180
Q3,210
Q4,150
```

## Jupyter Integration

Charts render inline automatically:

```python
from charted import BarChart

# Just create a chart, it displays inline
BarChart(
    data=[120, 180, 210, 150],
    labels=["Q1", "Q2", "Q3", "Q4"],
    title="Sales by Quarter"
)
```

## Apply a Theme

```python
from charted import BarChart

# Built-in themes
chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    theme="dark"  # or "light", "high-contrast"
)

# Or custom theme
chart = BarChart(
    data=[120, 180, 210],
    labels=["Q1", "Q2", "Q3"],
    theme={
        "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1"],
    }
)
```

## Use the CLI

Create charts without writing Python:

```bash
# From CSV
python -m charted create bar sales.svg --data sales.csv

# Batch process
python -m charted batch ./data ./output

# See options
python -m charted --help
```

## Next Steps

- [Explore Chart Types](charts/column): See all 14 chart types
- [Theming Guide](guides/theming): Customize colors and styles
- [Configuration](guides/configuration): Global settings and defaults

---

**Need help?** Check the [full documentation](index) or [report an issue](https://github.com/marzukia/charted/issues).
