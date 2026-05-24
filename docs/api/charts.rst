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
    - ``inner_radius`` — Inner radius for doughnut mode (0.3-0.7, 0 = regular pie)
    - ``slice_styles`` — Per-slice customization (colors, explosion, labels)

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

Radar Chart
-----------

.. autoclass:: charted.RadarChart
   :members:
   :undoc-members:
   :show-inheritance:

   Radar (spider) chart for multi-axis comparison with support for multi-series data.

   **Key Parameters:**

   - ``data`` — List of lists for multi-series, each inner list has one value per axis
   - ``labels`` — Axis labels (one per data point)
   - ``series_names`` — Names for each data series (used in legend)
   - ``theme`` — Theme dictionary or theme name string

   **Example:**

   .. code-block:: python

      from charted import RadarChart

      chart = RadarChart(
          data=[
              [85, 90, 75, 88, 92],  # Player A
              [70, 85, 90, 75, 80],  # Player B
          ],
          labels=["Speed", "Strength", "Defense", "Technique", "Stamina"],
          series_names=["Player A", "Player B"],
          title="Player Skill Comparison"
      )
      chart.save("radar.svg")

Area Chart
----------

.. autoclass:: charted.AreaChart
   :members:
   :undoc-members:
   :show-inheritance:

   Line chart with filled area underneath.

   **Key Parameters:**

   - ``data`` — Single list or list of lists for multi-series
   - ``labels`` — X-axis labels
   - ``fill_opacity`` — Area fill opacity (0.0-1.0, default 0.3)
   - ``theme`` — Theme instance or preset name

   **Example:**

   .. code-block:: python

      from charted import AreaChart

      chart = AreaChart(
          data=[[10, 20, 30], [15, 25, 35]],
          labels=["Q1", "Q2", "Q3"],
          series_names=["Revenue", "Profit"],
          fill_opacity=0.4,
          title="Growth"
      )
      chart.save("area.svg")

Box Plot
--------

.. autoclass:: charted.BoxPlot
   :members:
   :undoc-members:
   :show-inheritance:

   Statistical distribution chart showing quartiles, median, and range.

   **Key Parameters:**

   - ``data`` — List of series (each a list of values)
   - ``labels`` — Labels for each box
   - ``theme`` — Theme instance or preset name

   **Example:**

   .. code-block:: python

      from charted import BoxPlot

      chart = BoxPlot(
          data=[[1, 2, 3, 4, 5], [2, 3, 4, 5, 6, 7]],
          labels=["Group A", "Group B"],
          title="Distribution"
      )
      chart.save("boxplot.svg")

Histogram
---------

.. autoclass:: charted.Histogram
   :members:
   :undoc-members:
   :show-inheritance:

   Frequency distribution across auto-computed bins.

   **Key Parameters:**

   - ``data`` — Flat list of values to bin
   - ``bins`` — Number of bins (auto via Sturges' rule if None)
   - ``theme`` — Theme instance or preset name

   **Example:**

   .. code-block:: python

      from charted import Histogram

      chart = Histogram(
          data=[1, 2, 2, 3, 3, 3, 4, 4, 5],
          bins=5,
          title="Value Distribution"
      )
      chart.save("histogram.svg")

Heatmap Chart
-------------

.. autoclass:: charted.HeatmapChart
   :members:
   :undoc-members:
   :show-inheritance:

   2D matrix with color-coded cells.

   **Key Parameters:**

   - ``data`` — 2D list (rows x columns)
   - ``x_labels`` — Column labels
   - ``y_labels`` — Row labels
   - ``low_color`` / ``high_color`` — Color scale endpoints
   - ``show_values`` — Display value annotations (default True)
   - ``theme`` — Theme instance or preset name

   **Example:**

   .. code-block:: python

      from charted import HeatmapChart

      chart = HeatmapChart(
          data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
          x_labels=["A", "B", "C"],
          y_labels=["X", "Y", "Z"],
          title="Correlation Matrix"
      )
      chart.save("heatmap.svg")

Gantt Chart
-----------

.. autoclass:: charted.GanttChart
   :members:
   :undoc-members:
   :show-inheritance:

   Project timeline / task scheduling chart.

   **Key Parameters:**

   - ``data`` — List of (start, end) tuples, or list of lists for multi-series
   - ``labels`` — Task names
   - ``dependencies`` — List of (from_index, to_index) tuples for arrows
   - ``bar_height_ratio`` — Bar height as fraction of row (default 0.6)
   - ``theme`` — Theme instance or preset name

   **Example:**

   .. code-block:: python

      from charted import GanttChart

      chart = GanttChart(
          data=[(0, 3), (2, 5), (4, 7)],
          labels=["Design", "Build", "Test"],
          dependencies=[(0, 1), (1, 2)],
          title="Project Plan"
      )
      chart.save("gantt.svg")

Common Methods
--------------

All chart types share these methods:

.. py:method:: to_svg()

   Generate the SVG string representation of the chart.

.. py:method:: save(filepath, *, scale=2)

   Save the chart to a file. Supports ``.svg`` and ``.png`` extensions.
   PNG export requires the ``cairosvg`` optional dependency.

.. py:method:: to_markdown(alt_text=None, width=None)

   Generate markdown embedding with inline data URL.

.. py:method:: to_html(style="display: inline-block;")

   Wrap the SVG in an HTML div with optional inline style.

.. py:method:: to_base64()

   Return the SVG as a base64-encoded data URI string.

.. py:method:: to_config()

   Serialize the chart to a dictionary suitable for JSON storage.

.. py:classmethod:: from_config(config, **overrides)

   Recreate a chart from a config dict (from ``to_config()``).

.. py:method:: describe()

   Return structured metadata about the chart (type, dimensions, series stats).

.. py:method:: _repr_html_()

   IPython/Jupyter integration — returns HTML with inline SVG.

Data Loading API
----------------

.. autofunction:: charted.load_csv

   Load data from a CSV file.

   **Parameters:**

   - ``filepath`` — Path to CSV file
   - ``x_col`` — Column name for X-axis/labels
   - ``y_cols`` — Column name(s) for Y-axis data
   - ``delimiter`` — CSV delimiter (default: ",")

   **Returns:** Tuple of (x_values, y_values, column_names)

.. autofunction:: charted.load_json

   Load data from a JSON file. Auto-detects format based on JSON structure.

   **Parameters:**

   - ``filepath`` — Path to JSON file

   **Returns:** Tuple of (x_values, y_values, column_names)

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

   # Batch process
   python -m charted batch <input_dir> <output_dir>

Theme API
---------

.. autofunction:: charted.get_theme

   Get a registered theme by name.

   **Parameters:**

   - ``name`` — Registered theme name string

   **Returns:** Theme instance

Built-in presets: ``"dark"``, ``"light"``, ``"high-contrast"``.

See :doc:`themes` for full theme documentation including ``Theme.from_preset()``,
``Theme.compose()``, ``register_theme()``, and ``validate_theme()``.
