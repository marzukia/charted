charted
=======

Charted is a zero-dependency SVG chart generator for Python. It produces clean, publication-quality charts entirely in Python — no JavaScript, no browser, no external services. Drop the SVG into a web page, a PDF report, or a README and it just works.

Key features:

- **No dependencies** — pure Python, ships as a single package
- **Negative values** — all chart types handle positive/negative data correctly, with a zero baseline
- **Multi-series** — side-by-side bars, stacked columns, overlapping lines with distinct colours
- **Themeable** — override colours, padding, grid styles via a simple dict
- **Embeddable** — output is a single SVG string; write it to a file or inline it in HTML

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
