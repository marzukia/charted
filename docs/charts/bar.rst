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

Adjust spacing between bars with ``bar_gap`` (0–1, default 0.5)::

   chart = BarChart(data=[1, 2, 3], labels=["a", "b", "c"], bar_gap=0.3)

.. image:: ../examples/bar_multi.svg
   :width: 100%

.. autoclass:: charted.charts.bar.BarChart
   :members:
   :undoc-members:
