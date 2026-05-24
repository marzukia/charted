Area Charts
===========

Line chart with filled area underneath. Shows one or more series as filled regions under lines.

.. image:: ../examples/area.svg
   :width: 100%

Basic Usage
-----------

Single series area chart::

   from charted import AreaChart

   chart = AreaChart(
       data=[10, 25, 18, 30, 22],
       labels=["Mon", "Tue", "Wed", "Thu", "Fri"],
       title="Daily Traffic"
   )
   chart.save("area.svg")

Multi-Series
------------

Stack multiple series to show cumulative trends::

   chart = AreaChart(
       data=[[10, 20, 30], [15, 25, 35]],
       labels=["Q1", "Q2", "Q3"],
       series_names=["Product A", "Product B"],
       title="Revenue by Product"
   )

.. image:: ../examples/area_multi.svg
   :width: 100%

Fill Opacity
------------

Control how transparent the filled area is::

   chart = AreaChart(
       data=[10, 25, 18, 30, 22],
       labels=["Mon", "Tue", "Wed", "Thu", "Fri"],
       fill_opacity=0.5,  # Default is 0.3
   )

API Reference
-------------

.. autoclass:: charted.charts.area.AreaChart
   :members:
   :undoc-members:
   :show-inheritance:

   **Parameters:**

   - ``data`` — Single list for one series, or list of lists for multi-series
   - ``x_data`` — Optional custom x-axis values
   - ``labels`` — X-axis category labels
   - ``width`` — Chart width in pixels (default 800)
   - ``height`` — Chart height in pixels (default 600)
   - ``fill_opacity`` — Opacity of the filled area (0.0-1.0, default 0.3)
   - ``title`` — Chart title text
   - ``theme`` — Theme instance or None for default
   - ``series_names`` — Names for each data series (shown in legend)
   - ``series_styles`` — Per-series style overrides
