Charts API
==========

This is the complete API reference for all chart types in charted.

Base Chart Class
----------------

.. autoclass:: charted.Chart
   :members:
   :undoc-members:
   :show-inheritance:

   The base ``Chart`` class provides a unified interface for creating any chart type dynamically.

Column Chart
------------

.. autoclass:: charted.ColumnChart
   :members:
   :undoc-members:
   :show-inheritance:

   Vertical bar chart with support for multi-series, stacked layouts, and side-by-side grouping.

   **Key Parameters:**

   - ``data`` — List of lists for multi-series, or single list for one series
   - ``labels`` — X-axis labels
   - ``series_names`` — Names for each data series (used in legend)
   - ``y_stacked`` — If True, stack bars vertically (default for multi-series)
   - ``theme`` — Theme dictionary or theme name string

   **Example:**

   .. code-block:: python

      from charted import ColumnChart

      chart = ColumnChart(
          data=[[120, 180, 210], [80, 95, 110]],
          labels=["Q1", "Q2", "Q3"],
          series_names=["Revenue", "Expenses"],
          title="Quarterly Performance"
      )
      chart.save("column.svg")

Bar Chart
---------

.. autoclass:: charted.BarChart
   :members:
   :undoc-members:
   :show-inheritance:

   Horizontal bar chart with support for single/multi-series and various layouts.

   **Key Parameters:**

   - ``data`` — Single list or list of lists for multi-series
   - ``labels`` — Y-axis labels
   - ``x_stacked`` — If True, stack bars horizontally
   - ``theme`` — Theme dictionary or theme name string

   **Example:**

   .. code-block:: python

      from charted import BarChart

      chart = BarChart(
          data=[120, 180, 210],
          labels=["Q1", "Q2", "Q3"],
          title="Sales by Quarter"
      )
      chart.save("bar.svg")

Line Chart
----------

.. autoclass:: charted.LineChart
   :members:
   :undoc-members:
   :show-inheritance:

   Line chart with support for multi-series and XY mode.

   **Key Parameters:**

   - ``data`` — List of lists for multi-series
   - ``labels`` — X-axis labels (or ``x_data`` for XY mode)
   - ``x_data`` — Custom X-axis values for XY mode
   - ``theme`` — Theme dictionary or theme name string

   **Example:**

   .. code-block:: python

      from charted import LineChart

      chart = LineChart(
          data=[[120, 180, 210], [80, 95, 110]],
          labels=["Q1", "Q2", "Q3"],
          series_names=["Revenue", "Expenses"],
          title="Trend Line"
      )
      chart.save("line.svg")

Scatter Chart
-------------

.. autoclass:: charted.ScatterChart
   :members:
   :undoc-members:
   :show-inheritance:

   Scatter plot with marker customization.

   **Key Parameters:**

   - ``data`` — List of [x, y] pairs or list of lists for multi-series
   - ``labels`` — Series names
   - ``marker_shape`` — "circle", "square", or "diamond"
   - ``theme`` — Theme dictionary or theme name string

   **Example:**

   .. code-block:: python

      from charted import ScatterChart

      chart = ScatterChart(
          data=[[1, 2], [2, 3], [3, 5], [4, 4]],
          labels=["Series 1"],
          marker_shape="square",
          title="Scatter Plot"
      )
      chart.save("scatter.svg")

Pie Chart
---------

.. autoclass:: charted.PieChart
   :members:
   :undoc-members:
   :show-inheritance:

   Pie chart with doughnut mode and per-slice styling.

   **Key Parameters:**

   - ``data`` — Single list of values
   - ``labels`` — Slice labels
   - ``series_names`` — Legend name
   - ``doughnut`` — If True, render as doughnut chart
   - ``inner_radius`` — Inner radius for doughnut mode (0.3-0.7)
   - ``slice_styles`` — Per-slice customization (colors, explosion, labels)
   - ``theme`` — Theme dictionary or theme name string

   **Example:**

   .. code-block:: python

      from charted import PieChart

      chart = PieChart(
          data=[300, 150, 100, 50],
          labels=["Product A", "Product B", "Product C", "Product D"],
          series_names=["Sales"],
          title="Market Share"
      )
      chart.save("pie.svg")

   **Doughnut Mode:**

   .. code-block:: python

      chart = PieChart(
          data=[300, 150, 100],
          labels=["A", "B", "C"],
          doughnut=True,
          inner_radius=0.5
      )

   **Per-Slice Styling:**

   .. code-block:: python

      chart = PieChart(
          data=[300, 150, 100],
          labels=["A", "B", "C"],
          slice_styles={
              0: {"color": "#FF6B6B", "explode": 0.1},
              1: {"color": "#4ECDC4"},
              2: {"color": "#45B7D1", "label_position": "outside"}
          }
      )

