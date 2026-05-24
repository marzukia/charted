Gantt Charts
============

Project timeline visualization. Displays tasks as horizontal bars along a timeline where position and length represent start time and duration.

Basic Usage
-----------

Pass a list of ``(start, end)`` tuples::

   from charted import GanttChart

   chart = GanttChart(
       data=[(1, 3), (2, 5), (4, 7)],
       labels=["Design", "Development", "Testing"],
       title="Project Timeline"
   )
   chart.save("gantt.svg")

Multi-Series (Grouped Tasks)
-----------------------------

Group tasks into series for color-coding::

   chart = GanttChart(
       data=[
           [(1, 3), (3, 5)],    # Team A
           [(2, 4), (5, 7)],    # Team B
       ],
       labels=["Phase 1", "Phase 2"],
       series_names=["Team A", "Team B"],
       title="Team Schedule"
   )

Dependency Arrows
-----------------

Show task dependencies with arrows between bars::

   chart = GanttChart(
       data=[(0, 2), (2, 5), (5, 8)],
       labels=["Research", "Build", "Deploy"],
       dependencies=[(0, 1), (1, 2)],  # Research→Build→Deploy
   )

Bar Height
----------

Adjust the height of task bars relative to their row::

   chart = GanttChart(
       data=[(1, 4), (3, 6)],
       labels=["Task A", "Task B"],
       bar_height_ratio=0.8,  # Default is 0.6
   )

API Reference
-------------

.. autoclass:: charted.charts.gantt.GanttChart
   :members:
   :undoc-members:
   :show-inheritance:

   **Parameters:**

   - ``data`` — List of (start, end) tuples, or list of lists for multi-series
   - ``labels`` — Task names on the y-axis
   - ``width`` — Chart width in pixels (default 800)
   - ``height`` — Chart height in pixels (default 600)
   - ``title`` — Chart title text
   - ``theme`` — Theme instance or None for default
   - ``series_names`` — Names for each series (shown in legend)
   - ``series_styles`` — Per-series style overrides
   - ``dependencies`` — List of (from_index, to_index) tuples for arrows
   - ``bar_height_ratio`` — Bar height as fraction of row height (default 0.6)
   - ``show_today_line`` — Draw a dashed vertical line at x_position
   - ``x_position`` — Position value for the today-line
