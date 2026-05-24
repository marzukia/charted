charted
=======

**Zero-dependency SVG chart generator** — simple interface, beautiful output, no external libraries required.

.. code-block:: bash

   pip install charted

.. image:: examples/line.svg
   :width: 100%

**Key Features:**

- **Zero runtime dependencies** — pure Python stdlib, no numpy/pandas needed
- **11 chart types** — Bar, Column, Line, Scatter, Pie, Radar, Area, BoxPlot, Histogram, Heatmap, Gantt
- **Multi-series support** — stacked, side-by-side, grouped layouts
- **Negative values handled** — proper zero baseline calculations
- **Theme system** — 3 built-in themes + custom dict overrides
- **Data loading** — CSV/JSON parsers built-in
- **Markdown export** — generate embed-ready markdown snippets
- **CLI included** — create charts without writing Python code
- **Jupyter ready** — charts render inline automatically
- **Base Chart class** — unified API for dynamic chart type selection
- **Font system** — 8 font definitions (Arial, Inter, Roboto, Helvetica, etc.)
- **PNG export** — rasterize to PNG via cairosvg (optional dependency)
- **auto() detection** — auto-picks chart type from data shape
- **DataFrame support** — create charts directly from pandas DataFrames
- **MCP server** — expose chart generation to AI agents via MCP protocol
- **DuckDB extension** — generate charts from SQL queries
- **describe()** — structured metadata for AI agent introspection

Why Charted?
------------

charted is a zero-dependency SVG chart generator that aims to provide a simple interface for generating beautiful and customizable graphs. This project is inspired by chart libraries like `mermaid.js`.

All chart types support negative values with a proper zero baseline, multi-series data, and theming via a simple dict. Output is a single SVG string — write it to a file or inline it in HTML.

**Installation:**

.. code-block:: bash

   pip install charted

Quick Start
-----------

.. code-block:: python

   from charted import BarChart

   # Create and save a chart in 3 lines
   chart = BarChart(data=[120, 180, 210], labels=["Q1", "Q2", "Q3"])
   chart.save("sales.svg")

That's it — no dependencies, no configuration needed.

Chart Types
-----------

charted provides 11 chart types, all with consistent API:

- **ColumnChart** — vertical bars, multi-series with stacked/side-by-side layouts
- **BarChart** — horizontal bars, single or multi-series
- **LineChart** — line graphs with XY mode support
- **ScatterChart** — scatter plots with marker customization
- **PieChart** — pie/doughnut charts with per-slice styling
- **RadarChart** — multi-axis spider/radar charts for comparison
- **AreaChart** — line chart with filled area underneath
- **BoxPlot** — statistical distribution (quartiles, outliers)
- **Histogram** — frequency distribution across bins
- **HeatmapChart** — 2D matrix with color-coded cells
- **GanttChart** — project timeline / task scheduling

.. toctree::
   :maxdepth: 2
   :caption: Chart Types

   charts/column
   charts/bar
   charts/line
   charts/scatter
   charts/pie
   charts/radar
   charts/area
   charts/boxplot
   charts/histogram
   charts/heatmap
   charts/gantt

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/charts
   api/themes

Advanced Features
-----------------

auto() — Smart Chart Creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let charted pick the best chart type based on your data shape:

.. code-block:: python

   from charted import auto

   # 1D list with <=6 items → PieChart
   chart = auto([40, 35, 15, 10], title="Market Share")

   # 1D list with >6 items → BarChart
   chart = auto([10, 20, 30, 40, 50, 60, 70], title="Scores")

   # 2D matrix → HeatmapChart
   chart = auto([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])

   # Dict → from_dataframe fallback
   chart = auto({"Sales": [10, 20, 30], "Profit": [5, 12, 18]})

from_dataframe() — Pandas Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create charts directly from pandas DataFrames:

.. code-block:: python

   from charted import from_dataframe
   import pandas as pd

   df = pd.DataFrame({"Revenue": [120, 180, 210], "Costs": [80, 95, 110]},
                     index=["Q1", "Q2", "Q3"])
   chart = from_dataframe(df, chart_type="ColumnChart", title="Quarterly")
   chart.save("quarterly.svg")

Also works with plain dicts (no pandas required):

.. code-block:: python

   chart = from_dataframe({"A": [1, 2, 3], "B": [4, 5, 6]})

describe() — Chart Metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get structured metadata about a chart for AI agent workflows:

.. code-block:: python

   from charted import BarChart

   chart = BarChart(data=[120, 180, 210], labels=["Q1", "Q2", "Q3"])
   info = chart.describe()
   # {'chart_type': 'BarChart', 'title': None, 'dimensions': {...},
   #  'series': [{'name': None, 'count': 3, 'min': 120, ...}], ...}

PNG Export
~~~~~~~~~~

Save charts as PNG (requires ``cairosvg`` optional dependency):

.. code-block:: python

   from charted import BarChart

   chart = BarChart(data=[120, 180, 210], labels=["Q1", "Q2", "Q3"])
   chart.save("chart.png")          # Default 2x resolution
   chart.save("chart.png", scale=3) # 3x resolution

Install the optional dependency:

.. code-block:: bash

   pip install cairosvg