Common Methods
--------------

All chart types share these methods:

- ``to_svg()`` — Generate the SVG string representation of the chart.
- ``save(filepath)`` — Save the chart to a file. Supports .svg extension.
- ``to_markdown(path=None)`` — Generate markdown embedding. If path is provided, uses image reference. Otherwise returns inline data URL.
- ``_repr_html_()`` — IPython/Jupyter integration — returns HTML with inline SVG.

Data Loading API
----------------

.. autofunction:: charted.load_csv

.. autofunction:: charted.load_json

   **Supported JSON Formats:**

   .. code-block:: json

      // Simple array
      [120, 180, 210]

      // Array of objects
      [{"label": "Q1", "value": 120}, {"label": "Q2", "value": 180}]

       // Object with data and labels
       {"data": [120, 180, 210], "labels": ["Q1", "Q2", "Q3"], "title": "Sales"}

CLI API
-------

charted includes a command-line interface for generating charts without writing Python code.

.. code-block:: bash

   # Create a single chart
   python -m charted create <chart_type> <output.svg> --data <input.csv|json>

   # Batch process directory
   python -m charted batch <input_dir> <output_dir> [-t chart_type]

   # Show help
   python -m charted --help
   python -m charted create --help

**Chart Types:** bar, column, line, scatter, pie

Full CLI Reference
~~~~~~~~~~~~~~~~~~

**Create Command:**

.. code-block:: bash

   python -m charted create <chart_type> <output.svg> [options]

   Options:
     <chart_type>      bar, column, line, scatter, or pie
     <output.svg>      Output file path (must end in .svg)
     -d, --data        Input data file (.csv or .json)
     -c, --config      Optional config file (.chartedrc.toml)

   Examples:
     # Create bar chart from CSV
     python -m charted create bar sales.svg --data sales.csv

     # Create column chart with short flags
     python -m charted create column chart.svg -d data.json

     # Use custom config
     python -m charted create line trend.svg --data trend.csv --config .chartedrc.toml

**Batch Command:**

.. code-block:: bash

   python -m charted batch <input_dir> <output_dir> [options]

   Options:
     <input_dir>       Directory containing .csv or .json files
     <output_dir>      Output directory for generated .svg files
     -t, --chart-type  Override chart type inferred from filename
     -c, --config      Optional config file (.chartedrc.toml)

   Filename Pattern: Files should contain chart type keywords (bar, column, line, pie, scatter)
   
   Examples:
     # Process all files, infer chart type from filename
     python -m charted batch data/ output/

     # Force all files to be line charts
     python -m charted batch data/ output/ --chart-type line

     # Use custom config for all charts
     python -m charted batch data/ output/ -c .chartedrc.toml

**Data Formats:**

CSV: First column is labels, remaining columns are data series
.. code-block:: csv

   Quarter,Q1,Q2,Q3,Q4
   Sales,120,180,210,150
   Profit,80,120,140,100

JSON: Supports arrays, arrays of objects, or structured objects

.. code-block:: json

   [120, 180, 210, 150]
   [{"label": "Q1", "value": 120}, {"label": "Q2", "value": 180}]
   {"data": [120, 180], "labels": ["Q1", "Q2"], "title": "Sales"}
**Error Handling:**


CLI provides helpful error messages with suggestions:
- Missing data file → check file path
- Unsupported format → use .csv or .json only
- Invalid chart type → use bar, column, line, scatter, or pie
