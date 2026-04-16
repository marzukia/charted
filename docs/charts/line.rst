Line Charts
===========

.. image:: ../examples/line.svg
   :width: 100%

Basic usage::

   from charted.charts.line import LineChart

   chart = LineChart(data=[1, 2, 3], labels=["a", "b", "c"])
   chart.html  # returns SVG string

Multi-series::

   chart = LineChart(
       data=[[1, 2, 3], [3, 2, 1]],
       labels=["a", "b", "c"],
       series_names=["Series 1", "Series 2"],
   )

.. image:: ../examples/xy_line.svg
   :width: 100%

XY (scatter-line) with real x-values::

   from charted.charts.line import LineChart

   chart = LineChart(
       data=[9, 1, 0, 1, 9],
       x_data=[-3, -1, 0, 1, 3],
       labels=["Jan", "Feb", "Mar", "Apr", "May"],
   )

.. autoclass:: charted.charts.line.LineChart
   :members:
   :undoc-members:
