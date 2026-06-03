"""Colourblind-safe hatch/pattern fills for filled chart shapes.

Patterns add a second, redundant channel on top of fill colour so that
categories stay distinguishable for readers with colour vision deficiency (and
in greyscale print). Each pattern is emitted once as an SVG ``<pattern>`` in
the chart ``<defs>`` and referenced by filled shapes via ``url(#id)``.

The geometry of each pattern is drawn in the fill colour, on a transparent
tile, so the underlying colour still reads through. This keeps the pattern a
texture overlay rather than a flat replacement of the colour channel.
"""

from __future__ import annotations

from charted.html.element import Element

# The built-in hatch cycle. Names chosen to be visually distinct from each
# other under the common forms of colour vision deficiency and in greyscale.
DEFAULT_PATTERN_CYCLE = [
    "diagonal",
    "horizontal",
    "vertical",
    "grid",
    "dots",
    "diagonal-back",
]


class Pattern(Element):
    """An SVG ``<pattern>`` tile."""

    tag = "pattern"


def resolve_pattern_cycle(spec: list[str] | bool | None) -> list[str] | None:
    """Normalise the ``category_patterns`` argument to a list or None.

    ``None`` / ``False`` disable patterns (fills stay flat colour). ``True``
    selects the built-in cycle. A non-empty list is used verbatim.
    """
    if spec is None or spec is False:
        return None
    if spec is True:
        return list(DEFAULT_PATTERN_CYCLE)
    if isinstance(spec, list) and spec:
        return list(spec)
    return None


def _pattern_geometry(name: str, color: str, size: float, stroke_width: float):
    """Return the child SVG element(s) drawing one pattern's geometry."""
    from charted.html.element import Circle, Path

    s = size
    sw = stroke_width
    if name == "horizontal":
        return [Path(d=f"M0,{s / 2} L{s},{s / 2}", stroke=color, stroke_width=sw)]
    if name == "vertical":
        return [Path(d=f"M{s / 2},0 L{s / 2},{s}", stroke=color, stroke_width=sw)]
    if name == "grid":
        return [
            Path(d=f"M0,{s / 2} L{s},{s / 2}", stroke=color, stroke_width=sw),
            Path(d=f"M{s / 2},0 L{s / 2},{s}", stroke=color, stroke_width=sw),
        ]
    if name == "dots":
        return [Circle(cx=s / 2, cy=s / 2, r=max(0.8, s * 0.18), fill=color)]
    if name == "diagonal-back":
        return [
            Path(
                d=f"M0,0 L{s},{s} M{-s},0 L0,{s} M0,{-s} L{s},0",
                stroke=color,
                stroke_width=sw,
                fill="none",
            )
        ]
    # default: forward diagonal hatch
    return [
        Path(
            d=f"M0,{s} L{s},0 M{-s / 2},{s / 2} L{s / 2},{-s / 2} "
            f"M{s / 2},{s + s / 2} L{s + s / 2},{s / 2}",
            stroke=color,
            stroke_width=sw,
            fill="none",
        )
    ]


def build_pattern(
    pattern_id: str,
    name: str,
    color: str,
    *,
    size: float = 8.0,
    stroke_width: float = 1.2,
) -> Pattern:
    """Build one ``<pattern>`` tile drawn in ``color`` on a transparent ground.

    Args:
        pattern_id: ``id`` attribute referenced by ``url(#id)`` fills.
        name: Pattern name (see ``DEFAULT_PATTERN_CYCLE``).
        color: Colour the hatch geometry is drawn in.
        size: Tile size in user units.
        stroke_width: Line weight for stroked patterns.
    """
    pattern = Pattern(
        id=pattern_id,
        patternUnits="userSpaceOnUse",
        width=size,
        height=size,
    )
    for child in _pattern_geometry(name, color, size, stroke_width):
        pattern.add_child(child)
    return pattern
