"""Sankey flow diagram.

Renders a directed acyclic flow graph as nodes (rectangles) connected by
proportional ribbons. The layout copies d3-sankey: nodes are assigned to
columns by alignment, then their vertical positions are relaxed over several
iterations so connected nodes line up and ribbons cross as little as possible.
See :mod:`charted.utils.sankey_layout` for the algorithm.
"""

from __future__ import annotations

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
        alignment: Column alignment: ``justify`` / ``left`` / ``right`` /
            ``center``.
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
        label_color = self.theme.resolved_label_color
        midline = (x0 + x1) / 2.0
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

            # Label: to the right of nodes on the left half, to the left of
            # nodes on the right half (d3 convention), so labels point outward.
            name = names[node.index]
            cy = (node.y0 + node.y1) / 2.0
            if node.x0 < midline:
                lx = node.x1 + label_pad
                anchor = "start"
            else:
                lx = node.x0 - label_pad
                anchor = "end"
            result.add_child(
                Text(
                    x=f"{lx:.3f}",
                    y=f"{cy:.3f}",
                    text=name,
                    fill=label_color,
                    font_size=font_size,
                    font_family=self.theme.title_font_family,
                    text_anchor=anchor,
                    dominant_baseline="middle",
                )
            )

        return result

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
