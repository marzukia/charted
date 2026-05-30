Interactivity
=============

charted output is a static SVG by default. For HTML embedding you can opt
into native hover tooltips that work in every browser without any
JavaScript.

Hover Tooltips
--------------

Call ``to_html(tooltips=True)`` to attach a native SVG ``<title>`` element
to each data mark. Browsers render these as built-in hover tooltips, so the
chart stays a single self-contained SVG with no scripts or external
dependencies::

   from charted.charts import ColumnChart

   chart = ColumnChart(
       data=[120, 180, 210],
       labels=["Q1", "Q2", "Q3"],
       title="Quarterly Sales",
   )

   html = chart.to_html(tooltips=True)
   with open("chart.html", "w") as f:
       f.write(html)

Hovering over a bar, point, slice, or other mark shows its value in the
browser's standard tooltip. This works across all chart types.

The feature is opt-in. Tooltips are added only when you pass
``tooltips=True`` to ``to_html()``. File output via ``to_svg()`` and
``save()`` is never affected and stays completely inert, so saved ``.svg``
files contain no ``<title>`` elements.
