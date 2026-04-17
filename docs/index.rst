charted
=======

Charted is a zero dependency SVG chart generator that aims to provide a simple interface for generating beautiful and customisable graphs. This project is inspired by chart libraries like ``mermaid.js``.

All chart types support negative values with a proper zero baseline, multi-series data, and theming via a simple dict. Output is a single SVG string — write it to a file or inline it in HTML.

.. code-block:: bash

   pip install charted

.. image:: examples/line.svg
   :width: 100%

.. toctree::
   :maxdepth: 2
   :caption: Charts

   charts/line
   charts/bar
   charts/column
   charts/scatter
    charts/pie

.. toctree::
   :maxdepth: 1
   :caption: API Reference

   api/charts
   api/themes

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
