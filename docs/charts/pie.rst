Pie & Doughnut Charts
=====================

Pie chart for categorical data. Set ``doughnut=True`` for a doughnut variant.

.. image:: ../examples/pie.svg
   :width: 80%

Basic usage::

   from charted.charts import PieChart

   chart = PieChart(
       title="Market Share by Product Line",
       data=[35, 28, 18, 12, 7],
       labels=["Product A", "Product B", "Product C", "Product D", "Other"],
       width=600,
       height=500,
   )
   chart.html

Doughnut mode::

   chart = PieChart(
       title="Operating System Market Share",
       data=[72, 15, 8, 5],
       labels=["Windows", "macOS", "Linux", "Other"],
       doughnut=True,
       inner_radius=0.5,
       width=600,
       height=500,
   )

.. image:: ../examples/pie_doughnut.svg
   :width: 80%

.. autoclass:: charted.charts.pie.PieChart
   :members:
   :undoc-members:
