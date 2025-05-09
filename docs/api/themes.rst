Themes API
==========

charted includes a comprehensive theme system with 3 built-in themes and full custom theme support.

Built-in Themes
---------------

The following presets are available out of the box:

- ``"dark"`` — Dark background with high-contrast light colors
- ``"light"`` — Light background with subtle grid lines
- ``"high-contrast"`` — Maximum visibility with bold colors

Using the ``theme.load()`` method to load a theme by name:

.. code-block:: python

   from charted import BarChart
   from charted.utils.themes import Theme

   # Use built-in theme by name
   chart = BarChart(
       data=[120, 180, 210],
       labels=["Q1", "Q2", "Q3"],
       theme=Theme.load("dark")
   )

   # Override specific properties
   chart = BarChart(
       data=[120, 180, 210],
       labels=["Q1", "Q2", "Q3"],
       theme={
           "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1"]
       }
   )

   # Merge built-in with custom overrides
   dark_overrides = Theme.load("dark")
   dark_overrides["title"]["font_size"] = "24px"
   chart = BarChart(
       data=[120, 180, 210],
       labels=["Q1", "Q2", "Q3"],
       theme=dark_overrides
   )

Theme Dictionary Structure
--------------------------

Complete theme configuration dictionary structure:

.. code-block:: python

   {
       # Legend configuration
       "legend": {
           "font_size": str,       # Font size (e.g., "11px")
           "legend_padding": float, # Padding ratio (e.g., 0.25)
           "position": str,        # "topright", "topleft", "bottomright", etc.
       },

       # Marker configuration
       "marker": {
           "marker_size": float,   # Marker size in pixels (e.g., 3.0)
       },

       # Title configuration
       "title": {
           "font_size": str,       # Font size (e.g., "18px")
           "font_family": str,     # Font family (e.g., "Arial")
           "font_weight": str,     # "normal", "bold", "lighter"
           "font_color": str,      # Hex color (e.g., "#333333")
       },

       # Colors configuration
       "colors": list[str],        # List of hex colors for data series

       # Vertical grid configuration
       "v_grid": {
           "stroke": str,          # Grid line color
           "stroke_dasharray": str,# "2,2" for dashed, None for solid
       },

       # Horizontal grid configuration
       "h_grid": {
           "stroke": str,
           "stroke_dasharray": str,
       },

       # Padding configuration
       "padding": {
           "h_padding": float,     # Horizontal padding ratio (e.g., 0.05)
           "v_padding": float,     # Vertical padding ratio (e.g., 0.05)
       },

       # Series style configuration (optional)
       "series_style": {
           # Per-series style overrides
       },
   }

Example: Dark Theme
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   DARK_THEME = {
       "legend": {
           "font_size": "11px",
           "legend_padding": 0.25,
           "position": "topright",
       },
       "marker": {
           "marker_size": 3.0,
       },
       "title": {
           "font_size": "18px",
           "font_family": "Arial",
           "font_weight": "bold",
           "font_color": "#E0E0E0",
       },
       "colors": ["#5fab9e", "#f58b51", "#f7dd72", "#db504a", "#2e4756"],
       "v_grid": {
           "stroke": "#444444",
           "stroke_dasharray": None,
       },
       "h_grid": {
           "stroke": "#444444",
           "stroke_dasharray": None,
       },
       "padding": {
           "h_padding": 0.05,
           "v_padding": 0.05,
       },
       "series_style": None,
   }

Creating Custom Themes
----------------------

You can create custom themes by defining a dictionary with the structure above:

.. code-block:: python

   custom_theme = {
       "colors": ["#1e88e5", "#e53935", "#43a047", "#fb8c00"],
       "title": {
           "font_size": "20px",
           "font_weight": "bold",
       },
   }

   chart = BarChart(
       data=[120, 180, 210],
       labels=["Q1", "Q2", "Q3"],
       theme=custom_theme
   )

The theme dictionary is merged with ``DEFAULT_THEME``, so you only need to specify the properties you want to override.

Theme Loading
-------------

Use ``Theme.load()`` to load themes safely:

.. code-block:: python

   from charted.utils.themes import Theme

   # Load by name (returns preset or default)
   theme = Theme.load("dark")

   # Load custom dict (merges with defaults)
   theme = Theme.load({"colors": ["#FF0000", "#00FF00"]})

   # Load None (returns default theme)
   theme = Theme.load(None)

This ensures all required fields are present with proper defaults.
