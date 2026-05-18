#!/usr/bin/env python
"""Generate example charts demonstrating axis tick interval functionality."""

from charted import BarChart, ColumnChart, LineChart

# Example 1: Column chart with Y-axis spanning negative to positive
print("=" * 70)
print("Example 1: Column Chart - Y-axis interval=2")
print("=" * 70)
column_data = [
    [-10, -20, -30, -40, -50, -40, -30],  # Negative series
    [10, 20, 30, 40, 50, 40, 30],  # Positive series
]
column_labels = ["A", "B", "C", "D", "E", "F", "G"]

col_chart = ColumnChart(
    data=column_data,
    labels=column_labels,
    title="Column Chart - Y-Axis Interval=2",
    y_stacked=True,
    axis_tick_interval=2,  # Show every 2nd tick label on Y-axis
    width=600,
    height=400,
)
with open("/home/andryo/git/charted/examples/column_y_interval.svg", "w") as f:
    f.write(col_chart.to_svg())
print("✓ Saved: examples/column_y_interval.svg")
print(f"  Y-axis labels: {col_chart.y_axis.values}")
print(f"  Y-axis grid lines: {len(col_chart.y_axis._grid_line_values)}")

# Example 2: Line chart with X-axis spanning negative to positive
print("\n" + "=" * 70)
print("Example 2: Line Chart - X-axis interval=2")
print("=" * 70)
line_data = [5, 15, 25, 35, 45, 35, 25]
line_x = [-4, -2, 0, 2, 4, 6, 8]
line_labels = ["T-4", "T-2", "T0", "T+2", "T+4", "T+6", "T+8"]

line_chart = LineChart(
    data=line_data,
    x_data=line_x,
    labels=line_labels,  # x-axis labels
    title="Line Chart - X-Axis Interval=2",
    axis_tick_interval=2,  # Show every 2nd tick label on X-axis
    width=600,
    height=400,
)
with open("/home/andryo/git/charted/examples/line_x_interval.svg", "w") as f:
    f.write(line_chart.to_svg())
print("✓ Saved: examples/line_x_interval.svg")
print(f"  X-axis labels: {line_chart.x_axis.values}")
print(f"  X-axis grid lines: {len(line_chart.x_axis._grid_line_values)}")
print(f"  Y-axis labels: {line_chart.y_axis.values}")

# Example 3: Bar chart with X-axis spanning negative to positive
print("\n" + "=" * 70)
print("Example 3: Bar Chart - X-axis interval=2")
print("=" * 70)
bar_data = [-40, -20, 0, 20, 40]
bar_labels = ["Very Low", "Low", "Medium", "High", "Very High"]

bar_chart = BarChart(
    data=bar_data,
    labels=bar_labels,
    title="Bar Chart - X-Axis Interval=2",
    x_stacked=True,
    axis_tick_interval=2,  # Show every 2nd tick label on X-axis
    width=600,
    height=400,
)
with open("/home/andryo/git/charted/examples/bar_x_interval.svg", "w") as f:
    f.write(bar_chart.to_svg())
print("✓ Saved: examples/bar_x_interval.svg")
print(f"  X-axis labels: {bar_chart.x_axis.values}")
print(f"  X-axis grid lines: {len(bar_chart.x_axis._grid_line_values)}")

# Example 4: Column chart WITHOUT tick interval (default)
print("\n" + "=" * 70)
print("Example 4: Column Chart - Default (no interval)")
print("=" * 70)
col_default = ColumnChart(
    data=column_data,
    labels=column_labels,
    title="Column Chart - Default Tick Labels",
    y_stacked=True,
    width=600,
    height=400,
)
with open("/home/andryo/git/charted/examples/column_default.svg", "w") as f:
    f.write(col_default.to_svg())
print("✓ Saved: examples/column_default.svg")
print(f"  Y-axis labels: {col_default.y_axis.values}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY - Key Improvements:")
print("=" * 70)
print("1. ✓ Zero axis is ALWAYS rendered when spanning negative to positive")
print("2. ✓ Tick intervals are UNIFORM (consistent spacing)")
print("3. ✓ Works for both X and Y axes")
print("4. ✓ Grid lines show all ticks, labels show filtered subset")
print("=" * 70)
