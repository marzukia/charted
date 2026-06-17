"""Plot two series on the same chart.

Pass a list of lists as data and name each series with series_names.
Bar and column charts group side by side; set x_stacked=True to stack.
"""

from charted.charts import ColumnChart

ColumnChart(
    title="Revenue vs Expenses by Quarter ($K)",
    data=[[120, 180, 210, 150], [80, 95, 110, 90]],
    labels=["Q1", "Q2", "Q3", "Q4"],
    series_names=["Revenue", "Expenses"],
    width=700,
    height=400,
).save("compare.svg")
print("wrote compare.svg")

# Stacked version: same data, totals per quarter.
ColumnChart(
    title="Budget Split by Quarter ($K)",
    data=[[120, 180, 210, 150], [80, 95, 110, 90]],
    labels=["Q1", "Q2", "Q3", "Q4"],
    series_names=["Revenue", "Expenses"],
    x_stacked=True,
    width=700,
    height=400,
).save("compare_stacked.svg")
print("wrote compare_stacked.svg")
