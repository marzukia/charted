Column Charts
=============

.. image:: ../examples/column.svg
   :width: 100%

Basic usage::

   from charted.charts.column import ColumnChart

   chart = ColumnChart(data=[1, 2, 3], labels=["a", "b", "c"])
   chart.html

Stacked::

   chart = ColumnChart(
       data=[[1, 2, 3], [2, 3, 4]],
       labels=["a", "b", "c"],
   )

Adjust column width with ``column_gap`` (0–1, default 0.5)::

   chart = ColumnChart(data=[1, 2, 3], labels=["a", "b", "c"], column_gap=0.3)

.. autoclass:: charted.charts.column.ColumnChart
   :members:
   :undoc-members:
