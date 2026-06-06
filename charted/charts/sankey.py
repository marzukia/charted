"""Sankey flow diagram.

Renders a directed acyclic flow graph as nodes (rectangles) connected by
proportional ribbons. The layout copies d3-sankey: nodes are assigned to
columns by alignment, then their vertical positions are relaxed over several
iterations so connected nodes line up and ribbons cross as little as possible.
See :mod:`charted.utils.sankey_layout` for the algorithm.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from charted.charts.chart import Chart
from charted.constants import DEFAULT_FONT_SIZE
from charted.html.element import G, Path, Rect, Text, Title
from charted.themes.core import Theme
from charted.utils.exceptions import ChartedError
from charted.utils.helpers import calculate_text_dimensions
from charted.utils.sankey_layout import (
    DEFAULT_ITERATIONS,
    DEFAULT_NODE_PADDING,
    DEFAULT_NODE_WIDTH,
    SankeyLayout,
    SankeyLink,
    SankeyNode,
    compute_layout,
)
from charted.utils.types import Vector2D

# Reasonable default canvas: wider than tall, flows read left-to-right.
SANKEY_WIDTH = 800
SANKEY_HEIGHT = 500

# Link/Node triple may be given as a tuple or a {source,target,value} dict.
LinkInput = tuple[object, object, float] | dict[str, object]


@dataclass
class _PlacedLabel:
    """A node label resolved to its final anchor point and alignment."""

    x: float
    y: float
    text: str
    anchor: str


def _spread_labels(
    centres: list[float], line_h: float, y0: float, y1: float
) -> list[float]:
    """Nudge a sorted column of label centres so their boxes stop overlapping.

    ``centres`` must be sorted ascending. Each label box is ``line_h`` tall and
    centred on its value, so two labels collide when their centres are closer
    than ``line_h``. We enforce a minimum ``line_h`` gap between consecutive
    centres with the same two-pass sweep the node layout uses: push down to
    open gaps and clear the top, then pull up to clear the bottom. When the
    column is too tall to fit every label, the bottom-up pass wins and the
    stack is packed flush from ``y1`` upward (labels still cannot leave the
    canvas, they just sit gap-to-gap).
    """
    n = len(centres)
    if n <= 1:
        return list(centres)

    out = list(centres)
    half = line_h / 2.0

    # Top-down: each centre at least line_h below the previous, and the first
    # no higher than the top edge allows.
    floor = y0 + half
    for i in range(n):
        lo = floor if i == 0 else out[i - 1] + line_h
        if out[i] < lo:
            out[i] = lo

    # Bottom-up: pull the stack up so the last label clears y1, propagating the
    # minimum gap upward. This both contains the column and, when it overflows,
    # packs the labels flush instead of letting them spill past the canvas.
    ceil = y1 - half
    if out[-1] > ceil:
        out[-1] = ceil
    for i in range(n - 2, -1, -1):
        hi = out[i + 1] - line_h
        if out[i] > hi:
            out[i] = hi
    return out


class SankeyChart(Chart):
    """Sankey diagram for visualising weighted flow between nodes.

    Nodes are drawn as vertical rectangles arranged in columns; the flow
    between two nodes is a ribbon whose thickness is proportional to its value.
    The column assignment and vertical relaxation copy d3-sankey.

    Args:
        nodes: Node names. Links reference nodes by name or by integer index
            into this list.
        links: Flows as ``(source, target, value)`` tuples or
            ``{"source": ..., "target": ..., "value": ...}`` dicts. ``source``
            / ``target`` may be a node name (str) or an index (int).
        width, height: Canvas dimensions in pixels.
        title: Optional chart title.
        theme: Optional theme (name, dict, or Theme).
        node_width: Width of each node rectangle in pixels.
        node_padding: Minimum vertical gap between nodes in a column.
        iterations: Number of layout relaxation passes (d3 default 6).
        alignment: How nodes are assigned to columns. One of:

            * ``justify`` (default, matching d3-sankey): sink nodes (no
              outbound flow) are pushed to the final column, so every terminal
              node lines up on the right edge.
            * ``left``: every node sits at its own depth from the source. Use
              this for **funnel / drop-off data**, where dropout sinks appear at
              many different depths: ``left`` lets each one terminate at its
              natural stage instead of being yanked to the last column, which
              reads as a true funnel staircase. Under ``justify`` the same data
              squashes all the dropouts into one tall final column.
            * ``right``: nodes align to the right by distance from the sink.
            * ``center``: like ``left`` but sources stay at depth 0.
        link_opacity: Ribbon fill opacity (0-1); slight transparency so
            overlaps read.
        show_values: Append each node's total flow to its label.

    Example:
        >>> from charted import SankeyChart
        >>> chart = SankeyChart(
        ...     nodes=["Coal", "Gas", "Grid", "Homes", "Industry"],
        ...     links=[
        ...         ("Coal", "Grid", 30),
        ...         ("Gas", "Grid", 20),
        ...         ("Grid", "Homes", 28),
        ...         ("Grid", "Industry", 22),
        ...     ],
        ...     title="Energy flow",
        ... )
        >>> chart.save("energy.svg")
    """

    render_axes = False

    def __init__(
        self,
        nodes: list[str],
        links: list[LinkInput],
        width: float = SANKEY_WIDTH,
        height: float = SANKEY_HEIGHT,
        title: str | None = None,
        theme: Theme | str | dict[str, object] | None = None,
        node_width: float = DEFAULT_NODE_WIDTH,
        node_padding: float = DEFAULT_NODE_PADDING,
        iterations: int = DEFAULT_ITERATIONS,
        alignment: str = "justify",
        link_opacity: float = 0.45,
        show_values: bool = False,
    ) -> None:
        if not nodes:
            raise ChartedError(
                "SankeyChart needs at least one node. "
                "Pass node names via nodes=['A', 'B', ...]."
            )
        if not links:
            raise ChartedError(
                "SankeyChart needs at least one link. "
                "Pass flows via links=[(source, target, value), ...]."
            )

        self._node_names = list(nodes)
        self._raw_links = self._normalize_links(links, self._node_names)
        self._node_width = float(node_width)
        self._node_padding = float(node_padding)
        self._iterations = int(iterations)
        self._alignment = alignment
        self._link_opacity = float(link_opacity)
        self._show_values = show_values

        # Resolve the palette up front: Chart.__init__ renders the
        # representation during construction, so colours must be ready.
        from charted.utils.theme_manager import ThemeManager

        resolved = ThemeManager.load_theme(theme, "sankey")
        self._palette = list(resolved.resolved_colors)

        # Synthetic minimal data to satisfy the Chart base (it is axis-driven);
        # Sankey draws entirely in its own representation. Mirrors PieChart.
        x_data = cast(Vector2D, [[float(i) for i in range(len(nodes))]])
        y_data = cast(Vector2D, [[0.0, 1.0]])

        super().__init__(
            width=width,
            height=height,
            x_data=x_data,
            y_data=y_data,
            title=title,
            theme=theme,
            chart_type="sankey",
            zero_index=True,
        )

    @staticmethod
    def _normalize_links(
        links: list[LinkInput], node_names: list[str]
    ) -> list[tuple[int, int, float]]:
        """Resolve link endpoints (name or index) to integer node indices."""
        index_of = {name: i for i, name in enumerate(node_names)}
        n = len(node_names)

        def resolve(ref: object, which: str, i: int) -> int:
            if isinstance(ref, bool):
                # bool is an int subclass; reject it explicitly so True/False
                # are not silently treated as node 1/0.
                raise ChartedError(
                    f"links[{i}] {which} is a bool; use a node name or index."
                )
            if isinstance(ref, int):
                if not (0 <= ref < n):
                    raise ChartedError(
                        f"links[{i}] {which} index {ref} out of range (0..{n - 1})."
                    )
                return ref
            if isinstance(ref, str):
                if ref not in index_of:
                    raise ChartedError(
                        f"links[{i}] {which} {ref!r} is not a known node. "
                        f"Known nodes: {node_names}."
                    )
                return index_of[ref]
            raise ChartedError(
                f"links[{i}] {which} must be a node name (str) or index (int), "
                f"got {type(ref).__name__}."
            )

        out: list[tuple[int, int, float]] = []
        for i, link in enumerate(links):
            if isinstance(link, dict):
                if not {"source", "target", "value"} <= set(link):
                    raise ChartedError(
                        f"links[{i}] dict must have 'source', 'target' and "
                        f"'value' keys; got keys {sorted(link)}."
                    )
                s_ref = link["source"]
                t_ref = link["target"]
                v_raw = link["value"]
            else:
                if len(link) != 3:
                    raise ChartedError(
                        f"links[{i}] tuple must be (source, target, value); "
                        f"got {len(link)} elements."
                    )
                s_ref, t_ref, v_raw = link

            if isinstance(v_raw, bool) or not isinstance(v_raw, (int, float)):
                raise ChartedError(
                    f"links[{i}] value must be a number, got {type(v_raw).__name__}."
                )
            value = float(v_raw)
            out.append(
                (resolve(s_ref, "source", i), resolve(t_ref, "target", i), value)
            )
        return out

    @property
    def colors(self) -> list[str]:
        """Node colour palette (read-only)."""
        return self._palette

    def _node_color(self, node: SankeyNode) -> str:
        return self._palette[node.index % len(self._palette)]

    def _link_path(self, link: SankeyLink) -> str:
        """Cubic-bezier ribbon path (d3 sankeyLinkHorizontal).

        A filled path: top edge left-to-right along the ribbon's upper bound,
        then the bottom edge back. Control points sit at the horizontal
        midpoint between the two node edges.
        """
        x0 = link.source.x1
        x1 = link.target.x0
        xm = (x0 + x1) / 2.0
        half = link.width / 2.0
        y0t = link.y0 - half
        y0b = link.y0 + half
        y1t = link.y1 - half
        y1b = link.y1 + half
        return (
            f"M{x0:.3f},{y0t:.3f}"
            f"C{xm:.3f},{y0t:.3f} {xm:.3f},{y1t:.3f} {x1:.3f},{y1t:.3f}"
            f"L{x1:.3f},{y1b:.3f}"
            f"C{xm:.3f},{y1b:.3f} {xm:.3f},{y0b:.3f} {x0:.3f},{y0b:.3f}"
            "Z"
        )

    @property
    def representation(self) -> G:
        """Render the Sankey diagram."""
        result = G()

        font_size = float(DEFAULT_FONT_SIZE)
        label_pad = 6.0
        frame_pad = 4.0

        # Reserve horizontal room for the labels flanking the outer columns so
        # they do not clip off the canvas edge. Estimate from the widest name.
        names = self._display_names()
        max_label_w = max(
            (
                calculate_text_dimensions(name, font_size=font_size).width
                for name in names
            ),
            default=0.0,
        )
        side_pad = max_label_w + label_pad + frame_pad

        top = self.top_padding if self.top_padding else 20.0
        bottom = frame_pad + font_size
        x0 = side_pad
        x1 = self.width - side_pad
        y0 = top
        y1 = self.height - bottom

        # Guard against a frame collapsing on extreme aspect ratios / long
        # labels: keep a minimum positive drawing rectangle.
        if x1 - x0 < self._node_width + 1:
            x0 = frame_pad
            x1 = self.width - frame_pad
        if y1 - y0 < 2:
            y0 = frame_pad
            y1 = self.height - frame_pad

        layout = compute_layout(
            self._node_names,
            self._raw_links,
            x0=x0,
            y0=y0,
            x1=x1,
            y1=y1,
            node_width=self._node_width,
            node_padding=self._node_padding,
            iterations=self._iterations,
            alignment=self._alignment,
        )

        # Links first so nodes sit on top. Each ribbon inherits its source
        # node's colour at slight opacity so overlapping flows still read.
        for link in layout.links:
            color = self._node_color(link.source)
            path = Path(
                d=self._link_path(link),
                fill=color,
                fill_opacity=f"{self._link_opacity:.3f}",
                stroke="none",
            )
            if self._tooltips:
                src = self._node_names[link.source.index]
                tgt = self._node_names[link.target.index]
                path.add_child(Title(text=f"{src} → {tgt}: {link.value:g}"))
            result.add_child(path)

        # Node rectangles.
        for node in layout.nodes:
            color = self._node_color(node)
            rect = Rect(
                x=f"{node.x0:.3f}",
                y=f"{node.y0:.3f}",
                width=f"{node.x1 - node.x0:.3f}",
                height=f"{max(node.y1 - node.y0, 0.0):.3f}",
                fill=color,
            )
            if self._tooltips:
                rect.add_child(
                    Title(text=f"{self._node_names[node.index]}: {node.value:g}")
                )
            result.add_child(rect)

        # Labels, with vertical collision avoidance per column. On dense
        # columns the node centres sit closer than a line of text is tall, so
        # placing every label at its node's centre piles them into an
        # unreadable mush. We measure each label's real height, then nudge the
        # labels in each column apart just enough to stop their boxes
        # overlapping (a relaxation sweep, like the node layout itself).
        for placed in self._place_labels(layout, names, x0, x1, y0, y1, font_size):
            result.add_child(
                Text(
                    x=f"{placed.x:.3f}",
                    y=f"{placed.y:.3f}",
                    text=placed.text,
                    fill=self.theme.resolved_label_color,
                    font_size=font_size,
                    font_family=self.theme.title_font_family,
                    text_anchor=placed.anchor,
                    dominant_baseline="middle",
                )
            )

        return result

    def _place_labels(
        self,
        layout: SankeyLayout,
        names: list[str],
        x0: float,
        x1: float,
        y0: float,
        y1: float,
        font_size: float,
    ) -> list[_PlacedLabel]:
        """Position node labels, nudging overlapping ones apart vertically.

        Each label starts at its node's vertical centre and flanks the node on
        the outward side (right of left-half nodes, left of right-half nodes,
        the d3 convention). Within a column we then relax the label centres so
        no two label boxes overlap: a column may pack node centres tighter than
        a text line is tall, which would otherwise smear the labels together.

        The nudge keeps the original vertical order, uses the font's measured
        line height for the spacing, and clamps the whole stack inside
        ``[y0, y1]`` so labels never run off the canvas.
        """
        label_pad = 6.0
        midline = (x0 + x1) / 2.0

        # Measured line height for the label font; the same value for every
        # label since they share size and family. Fall back to the font size if
        # the measurer reports nothing (never zero, so boxes always have area).
        line_h = calculate_text_dimensions("Ag", font_size=int(font_size)).height
        if line_h <= 0:
            line_h = font_size

        # Group nodes by column so each column relaxes independently.
        columns: dict[int, list[SankeyNode]] = {}
        for node in layout.nodes:
            columns.setdefault(node.layer, []).append(node)

        placed: list[_PlacedLabel] = []
        for col_nodes in columns.values():
            col_nodes.sort(key=lambda nd: (nd.y0 + nd.y1) / 2.0)
            centres = [(nd.y0 + nd.y1) / 2.0 for nd in col_nodes]
            centres = _spread_labels(centres, line_h, y0, y1)
            for node, cy in zip(col_nodes, centres):
                if node.x0 < midline:
                    lx = node.x1 + label_pad
                    anchor = "start"
                else:
                    lx = node.x0 - label_pad
                    anchor = "end"
                placed.append(
                    _PlacedLabel(
                        x=lx, y=cy, text=names[node.index], anchor=anchor
                    )
                )
        return placed

    def _display_names(self) -> list[str]:
        """Node labels, optionally annotated with each node's total flow."""
        if not self._show_values:
            return list(self._node_names)
        totals: dict[int, float] = {i: 0.0 for i in range(len(self._node_names))}
        for s, t, v in self._raw_links:
            totals[s] += v
        # A node's value is max of in/out; recompute inbound too.
        inbound: dict[int, float] = {i: 0.0 for i in range(len(self._node_names))}
        for _s, t, v in self._raw_links:
            inbound[t] += v
        names = []
        for i, name in enumerate(self._node_names):
            val = max(totals[i], inbound[i])
            names.append(f"{name} ({val:g})")
        return names
