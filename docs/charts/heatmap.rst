Heatmap Charts
==============

2D matrix visualization where each cell is colored according to its value. Useful for correlation matrices, time-series grids, and any tabular numeric data.

Basic Usage
-----------

Pass a 2D list (rows x columns)::

   from charted import HeatmapChart

   chart = HeatmapChart(
       data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
       x_labels=["A", "B", "C"],
       y_labels=["X", "Y", "Z"],
       title="Matrix"
   )
   chart.save("heatmap.svg")

Color Scale
-----------

Customize the low-to-high color gradient::

   chart = HeatmapChart(
       data=[[10, 20], [30, 40]],
       low_color="#ffffff",
       high_color="#ff0000",
   )

Value Annotations
-----------------

By default, numeric values are displayed inside each cell. Control formatting::

   chart = HeatmapChart(
       data=[[1.234, 5.678], [9.012, 3.456]],
       show_values=True,        # Default
       value_format=".2f",      # Two decimal places (default is '.1f')
   )

Disable value display::

   chart = HeatmapChart(
       data=[[1, 2], [3, 4]],
       show_values=False,
   )

Cell Spacing
------------

Adjust gap between cells::

   chart = HeatmapChart(
       data=[[1, 2, 3], [4, 5, 6]],
       cell_gap=0.08,  # Default is 0.04
   )

API Reference
-------------

.. autoclass:: charted.charts.heatmap.HeatmapChart
   :members:
   :undoc-members:
   :show-inheritance:

   **Parameters:**

   - ``data`` — 2D matrix (list of lists), each inner list is one row
   - ``x_labels`` — Column labels (auto-generated if omitted)
   - ``y_labels`` — Row labels (auto-generated if omitted)
   - ``width`` — Chart width in pixels (default 800)
   - ``height`` — Chart height in pixels (default 600)
   - ``title`` — Chart title text
   - ``theme`` — Theme instance or None for default
   - ``series_names`` — Names for each series (shown in legend)
   - ``series_styles`` — Per-series style overrides
   - ``low_color`` — Color for lowest value (default '#1a6b8f')
   - ``high_color`` — Color for highest value (default '#f7a55c')
   - ``show_values`` — Display numeric values in cells (default True)
   - ``value_format`` — Format string for values (default '.1f')
   - ``cell_gap`` — Gap between cells as fraction of cell size (default 0.04)
   - ``label_font_size`` — Font size for labels (default 11)
