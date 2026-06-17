"""Read a CSV and save a chart as PNG.

The first CSV column is the x-axis labels; pick a numeric column for the y values.
Run: pip install 'charted[png]'
"""

from charted import load_csv, BarChart

# sales.csv:
#   Quarter,Revenue,Expenses
#   Q1,120,80
#   Q2,180,95
#   Q3,210,110
x, y, labels = load_csv("sales.csv", x_col="Quarter", y_col="Revenue")

chart = BarChart(
    title="Revenue by Quarter",
    data=y,
    labels=x,
    width=700,
    height=400,
)
chart.save("revenue.png")
print("wrote revenue.png")
