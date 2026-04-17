Pie Charts
==========

.. image:: ../examples/pie.svg
   :width: 100%

Basic usage::

   from charted.charts.pie import PieChart

   chart = PieChart(data=[45, 30, 15, 10], labels=["A", "B", "C", "D"])
   chart.html

Donut mode::

   chart = PieChart(
       data=[45, 30, 15, 10],
       labels=["Electronics", "Clothing", "Food", "Other"],
       donut=True,
       donut_radius=0.5,
   )

Custom start angle::

   chart = PieChart(
       data=[25, 25, 25, 25],
       labels=["A", "B", "C", "D"],
       start_angle=45,
   )

.. autoclass:: charted.charts.pie.PieChart
   :members:
   :undoc-members:
