================================================================================
**Charted**: Zero-Dependency SVG Charting for Python
================================================================================

.. raw:: html

   <p align="center">
     <img src="_static/images/charted-full.svg" alt="Charted Logo" width="400"/>
   </p>

   <p align="center">
     <a href="https://pypi.org/project/charted/"><img src="https://img.shields.io/pypi/v/charted?color=blue" alt="PyPI"/></a>
     <a href="https://github.com/marzukia/charted"><img src="https://img.shields.io/github/stars/marzukia/charted?style=social" alt="GitHub Stars"/></a>
     <a href="https://pypi.org/project/charted/"><img src="https://img.shields.io/pypi/dm/charted" alt="Downloads"/></a>
     <a href="https://github.com/marzukia/charted/blob/main/LICENSE"><img src="https://img.shields.io/github/license/marzukia/charted" alt="License"/></a>
   </p>

   <p align="center">
     <strong>Create beautiful, publication-quality SVG charts with zero runtime dependencies.</strong>
   </p>

   <p align="center">
     <code>pip install charted</code>
   </p>

================================================================================
Why Charted?
================================================================================

.. grid:: 3
   :gutter: 2

   .. grid-item-card:: 🚀 Zero Dependencies
      :class-card: sd-shadow-sm

      Pure Python stdlib. No numpy, pandas, matplotlib, or seaborn required. Charts render as clean SVG strings.

   .. grid-item-card:: 🎨 Beautiful Output
      :class-card: sd-shadow-sm

      Publication-quality SVG with proper typography, color contrast, and responsive design built-in.

   .. grid-item-card:: 📊 14 Chart Types
      :class-card: sd-shadow-sm

      Bar, Column, Line, Scatter, Pie, Radar, Area, Bubble, Combo, HeatmapChart, Gantt, Histogram, Polar Area, Box Plot.

   .. grid-item-card:: 🎯 Simple API
      :class-card: sd-shadow-sm

      Create a chart in 3 lines:

      .. code-block:: python

         from charted import BarChart
         chart = BarChart(data=[120, 180, 210], labels=["Q1", "Q2", "Q3"])
         chart.save("sales.svg")

   .. grid-item-card:: 🌙 Theming System
      :class-card: sd-shadow-sm

      Built-in light/dark/high-contrast themes plus full custom theme support.

   .. grid-item-card:: 📱 Jupyter Ready
      :class-card: sd-shadow-sm

      Charts render inline automatically. No extra configuration needed.

================================================================================
Quick Start
================================================================================

.. tab-set::

   .. tab-item:: Python

      .. code-block:: python

         from charted import BarChart, ColumnChart, LineChart

         # Bar chart
         bar = BarChart(
             data=[120, 180, 210, 150],
             labels=["Q1", "Q2", "Q3", "Q4"],
             title="Sales by Quarter"
         )
         bar.save("bar.svg")

         # Column chart
         column = ColumnChart(
             data=[120, 180, 210, 150],
             labels=["Q1", "Q2", "Q3", "Q4"],
             title="Sales by Quarter"
         )
         column.save("column.svg")

         # Line chart
         line = LineChart(
             data=[120, 180, 210, 150],
             labels=["Q1", "Q2", "Q3", "Q4"],
             title="Sales Trend"
         )
         line.save("line.svg")

   .. tab-item:: CLI

      .. code-block:: bash

         # Create a bar chart from CSV
         python -m charted create bar sales.svg --data sales.csv

         # Batch process multiple files
         python -m charted batch ./data ./output

         # See all options
         python -m charted --help

   .. tab-item:: Jupyter

      .. code-block:: python

         from charted import BarChart

         # Just create a chart: it renders inline
         BarChart(
             data=[120, 180, 210, 150],
             labels=["Q1", "Q2", "Q3", "Q4"],
             title="Sales by Quarter"
         )

================================================================================
Chart Types
================================================================================

