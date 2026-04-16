Bar Charts
==========

.. image:: ../examples/bar.svg
   :width: 100%

Basic usage::

   from charted.charts.bar import BarChart

   chart = BarChart(data=[1, 2, 3], labels=["a", "b", "c"])
   chart.html

Multi-series (side-by-side)::

   chart = BarChart(
       data=[[1, 2, 3], [3, 2, 1]],
       labels=["a", "b", "c"],
   )

.. image:: ../examples/bar_multi.svg
   :width: 100%

.. autoclass:: charted.charts.bar.BarChart
   :members:
   :undoc-members:
