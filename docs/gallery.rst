Gallery
=======

A one-stop tour of every chart type Charted can render. Each entry shows the
code that produces it, the rendered SVG, and a one-line note on when to reach
for it. For the full parameter list of any type, follow the link in its
heading through to the dedicated chart page.

Themes at a Glance
------------------

The same chart rendered under each built-in theme. Pass ``theme="light"``,
``theme="dark"``, or ``theme="high-contrast"`` to any chart.

.. list-table::
   :widths: 33 33 33

   * - .. image:: examples_themes/light.svg
          :width: 100%
          :alt: Light theme
     - .. image:: examples_themes/dark.svg
          :width: 100%
          :alt: Dark theme
     - .. image:: examples_themes/high-contrast.svg
          :width: 100%
          :alt: High-contrast theme

.. code-block:: python

   from charted import ColumnChart

   chart = ColumnChart(
       data=[120, 180, 210, 150],
       labels=["Q1", "Q2", "Q3", "Q4"],
       title="Sales by Quarter",
       theme="dark",  # or "light", "high-contrast"
   )
   chart.save("themed.svg")

Combo
-----

.. image:: examples/combo.svg
   :width: 100%
   :alt: Combo chart

.. code-block:: python

   from charted.charts import ComboChart

   chart = ComboChart(
       series=[
           {"data": [120, 180, 150, 210], "type": "bar", "name": "Revenue"},
           {"data": [12, 19, 15, 22], "type": "line", "name": "Margin %"},
       ],
       labels=["Q1", "Q2", "Q3", "Q4"],
       title="Revenue and Margin",
   )
   chart.save("combo.svg")

Why it matters: shows two metrics on different scales in one frame without flattening either. See :doc:`charts/combo`.

Bubble
------

.. image:: examples/bubble.svg
   :width: 100%
   :alt: Bubble chart

.. code-block:: python

   from charted.charts import BubbleChart

   chart = BubbleChart(
       x_data=[1, 2, 3, 4, 5],
       y_data=[10, 25, 15, 30, 20],
       sizes=[5, 30, 12, 45, 18],
       title="Sales by Region",
   )
   chart.save("bubble.svg")

Why it matters: encodes a third dimension as marker size, so magnitude rides alongside position. See :doc:`charts/bubble`.

Heatmap
-------

.. image:: examples/heatmap.svg
   :width: 100%
   :alt: Heatmap chart

.. code-block:: python

   from charted.charts import HeatmapChart

   chart = HeatmapChart(
       data=[
           [1, 2, 3],
           [4, 5, 6],
           [7, 8, 9],
       ],
       x_labels=["A", "B", "C"],
       y_labels=["Row 1", "Row 2", "Row 3"],
       title="Matrix Values",
   )
   chart.save("heatmap.svg")

Why it matters: turns a dense matrix into a colour field, making correlations and hotspots pop at a glance. See :doc:`charts/heatmap`.

Radar
-----

.. image:: examples/radar.svg
   :width: 100%
   :alt: Radar chart

.. code-block:: python

   from charted.charts import RadarChart

   chart = RadarChart(
       data=[85, 90, 75, 88, 92],
       labels=["Speed", "Strength", "Defense", "Technique", "Stamina"],
       title="Player Stats",
   )
   chart.save("radar.svg")

Why it matters: compares many attributes of one or two subjects on a single shape you can read at a glance. See :doc:`charts/radar`.

Box Plot
--------

.. image:: examples/boxplot.svg
   :width: 100%
   :alt: Box plot

.. code-block:: python

   from charted.charts import BoxPlot

   chart = BoxPlot(
       data=[
           [4, 5, 3, 6, 7, 8, 4, 6],
           [2, 4, 3, 5, 7, 8, 9, 3],
           [6, 7, 9, 8, 10, 6, 8, 5],
       ],
       labels=["Control", "Treatment A", "Treatment B"],
       title="Test Scores by Group",
   )
   chart.save("boxplot.svg")

Why it matters: summarises a distribution's quartiles and outliers, so you compare spread, not just averages. See :doc:`charts/boxplot`.

Gantt
-----

.. image:: examples/gantt.svg
   :width: 100%
   :alt: Gantt chart

.. code-block:: python

   from charted.charts import GanttChart

   chart = GanttChart(
       data=[(1, 5), (3, 7), (6, 9)],
       labels=["Design", "Development", "Testing"],
       title="Project Timeline",
   )
   chart.save("gantt.svg")

