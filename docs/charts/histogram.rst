Histograms
==========

Frequency distribution of values across evenly-spaced bins. Pass raw data and charted computes the bin counts automatically.

.. image:: ../examples/histogram.svg
   :width: 100%

Basic Usage
-----------

Pass a flat list of values — charted auto-calculates the bin count using Sturges' rule::

   from charted import Histogram

   chart = Histogram(
       data=[1, 2, 2, 3, 3, 3, 4, 4, 5, 5, 5, 5],
       title="Value Distribution"
   )
   chart.save("histogram.svg")

Custom Bin Count
----------------

Override the auto-calculated bin count::

   chart = Histogram(
       data=[10, 12, 14, 15, 18, 20, 22, 25, 30, 35, 40],
       bins=5,
       title="Custom Bins"
   )

API Reference
-------------

.. autoclass:: charted.charts.histogram.Histogram
   :members:
   :undoc-members:
   :show-inheritance:

   **Parameters:**

   - ``data`` — Flat list of numeric values to bin
   - ``bins`` — Number of bins (auto-calculated via Sturges' rule if None)
   - ``labels`` — Optional x-axis labels (auto-generated from bin edges if omitted)
   - ``width`` — Chart width in pixels (default 800)
   - ``height`` — Chart height in pixels (default 600)
   - ``title`` — Chart title text
   - ``theme`` — Theme instance or None for default