Serialization (to_config / from_config)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Serialize charts to dicts for storage or agent workflows:

.. code-block:: python

   from charted import BarChart
   from charted.charts.chart import Chart

   chart = BarChart(data=[120, 180, 210], labels=["Q1", "Q2", "Q3"])
   config = chart.to_config()  # Dict suitable for JSON serialization

   # Recreate later, optionally overriding parameters
   chart2 = Chart.from_config(config, title="Updated Title")

MCP Server
~~~~~~~~~~

charted ships with an MCP (Model Context Protocol) server that exposes chart generation
to AI agents. Tools provided: ``create_chart``, ``chart_from_csv``, ``list_chart_types``,
``list_themes``.

.. code-block:: bash

   # Run the MCP server (stdio transport)
   python -m mcp_server

DuckDB Extension
~~~~~~~~~~~~~~~~

Generate charts directly from SQL queries:

.. code-block:: python

   from duckdb_ext import load
   from duckdb_ext.extension import charted_query

   con = load()
   charted_query(con, 'SELECT quarter, revenue FROM sales',
                 chart_type='bar', title='Revenue', output='chart.svg')

CLI Usage
~~~~~~~~~

charted can be used from the command line to generate charts without writing Python code:

.. code-block:: bash

   # Generate a single chart from CSV/JSON
   python -m charted create bar output.svg --data data.csv

   # Specify chart type and data file
   python -m charted create column chart.svg -d sales.csv

   # Batch generate charts from a directory
   python -m charted batch input_data/ output_svg/

   # Override chart type inference
   python -m charted batch input_data/ output_svg/ -t line

Data Loading
~~~~~~~~~~~~

Load data directly from CSV/JSON files without pandas:

.. code-block:: python

   from charted import load_csv, load_json, BarChart

   # Load from CSV
   x, y, labels = load_csv("sales.csv", x_col="Quarter", y_col="Revenue")
   chart = BarChart(data=y, labels=x, title=labels[0])
   chart.save("sales.svg")

   # Load from JSON
   x, y, labels = load_json("data.json")
   chart = ColumnChart(data=y, labels=x)
   chart.save("chart.svg")

Supported JSON formats: simple arrays, arrays of objects, or objects with `data`/`labels` keys.

Markdown Export
~~~~~~~~~~~~~~~

Generate embed-ready markdown for documentation:

.. code-block:: python

   from charted import BarChart

   chart = BarChart(data=[120, 180, 210], labels=["Q1", "Q2", "Q3"], title="Sales")

   # Save and get markdown with file path
   chart.save("docs/sales.svg")
   md = chart.to_markdown(path="docs/sales.svg")
   # Output: ![Sales](docs/sales.svg)

   # Get markdown with inline data URL
   md = chart.to_markdown()  # Inline SVG as data URL

Perfect for embedding charts in README files, documentation, or markdown-based wikis.

Jupyter Notebook Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

charted works seamlessly in Jupyter notebooks — charts render inline automatically:

.. code-block:: python

   from charted.charts import BarChart

   # Just create a chart, it displays inline
   chart = BarChart(
       title="Sales by Quarter",
       data=[120, 180, 210, 150],
       labels=["Q1", "Q2", "Q3", "Q4"]
   )

Charts are automatically compatible with markdown documentation — just embed the generated SVG:

.. code-block:: markdown

   ![Sales by Quarter](sales.svg)

Base Chart Class
~~~~~~~~~~~~~~~~

Use the unified ``Chart`` class for dynamic chart type selection:

.. code-block:: python

   from charted import Chart

   # Create any chart type with the same interface
   chart = Chart(
       data=[120, 180, 210],
       labels=["Q1", "Q2", "Q3"],
       title="Sales",
       chart_type="bar"  # or "column", "line", "scatter", "pie"
   )
   chart.save("chart.svg")

   # Access all chart methods
   svg = chart.to_svg()
   md = chart.to_markdown()
   html = chart._repr_html_()

Theming
~~~~~~~

charted includes 3 built-in themes plus full custom theme support. See the `Themes Guide <themes.html>`_ for complete documentation on:

- Built-in theme reference (dark, light, high-contrast)
- Theme dictionary structure (legend, marker, title, colors, grid, padding)
- Merging custom overrides with built-in themes
- Creating and registering custom themes

Configuration
~~~~~~~~~~~~~

charted supports configuration via environment variables, TOML config files (``.chartedrc.toml``), and programmatic overrides. See the `Configuration Guide <config.html>`_ for complete documentation on:

- Basic settings (fonts, dimensions, color palette)
- Chart-specific defaults (bar_gap, column_gap, pie label settings)
- Chart-specific theme overrides
- CLI integration
- Environment variables and programmatic config

Font System
~~~~~~~~~~~

charted uses font definitions instead of runtime font rendering for zero-dependency operation. New font definitions can be created using:

.. code-block:: bash

   uv run python charted/commands/create_font_definition.py FontName

Available fonts: Arial, Inter, Roboto, Helvetica, Lato, Fira Code, JetBrains Mono.

Examples
~~~~~~~~

.. include:: ../README.md
   :start-after: ## Examples
   :end-before: ##
