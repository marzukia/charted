Pie Charts
==========

Circular chart displaying categorical data as proportional slices. Supports doughnut mode, per-slice styling, and exploded slices.

.. image:: ../examples/pie.svg
   :width: 100%

Basic Usage
-----------

Simple pie chart::

   from charted.charts import PieChart

   chart = PieChart(
       data=[45, 30, 15, 10],
       labels=["Electronics", "Clothing", "Food", "Other"],
       series_names=["Sales"],
       title="Revenue by Category"
   )
   chart.save("pie.svg")

Doughnut Mode
-------------

Create a doughnut chart by setting inner_radius::

   chart = PieChart(
       title="Sales Distribution",
       data=[45, 30, 15, 10],
       labels=["Electronics", "Clothing", "Food", "Other"],
       series_names=["Sales"],
       width=500,
       height=400,
       doughnut=True,
       inner_radius=0.5  # 50% of outer radius
   )

.. image:: ../examples/pie_doughnut.svg
   :width: 100%

Customizing Doughnut::

   chart = PieChart(
       data=[300, 150, 100],
       labels=["Product A", "Product B", "Product C"],
       doughnut=True,
       inner_radius=0.4,  # Smaller hole
       start_angle=45,  # Rotate chart
       theme={
           "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1"]  # Custom slice colors
       }
   )

Exploded Slices
---------------

Highlight specific slices by exploding them outward::

   # Explode all slices uniformly
   chart = PieChart(
       data=[45, 30, 15, 10],
       labels=["A", "B", "C", "D"],
       explode=0.1  # Explode all by 10%
   )

   # Explode specific slices
   chart = PieChart(
       data=[45, 30, 15, 10],
       labels=["A", "B", "C", "D"],
       explode=[0.15, 0.0, 0.1, 0.0]  # Per-slice explosion
   )

Per-Slice Styling
-----------------

Customize individual slices with colors, labels, and explosion::

   chart = PieChart(
       data=[300, 150, 100, 50],
       labels=["Product A", "Product B", "Product C", "Product D"],
       series_names=["Sales"],
       title="Market Share",
       slice_styles={
           0: {
               "color": "#FF6B6B",
               "explode": 0.1,
               "label_position": "outside"
           },
           1: {
               "color": "#4ECDC4",
               "label_position": "inside"
           },
           2: {
               "color": "#45B7D1",
               "label_position": "auto"
           },
           3: {
               "color": "#FFA07A",
               "label_position": "outside"
           }
       }
   )

Custom Colors
-------------

Override the default color palette::

   chart = PieChart(
       data=[300, 150, 100],
       labels=["A", "B", "C"],
       theme={
           "colors": ["#2ECC71", "#3498DB", "#E74C3C"]
       }
   )

Or use a built-in theme::

   chart = PieChart(
       data=[300, 150, 100],
       labels=["A", "B", "C"],
       theme="dark"  # Dark background theme
   )

   chart = PieChart(
       data=[300, 150, 100],
       labels=["A", "B", "C"],
       theme="light"  # Light background theme
   )

Rotation and Angle
------------------

Control the starting angle of the pie::

   # Start from top (default)
   chart = PieChart(
       data=[45, 30, 15, 10],
       labels=["A", "B", "C", "D"]
   )

   # Start from right (90 degrees)
   chart = PieChart(
       data=[45, 30, 15, 10],
       labels=["A", "B", "C", "D"],
       start_angle=90
   )

Label Positioning
-----------------

Control where labels appear::

   # Labels positioned automatically based on slice size
   chart = PieChart(
       data=[300, 150, 100],
       labels=["Large", "Medium", "Small"]
   )

   # Labels positioned automatically based on slice size
   chart = PieChart(
       data=[300, 150, 100],
       labels=["Large", "Medium", "Small"]
   )

Configuration Options
---------------------

Complete pie customization::

   chart = PieChart(
       data=[300, 150, 100, 50],
       labels=["Product A", "Product B", "Product C", "Product D"],
       series_names=["Sales"],
       title="Revenue Distribution",
       width=600,
       height=500,
       inner_radius=0.4,          # 0 for pie, 0.3-0.7 for doughnut
       start_angle=0,             # Starting angle in degrees
       explode=0,                 # Default explode amount
       theme={
           "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A"]
       }
   )

API Reference
-------------

.. autoclass:: charted.charts.pie.PieChart
   :members:
   :undoc-members:
   :show-inheritance:

   **Parameters:**

   - ``data`` — Single list of values (one slice per value)
   - ``labels`` — Slice labels
   - ``series_names`` — Legend name for the data series
   - ``doughnut`` — If True, render as doughnut chart (default: False)
   - ``inner_radius`` — Inner radius ratio for doughnut mode (0.3-0.7, default: 0)
   - ``slice_styles`` — Dictionary mapping slice index to style overrides
   - ``width`` — Chart width in pixels (default 800)
   - ``height`` — Chart height in pixels (default 600)
   - ``theme`` — Theme name string or theme dictionary
   - ``title`` — Chart title text
   - ``subtitle`` — Optional subtitle text

   **Slice Style Options:**

   - ``color`` — Override slice color
   - ``explode`` — Explode distance (0-1 ratio)
   - ``label_position`` — "inside", "outside", or "auto"

   **Example:**

   .. code-block:: python

      from charted import PieChart

      chart = PieChart(
          data=[300, 150, 100, 50],
          labels=["Product A", "Product B", "Product C", "Product D"],
          series_names=["Sales"],
          title="Market Share",
          doughnut=True,
          inner_radius=0.5,
          slice_styles={
              0: {"color": "#FF6B6B", "explode": 0.1},
              1: {"color": "#4ECDC4"},
              2: {"color": "#45B7D1"},
              3: {"color": "#FFA07A"}
          }
      )
      chart.save("pie.svg")
      print(chart.to_markdown())  # ![Market Share](pie.svg)