.. grid:: 2
   :gutter: 3

   .. grid-item-card:: `ColumnChart <charts/column.html>`_
      :link-type: doc

      Vertical bars for time series and categorical comparisons.

      .. image:: examples/column.svg
         :width: 100%
         :alt: Column Chart Example

   .. grid-item-card:: `BarChart <charts/bar.html>`_
      :link-type: doc

      Horizontal bars for long category labels.

      .. image:: examples/bar.svg
         :width: 100%
         :alt: Bar Chart Example

   .. grid-item-card:: `LineChart <charts/line.html>`_
      :link-type: doc

      Line graphs for trends over time with XY mode support.

      .. image:: examples/line.svg
         :width: 100%
         :alt: Line Chart Example

   .. grid-item-card:: `ScatterChart <charts/scatter.html>`_
      :link-type: doc

      Scatter plots for correlations and distributions.

      .. image:: examples/scatter.svg
         :width: 100%
         :alt: Scatter Chart Example

   .. grid-item-card:: `PieChart <charts/pie.html>`_
      :link-type: doc

      Pie and doughnut charts for proportional data.

      .. image:: examples/pie.svg
         :width: 100%
         :alt: Pie Chart Example

   .. grid-item-card:: `RadarChart <charts/radar.html>`_
      :link-type: doc

      Multi-axis radar charts for comparison analysis.

      .. image:: examples/radar.svg
         :width: 100%
         :alt: Radar Chart Example

   .. grid-item-card:: `HeatmapChart <charts/heatmap.html>`_
      :link-type: doc

      Heat maps for correlation matrices and density plots.

      .. image:: examples/heatmap.svg
         :width: 100%
         :alt: Heatmap Example

   .. grid-item-card:: `GanttChart <charts/gantt.html>`_
      :link-type: doc

      Gantt charts for project timelines with dependencies.

      .. image:: examples/gantt.svg
         :width: 100%
         :alt: Gantt Chart Example

   .. grid-item-card:: `AreaChart <charts/area.html>`_
      :link-type: doc

      Area charts with fill support for cumulative data.

      .. image:: examples/area.svg
         :width: 100%
         :alt: Area Chart Example

   .. grid-item-card:: `BubbleChart <charts/bubble.html>`_
      :link-type: doc

      Bubble charts for 3-dimensional data visualization.

      .. image:: examples/bubble.svg
         :width: 100%
         :alt: Bubble Chart Example

   .. grid-item-card:: `ComboChart <charts/combo.html>`_
      :link-type: doc

      Combo charts mixing bars and lines in one view.

      .. image:: examples/combo.svg
         :width: 100%
         :alt: Combo Chart Example

   .. grid-item-card:: `Histogram <charts/histogram.html>`_
      :link-type: doc

      Histograms for distribution analysis with auto-binning.

      .. image:: examples/histogram.svg
         :width: 100%
         :alt: Histogram Example

   .. grid-item-card:: `PolarAreaChart <charts/polar_area.html>`_
      :link-type: doc

      Polar area charts for radial distribution data.

      .. image:: examples/polar_area.svg
         :width: 100%
         :alt: Polar Area Chart Example

   .. grid-item-card:: `BoxPlot <charts/boxplot.html>`_
      :link-type: doc

      Box plots for statistical quartile and outlier visualization.

      .. image:: examples/boxplot.svg
         :width: 100%
         :alt: Box Plot Example

================================================================================
Features
================================================================================

Multi-Series Support
--------------------

Stacked, side-by-side, or grouped layouts for comparing multiple data series.

.. code-block:: python

   from charted import ColumnChart

   data = [
       [120, 180, 210, 150],  # 2023
       [130, 190, 220, 160],  # 2024
   ]

   chart = ColumnChart(
       data=data,
       labels=["Q1", "Q2", "Q3", "Q4"],
       series_names=["2023", "2024"],
       title="Sales Comparison"
   )
   chart.save("multi.svg")

Negative Values Handled
-----------------------

Proper zero baseline calculations for data with negative values.

.. code-block:: python

   from charted import ColumnChart

   chart = ColumnChart(
       data=[120, -80, 210, -150],
       labels=["Q1", "Q2", "Q3", "Q4"],
       title="Profit/Loss"
   )
   chart.save("negative.svg")

Theming
-------

Built-in themes plus full custom theme support.

.. code-block:: python

   from charted import BarChart

   # Use built-in theme
   chart = BarChart(
       data=[120, 180, 210],
       labels=["Q1", "Q2", "Q3"],
       theme="dark"  # or "light", "high-contrast"
   )

   # Or custom theme
   chart = BarChart(
       data=[120, 180, 210],
       labels=["Q1", "Q2", "Q3"],
       theme={
           "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1"],
           "background_color": "#1a1a2e",
           "grid_color": "#ffffff20"
       }
   )

Data Loading
------------

Load CSV/JSON without pandas.

.. code-block:: python

   from charted import load_csv, BarChart

   x, y, labels = load_csv("sales.csv", x_col="Quarter", y_col="Revenue")
   chart = BarChart(data=y, labels=x, title=labels[0])
   chart.save("sales.svg")

Markdown Export
---------------

Generate embed-ready markdown for documentation.

.. code-block:: python

   from charted import BarChart

   chart = BarChart(data=[120, 180, 210], labels=["Q1", "Q2", "Q3"], title="Sales")
   chart.save("docs/sales.svg")
   md = chart.to_markdown(path="docs/sales.svg")
   # Output: ![Sales](docs/sales.svg)

================================================================================
Documentation
================================================================================

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   quickstart
   getting_started

.. toctree::
   :maxdepth: 2
   :caption: Chart Types

   gallery
   charts/column
   charts/bar
   charts/line
   charts/scatter
   charts/pie
   charts/radar
   charts/area
   charts/bubble
   charts/combo
   charts/heatmap
   charts/gantt
   charts/histogram
   charts/polar_area
   charts/boxplot

.. toctree::
   :maxdepth: 2
   :caption: Guides

   guides/theming
   guides/configuration
   guides/interactivity
   guides/cli

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/charts
   api/themes

.. toctree::
   :maxdepth: 2
   :caption: Resources

   CHANGELOG <https://github.com/marzukia/charted/blob/main/CHANGELOG.md>

================================================================================
License
================================================================================

MIT License: See `LICENSE <https://github.com/marzukia/charted/blob/main/LICENSE>`_ for details.

================================================================================
Community
================================================================================

- `GitHub Repository <https://github.com/marzukia/charted>`_
- `Report Issues <https://github.com/marzukia/charted/issues>`_
- `Contribute <https://github.com/marzukia/charted/blob/main/CONTRIBUTING.md>`_

---

**Built with ❤️ by Andryo Marzuki**