Why it matters: lays out task start and end points on a timeline, so overlap and sequencing are obvious. See :doc:`charts/gantt`.

Bar
---

.. image:: examples/bar.svg
   :width: 100%
   :alt: Bar chart

.. code-block:: python

   from charted.charts import BarChart

   chart = BarChart(
       data=[120, 180, 210, 150],
       labels=["Q1", "Q2", "Q3", "Q4"],
       title="Sales by Quarter",
   )
   chart.save("bar.svg")

Why it matters: horizontal bars give long category labels room to breathe. See :doc:`charts/bar`.

Column
------

.. image:: examples/column.svg
   :width: 100%
   :alt: Column chart

.. code-block:: python

   from charted.charts import ColumnChart

   chart = ColumnChart(
       data=[12, 22, 30, 18, 25],
       labels=["Q1", "Q2", "Q3", "Q4", "Q5"],
       title="Monthly Sales",
   )
   chart.save("column.svg")

Why it matters: vertical bars are the default for time series and categorical comparisons. See :doc:`charts/column`.

Line
----

.. image:: examples/line.svg
   :width: 100%
   :alt: Line chart

.. code-block:: python

   from charted.charts import LineChart

   chart = LineChart(
       data=[120, 180, 210, 150, 230],
       labels=["Jan", "Feb", "Mar", "Apr", "May"],
       title="Monthly Sales Trend",
   )
   chart.save("line.svg")

Why it matters: connects points to show trend and direction over a continuous axis. See :doc:`charts/line`.

Area
----

.. image:: examples/area.svg
   :width: 100%
   :alt: Area chart

.. code-block:: python

   from charted.charts import AreaChart

   chart = AreaChart(
       data=[120, -80, 150, -90, 170],
       labels=["Jan", "Feb", "Mar", "Apr", "May"],
       title="Monthly Trend",
   )
   chart.save("area.svg")

Why it matters: the filled area under a line emphasises volume and cumulative weight. See :doc:`charts/area`.

Scatter
-------

.. image:: examples/scatter.svg
   :width: 100%
   :alt: Scatter chart

.. code-block:: python

   from charted.charts import ScatterChart

   chart = ScatterChart(
       data=[[1, 2], [2, 3], [3, 5], [4, 4], [5, 7]],
       labels=["Data Points"],
       title="Correlation Example",
   )
   chart.save("scatter.svg")

Why it matters: plots raw point pairs to reveal correlation, clustering, and outliers. See :doc:`charts/scatter`.

Pie and Doughnut
----------------

.. image:: examples/pie.svg
   :width: 100%
   :alt: Pie chart

.. code-block:: python

   from charted.charts import PieChart

   chart = PieChart(
       data=[45, 30, 15, 10],
       labels=["Electronics", "Clothing", "Food", "Other"],
       title="Revenue by Category",
   )
   chart.save("pie.svg")

Set ``inner_radius`` to render the same data as a doughnut:

.. image:: examples/pie_doughnut.svg
   :width: 100%
   :alt: Doughnut chart

.. code-block:: python

   chart = PieChart(
       data=[45, 30, 15, 10],
       labels=["Electronics", "Clothing", "Food", "Other"],
       title="Sales Distribution",
       inner_radius=0.5,  # 50% of outer radius
   )
   chart.save("pie_doughnut.svg")

Why it matters: shows parts of a whole; the doughnut frees the centre for a label or total. See :doc:`charts/pie`.

Histogram
---------

.. image:: examples/histogram.svg
   :width: 100%
   :alt: Histogram

.. code-block:: python

   from charted.charts import Histogram

   chart = Histogram(
       data=[1.2, 1.5, 2.1, 2.3, 3.1, 3.5, 4.0, 4.2, 5.1, 5.5],
       bins=5,
       title="Data Distribution",
   )
   chart.save("histogram.svg")

Why it matters: buckets raw values to show the shape of a distribution, with auto-binning when you skip ``bins``. See :doc:`charts/histogram`.

Polar Area
----------

.. image:: examples/polar_area.svg
   :width: 100%
   :alt: Polar area chart

.. code-block:: python

   from charted.charts import PolarAreaChart

   chart = PolarAreaChart(
       data=[10, 20, 30, 15, 25],
       labels=["A", "B", "C", "D", "E"],
       title="Activity by Category",
   )
   chart.save("polar_area.svg")

Why it matters: equal-angle wedges scaled by value suit cyclical data like weekdays or compass directions. See :doc:`charts/polar_area`.
