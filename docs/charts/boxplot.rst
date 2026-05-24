Box Plots
=========

Statistical distribution chart showing median, quartiles (Q1/Q3), and range for one or more groups.

.. image:: ../examples/boxplot.svg
   :width: 100%

Basic Usage
-----------

Provide a list of data series — each series becomes one box::

   from charted import BoxPlot

   chart = BoxPlot(
       data=[[1, 2, 3, 4, 5, 6, 7], [3, 4, 5, 6, 7, 8, 9]],
       labels=["Group A", "Group B"],
       title="Score Distribution"
   )
   chart.save("boxplot.svg")

Each box displays:

- **Box**: Q1 to Q3 (interquartile range)
- **Line inside box**: Median
- **Whiskers**: Minimum to maximum

Single Group
------------

Pass a single list inside a list::

   chart = BoxPlot(
       data=[[12, 15, 18, 22, 25, 28, 30, 35, 40]],
       labels=["Measurements"],
   )

API Reference
-------------

.. autoclass:: charted.charts.box.BoxPlot
   :members:
   :undoc-members:
   :show-inheritance:

   **Parameters:**

   - ``data`` — List of series, each series is a list of numeric values
   - ``labels`` — Labels for each box (category names)
   - ``width`` — Chart width in pixels (default 800)
   - ``height`` — Chart height in pixels (default 600)
   - ``title`` — Chart title text
   - ``theme`` — Theme instance or None for default
   - ``series_names`` — Names for each series
