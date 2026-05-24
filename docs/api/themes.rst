Themes API
==========

charted includes a modern, type-safe theming system using frozen dataclasses for immutability and IDE support.

Built-in Themes
---------------

Three presets are available:

- ``"dark"`` — Dark background with high-contrast light colors
- ``"light"`` — Light background with subtle grid lines (default)
- ``"high-contrast"`` — Maximum visibility with bold colors

Using ``Theme.from_preset()`` to load a theme:

.. code-block:: python

   from charted import BarChart
   from charted.themes import Theme

   # Use built-in theme by name
   chart = BarChart(
       data=[120, 180, 210],
       labels=["Q1", "Q2", "Q3"],
       theme=Theme.from_preset("dark")
   )

   # Or pass the string directly — charts accept preset names
   chart = BarChart(
       data=[120, 180, 210],
       labels=["Q1", "Q2", "Q3"],
       theme="dark"
   )

   # Compose overrides on top of a preset
   custom = Theme.from_preset("dark").compose(Theme(
       colors=["#FF6B6B", "#4ECDC4", "#45B7D1"],
       title_font_size=24,
   ))
   chart = BarChart(
       data=[120, 180, 210],
       labels=["Q1", "Q2", "Q3"],
       theme=custom
   )

Theme Dataclass
---------------

.. autoclass:: charted.themes.Theme
   :members:
   :undoc-members:
   :show-inheritance:

   **Fields:**

   - ``colors`` — List of hex color strings (default 5-color palette)
   - ``grid_color`` — Grid line color (default "#CCCCCC")
   - ``grid_dasharray`` — Dash pattern for grid (e.g., "2,2"), None = solid
   - ``grid_visible`` — Show/hide grid lines (default True)
   - ``legend_position`` — "topright", "topleft", "bottomright", "bottomleft"
   - ``legend_font_size`` — Legend text size (default 11)
   - ``legend_font_family`` — Legend font (default "Arial")
   - ``legend_font_color`` — Legend text color (default "#444444")
   - ``title_color`` — Chart title color (default "#444444")
   - ``title_font_size`` — Title size (default 16)
   - ``title_font_family`` — Title font (default "Arial")
   - ``background_color`` — Chart background (default "#FFFFFF")
   - ``h_padding`` — Horizontal padding as fraction (default 0.05)
   - ``v_padding`` — Vertical padding as fraction (default 0.05)
   - ``marker_size`` — Data point marker size (default 3.0)
   - ``arrow_color`` — Dependency arrow color for Gantt charts (default "#555555")

   **Class Methods:**

   - ``from_preset(name)`` — Load a built-in theme ("light", "dark", "high-contrast")
   - ``compose(overrides)`` — Return new Theme with overrides layered on top

ColorPalette
------------

.. autoclass:: charted.themes.ColorPalette
   :members:
   :undoc-members:
   :show-inheritance:

   Frozen dataclass for automatic color cycling. Used internally by charts.

   **Methods:**

   - ``get_color(index)`` — Get color at index, cycling through the palette
   - ``expand(min_colors)`` — Expand palette with generated HSL colors if needed

Named Palettes
--------------

charted provides named color palettes accessible via ``resolve_palette()``:

.. code-block:: python

   from charted.themes.core import NAMED_PALETTES, resolve_palette

   # Available palettes
   print(list(NAMED_PALETTES.keys()))
   # ['default', 'viridis', 'ocean', 'categorical', 'rainbow',
   #  'monochrome', 'pastel', 'sunset', 'forest', 'inferno']

   colors = resolve_palette("viridis")

Theme Registration
------------------

Register custom themes globally for reuse:

.. code-block:: python

   from charted import register_theme, list_themes, get_theme
   from charted.themes import Theme

   register_theme("corporate", Theme(
       colors=["#1a365d", "#2b6cb0", "#3182ce", "#4299e1", "#63b3ed"],
       background_color="#f7fafc"
   ))

   # Now usable by name
   chart = BarChart(data=[1, 2, 3], labels=["a", "b", "c"], theme="corporate")

   # List all available themes
   print(list_themes())

Theme Validation
----------------

.. autofunction:: charted.themes.validate_theme

   Validate a theme for WCAG contrast compliance. Returns a list of warning strings
   for any issues found (e.g., insufficient contrast between legend text and background).
