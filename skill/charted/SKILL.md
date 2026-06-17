---
name: charted
description: Generate SVG or PNG charts from raw numbers or a CSV using charted, a zero-dependency Python chart library. Covers bar, column, line, scatter, bubble, pie, polar_area, radar, area, box, histogram, heatmap, gantt, combo, and sankey, plus multi-series data, named palettes, and a CLI. Use when asked to plot, chart, or visualize data and produce an image file.
---

# charted

charted turns lists of numbers (or a CSV) into a clean SVG chart. The core library has no runtime dependencies. PNG export pulls in `cairosvg` as an opt-in extra.

## Install

```sh
pip install 'charted[png]'   # core + PNG export
```

Use plain `pip install charted` if you only need SVG.

## Generate a chart in Python

```python
from charted import BarChart

chart = BarChart(
    title="Sales by Quarter",
    data=[120, 180, 210, 150],
    labels=["Q1", "Q2", "Q3", "Q4"],
    width=700,
    height=400,
)
chart.save("sales.svg")   # SVG
chart.save("sales.png")   # PNG (needs charted[png])
```

`save()` picks the format from the file extension. Every chart class takes the same
core arguments: `data`, `labels`, `title`, `width`, `height`.

## Generate a chart from the CLI

No Python needed. The first CSV column is the x-axis labels, every other column is a data series.

```sh
python -m charted create bar output.svg --data sales.csv
python -m charted create bar output.svg --data sales.csv --title "Q3 Sales" --width 900 --height 400
python -m charted batch input_data/ output_svg/
```

Use `--transpose` when the CSV is laid out sideways (one series per row, x values across the header row).

## Pick a chart type by data shape

| Data shape | Use |
|------------|-----|
| Values across categories | `bar`, `column` |
| Values over a continuous x | `line`, `area` |
| Two paired numeric variables | `scatter` (add a size for `bubble`) |
| Parts of a whole | `pie`, `polar_area` |
| Several metrics per item | `radar` |
| Distribution of one variable | `histogram`, `box` |
| Grid of two categories | `heatmap` |
| Tasks over time | `gantt` |
| Bars and a line together | `combo` |
| Flows between nodes | `sankey` |

All chart types: `bar`, `column`, `line`, `scatter`, `bubble`, `pie`, `polar_area`,
`radar`, `area`, `box`, `histogram`, `heatmap`, `gantt`, `combo`, `sankey`.

Import any of them from `charted.charts`, for example
`from charted.charts import LineChart, PieChart, ScatterChart`.

## Multi-series data

Pass a list of lists as `data` and name each series with `series_names`. Bar and
column charts group side by side by default; set `x_stacked=True` to stack them.

```python
from charted.charts import ColumnChart

ColumnChart(
    title="Revenue vs Expenses",
    data=[[120, 180, 210], [80, 95, 110]],
    labels=["Q1", "Q2", "Q3"],
    series_names=["Revenue", "Expenses"],
).save("compare.svg")
```

## Themes and palettes

Built-in theme presets: `light`, `dark`, `high-contrast`. Pass one as `theme=`.

```python
BarChart(data=[120, 180, 210], labels=["Q1", "Q2", "Q3"], theme="dark").save("dark.svg")
```

Named palettes turn into a list of hex colors via `resolve_palette(name)`, passed as `colors=`:

```python
from charted import resolve_palette
BarChart(data=[1, 2, 3], colors=resolve_palette("viridis")).save("v.svg")
```

Named palettes: `default`, `viridis`, `ocean`, `categorical`, `rainbow`,
`monochrome`, `pastel`, `sunset`, `forest`, `inferno`, and the colourblind-safe `okabe-ito`.

## Load a CSV in Python

```python
from charted import load_csv, BarChart

x, y, labels = load_csv("sales.csv", x_col="Quarter", y_col="Revenue")
BarChart(data=y, labels=x, title=labels[0]).save("sales.svg")
```

`load_json` works the same way for JSON files.

## Show the result

After saving, give the user the file path. SVG opens in any browser and renders
inline in Jupyter. PNG is a raster image for slides, docs, or chat. When the user
wants an image they can preview, save a `.png` and hand them that path.

## More examples

See `examples/` next to this file for short worked scripts: a CSV-to-chart pipeline,
a multi-series comparison, and a themed chart.
