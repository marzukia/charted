Pie Charts
==========

Circular chart displaying categorical data as proportional slices. Supports doughnut mode.

.. image:: ../examples/pie.svg
   :width: 100%

Basic usage::

   from charted.charts import PieChart

   chart = PieChart(data=[45, 30, 15, 10], labels=["Electronics", "Clothing", "Food", "Other"])
   chart.html

With doughnut mode (set ``inner_radius``)::

   chart = PieChart(
       title="Sales Distribution",
       data=[45, 30, 15, 10],
       labels=["Electronics", "Clothing", "Food", "Other"],
       width=500,
       height=400,
       inner_radius=50,  # Creates a doughnut hole
   )

With exploded slices::

   chart = PieChart(
       data=[45, 30, 15, 10],
       labels=["A", "B", "C", "D"],
       explode=10,  # Explode all slices by 10 pixels
   )

Explode specific slices::

   chart = PieChart(
       data=[45, 30, 15, 10],
       labels=["A", "B", "C", "D"],
       explode=[0, 15, 0, 0],  # Only slice B is exploded
   )

Rotate the starting angle::

   chart = PieChart(
       data=[45, 30, 15, 10],
       labels=["A", "B", "C", "D"],
       start_angle=90,  # Start from right side instead of top
   )

.. autoclass:: charted.charts.pie.PieChart
   :members:
   :undoc-members:
