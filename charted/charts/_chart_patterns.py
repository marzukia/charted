"""Pattern-fill and contrasting-outline methods for charts.

Extracted from the :class:`~charted.charts.chart.Chart` base class to reduce
its size. The methods are unchanged; they are mixed back into ``Chart`` via
the class bases, so they continue to operate on the same ``self``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from charted.utils.patterns import Pattern


class ChartPatternMixin:
    """Colourblind-safe redundancy behavior for :class:`Chart`.

    Provides contrasting outlines and pattern fills. These rely on attributes
    supplied by the concrete chart class (``colors``, ``_category_patterns``,
    ``theme``).
    """

    def _pattern_color_count(self) -> int:
        """Number of distinct category colours that may need a pattern tile."""
        colors = getattr(self, "colors", None) or []
        return len(colors)

    def _pattern_defs(self) -> list[Pattern]:
        """Build one ``<pattern>`` def per (category, pattern) the chart uses.

        Returns an empty list unless ``category_patterns`` was enabled, so the
        default ``<defs>`` block is byte-for-byte unchanged. One pattern is
        emitted per colour index, drawn in that index's fill colour, so a hatch
        keeps the underlying category colour while adding a texture channel.
        """
        cycle = getattr(self, "_category_patterns", None)
        if not cycle:
            return []
        from charted.utils.patterns import build_pattern

        colors = getattr(self, "colors", None) or []
        defs: list[Pattern] = []
        for idx, color in enumerate(colors):
            name = cycle[idx % len(cycle)]
            defs.append(build_pattern(self._pattern_id(idx), name, color))
        return defs

    def _pattern_id(self, index: int) -> str:
        """Stable id for the pattern tile of category ``index``."""
        return f"chart-pattern-{id(self) & 0xFFFFFF:x}-{index}"

    def _category_fill(self, index: int, color: str) -> str:
        """Return the fill for category ``index``: a pattern url or the colour.

        With patterns disabled (the default) this returns ``color`` unchanged,
        preserving existing renders. With patterns enabled it returns a
        ``url(#...)`` reference to the matching pattern tile.
        """
        if not getattr(self, "_category_patterns", None):
            return color
        return f"url(#{self._pattern_id(index)})"

    def _filled_outline_attrs(self) -> dict[str, object]:
        """Stroke attributes to apply to a filled shape, or ``{}`` when off.

        Reads the theme's ``filled_shape_outline``; when no outline colour is
        configured (the default and the light/dark presets) this returns an
        empty dict so filled shapes stay unstroked exactly as before. The
        high-contrast preset returns a 1px black outline.
        """
        theme = getattr(self, "theme", None)
        if theme is None:
            return {}
        stroke, width = theme.filled_shape_outline
        if stroke is None:
            return {}
        return {"stroke": stroke, "stroke_width": width}
