"""Sankey diagram layout engine.

A faithful port of d3-sankey's layout algorithm (https://github.com/d3/d3-sankey)
to pure-stdlib Python. Given a directed acyclic graph of nodes and weighted
links it computes, for a fixed drawing rectangle:

* a column (``depth``) for every node, by one of four alignment strategies;
* a horizontal band per column;
* a vertical position and height for every node, sized so each node's height is
  proportional to the larger of its inbound / outbound flow;
* per-link vertical attachment points and widths at both endpoints, so the
  ribbons stack without gaps and each node's stacked link widths sum to the
  node's height (the flow-conservation invariant).

The vertical placement is solved iteratively: nodes are nudged toward the
weighted average of the links touching them (6 relaxation passes alternating
left-to-right and right-to-left), with a collision-resolution sweep after each
pass to enforce the minimum node padding and keep every node inside the frame.

No third-party dependencies: this module is part of the zero-runtime-dependency
``charted`` package.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from charted.utils.exceptions import ChartedError

# d3-sankey defaults.
DEFAULT_NODE_WIDTH = 24.0
DEFAULT_NODE_PADDING = 8.0
DEFAULT_ITERATIONS = 6

# Alignment strategies (d3's nodeAlign equivalents).
ALIGNMENTS = ("justify", "left", "right", "center")


@dataclass
class SankeyNode:
    """A single node in the laid-out diagram.

    ``x0``/``x1``/``y0``/``y1`` are the node rectangle's edges in pixels, filled
    in by :func:`compute_layout`. ``depth`` is the column index from the source
    side; ``height`` the column index from the sink side; ``layer`` the final
    horizontal column used for x-positioning.
    """

    index: int
    name: str
    value: float = 0.0
    depth: int = 0
    height: int = 0
    layer: int = 0
    x0: float = 0.0
    x1: float = 0.0
    y0: float = 0.0
    y1: float = 0.0
    source_links: list[SankeyLink] = field(default_factory=list)
    target_links: list[SankeyLink] = field(default_factory=list)


@dataclass
class SankeyLink:
    """A weighted directed edge plus its laid-out ribbon attachment points.

    ``y0``/``y1`` are the vertical centres of the ribbon where it meets the
    source and target node respectively; ``width`` is the ribbon thickness
    (shared at both ends, proportional to ``value``).
    """

    source: SankeyNode
    target: SankeyNode
    value: float
    index: int
    y0: float = 0.0
    y1: float = 0.0
    width: float = 0.0


@dataclass
class SankeyLayout:
    """Result of :func:`compute_layout`: positioned nodes and links."""

    nodes: list[SankeyNode]
    links: list[SankeyLink]


def _build_graph(
    node_names: list[str],
    raw_links: list[tuple[int, int, float]],
) -> tuple[list[SankeyNode], list[SankeyLink]]:
    """Construct node/link objects and wire up adjacency, with validation."""
    if not node_names:
        raise ChartedError(
            "SankeyChart needs at least one node. "
            "Pass node names via nodes=['A', 'B', ...]."
        )
    if not raw_links:
        raise ChartedError(
            "SankeyChart needs at least one link. "
            "Pass flows via links=[(source, target, value), ...]."
        )

    nodes = [SankeyNode(index=i, name=name) for i, name in enumerate(node_names)]
    n = len(nodes)
    links: list[SankeyLink] = []
    for i, (s, t, v) in enumerate(raw_links):
        if not (0 <= s < n) or not (0 <= t < n):
            raise ChartedError(
                f"links[{i}] references node index out of range: "
                f"({s}, {t}); valid node indices are 0..{n - 1}."
            )
        if s == t:
            raise ChartedError(
                f"links[{i}] is a self-loop ({s} -> {t}); "
                "Sankey diagrams require source != target."
            )
        if v < 0:
            raise ChartedError(
                f"links[{i}] has a negative value ({v}); flow values must be >= 0."
            )
        link = SankeyLink(source=nodes[s], target=nodes[t], value=float(v), index=i)
        nodes[s].source_links.append(link)
        nodes[t].target_links.append(link)
        links.append(link)
    return nodes, links


def _compute_node_values(nodes: list[SankeyNode]) -> None:
    """Node value = max(sum inbound, sum outbound), as in d3."""
    for node in nodes:
        out_sum = sum(link.value for link in node.source_links)
        in_sum = sum(link.value for link in node.target_links)
        node.value = max(out_sum, in_sum)


def _compute_node_depths(nodes: list[SankeyNode]) -> int:
    """Forward longest-path BFS assigning ``depth``; detects cycles.

    Returns the number of columns (max depth + 1).
    """
    n = len(nodes)
    current = list(nodes)
    x = 0
    while current:
        nxt: list[SankeyNode] = []
        seen: set[int] = set()
        for node in current:
            node.depth = x
            for link in node.source_links:
                if link.target.index not in seen:
                    seen.add(link.target.index)
                    nxt.append(link.target)
        x += 1
        if x > n:
            raise ChartedError(
                "SankeyChart links form a cycle; the flow graph must be a DAG "
                "(directed acyclic graph). Remove the back-edge and retry."
            )
        current = nxt
    return x


def _compute_node_heights(nodes: list[SankeyNode]) -> None:
    """Reverse BFS assigning ``height`` (distance from the sink side)."""
    n = len(nodes)
    current = list(nodes)
    x = 0
    while current:
        nxt: list[SankeyNode] = []
        seen: set[int] = set()
        for node in current:
            node.height = x
            for link in node.target_links:
                if link.source.index not in seen:
                    seen.add(link.source.index)
                    nxt.append(link.source)
        x += 1
        if x > n:
            raise ChartedError(
                "SankeyChart links form a cycle; the flow graph must be a DAG."
            )
        current = nxt


def _assign_layers(nodes: list[SankeyNode], n_cols: int, alignment: str) -> int:
    """Assign each node's final ``layer`` per the alignment strategy.

    Returns the number of distinct columns actually used.
    """
    for node in nodes:
        if alignment == "left":
            node.layer = node.depth
        elif alignment == "right":
            node.layer = n_cols - 1 - node.height
        elif alignment == "center":
            # Sources (no inbound) stay at depth; everything else as left.
            node.layer = node.depth
        else:  # justify (default): sinks pushed to the far right column.
            if not node.source_links:
                node.layer = n_cols - 1
            else:
                node.layer = node.depth
    used = {node.layer for node in nodes}
    return max(used) + 1 if used else 1


def _columns(nodes: list[SankeyNode], n_cols: int) -> list[list[SankeyNode]]:
    """Group nodes by ``layer`` into ordered columns."""
    cols: list[list[SankeyNode]] = [[] for _ in range(n_cols)]
    for node in nodes:
        cols[node.layer].append(node)
    # Deterministic vertical order within a column: by original index.
    for col in cols:
        col.sort(key=lambda nd: nd.index)
    return cols


def _initialize_breadths(
    columns: list[list[SankeyNode]],
    y0: float,
    y1: float,
    node_padding: float,
) -> None:
    """Set initial node y0/y1 by scaling each column's values to the height."""
    ky = float("inf")
    for col in columns:
        if not col:
            continue
        total = sum(node.value for node in col)
        avail = (y1 - y0) - (len(col) - 1) * node_padding
        if total > 0:
            ky = min(ky, avail / total)
    if ky == float("inf") or ky <= 0:
        ky = 1.0
    for col in columns:
        y = y0
        for node in col:
            node.y0 = y
            node.y1 = y + node.value * ky
            y = node.y1 + node_padding
        # Centre each column vertically in the frame.
        if col:
            used = col[-1].y1 - col[0].y0
            shift = (y1 - y0 - used) / 2.0
            if shift > 0:
                for node in col:
                    node.y0 += shift
                    node.y1 += shift


def _target_top(source: SankeyNode, target: SankeyNode, node_padding: float) -> float:
    """Ideal top for ``target`` so its ribbon from ``source`` lines up.

    Mirrors d3's ``targetTop``: walk the source's outbound links (which are
    sorted by target y) accumulating widths until we reach this link, then back
    off the target's already-consumed inbound widths.
    """
    y = source.y0 - (len(source.source_links) - 1) * node_padding / 2.0
    for link in source.source_links:
        if link.target is target:
            break
        y += link.width + node_padding
    for link in target.target_links:
        if link.source is source:
            break
        y -= link.width
    return y


def _source_top(source: SankeyNode, target: SankeyNode, node_padding: float) -> float:
    """Ideal top for ``source`` so its ribbon to ``target`` lines up (d3 sourceTop)."""
    y = target.y0 - (len(target.target_links) - 1) * node_padding / 2.0
    for link in target.target_links:
        if link.source is source:
            break
        y += link.width + node_padding
    for link in source.source_links:
        if link.target is target:
            break
        y -= link.width
    return y


def _resolve_collisions(
    col: list[SankeyNode],
    y0: float,
    y1: float,
    node_padding: float,
) -> None:
    """Enforce node padding and clamp the whole column inside [y0, y1].

    Two ordered sweeps, mirroring d3's resolveCollisions: first push nodes down
    so none overlaps the one above it and the column's top clears ``y0``; then
    push nodes back up from the bottom so the column's bottom clears ``y1``.
    With the column ordered top-to-bottom this guarantees containment whenever
    the column's intrinsic height (sum of node heights plus padding gaps) fits
    in the frame, which initialize_breadths sizes it to.
    """
    if not col:
        return
    col.sort(key=lambda nd: nd.y0)

    # Top-to-bottom: separate overlaps and lift the first node to y0 if needed.
    y = y0
    for node in col:
        dy = y - node.y0
        if dy > 0:
            node.y0 += dy
            node.y1 += dy
        y = node.y1 + node_padding

    # Bottom-to-top: pull the stack up so the last node clears y1.
    y = y1
    for node in reversed(col):
        dy = node.y1 - y
        if dy > 0:
            node.y0 -= dy
            node.y1 -= dy
        y = node.y0 - node_padding


def _relax_left_to_right(
    columns: list[list[SankeyNode]], node_padding: float, alpha: float
) -> None:
    for col in columns:
        for target in col:
            if not target.target_links:
                continue
            y = 0.0
            w = 0.0
            for link in target.target_links:
                weight = link.value * (target.layer - link.source.layer)
                y += _target_top(link.source, target, node_padding) * weight
                w += weight
            if w > 0:
                dy = (y / w - target.y0) * alpha
                target.y0 += dy
                target.y1 += dy


def _relax_right_to_left(
    columns: list[list[SankeyNode]], node_padding: float, alpha: float
) -> None:
    for col in reversed(columns):
        for source in col:
            if not source.source_links:
                continue
            y = 0.0
            w = 0.0
            for link in source.source_links:
                weight = link.value * (link.target.layer - source.layer)
                y += _source_top(source, link.target, node_padding) * weight
                w += weight
            if w > 0:
                dy = (y / w - source.y0) * alpha
                source.y0 += dy
                source.y1 += dy


def _reorder_links(nodes: list[SankeyNode]) -> None:
    """Sort each node's links by the y-position of the node at the other end.

    This is what keeps ribbons from crossing unnecessarily: at every node the
    inbound links stack in the vertical order of their sources, and outbound in
    the order of their targets.
    """
    for node in nodes:
        node.source_links.sort(key=lambda link: link.target.y0)
        node.target_links.sort(key=lambda link: link.source.y0)


def _compute_link_breadths(nodes: list[SankeyNode]) -> None:
    """Assign each link its width and its y0/y1 centres, stacked at each node."""
    for node in nodes:
        # Stack outbound links down the source node's right edge.
        y = node.y0
        for link in node.source_links:
            link.y0 = y + link.width / 2.0
            y += link.width
        # Stack inbound links down the target node's left edge.
        y = node.y0
        for link in node.target_links:
            link.y1 = y + link.width / 2.0
            y += link.width


def compute_layout(
    node_names: list[str],
    raw_links: list[tuple[int, int, float]],
    *,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    node_width: float = DEFAULT_NODE_WIDTH,
    node_padding: float = DEFAULT_NODE_PADDING,
    iterations: int = DEFAULT_ITERATIONS,
    alignment: str = "justify",
) -> SankeyLayout:
    """Lay out a Sankey diagram inside the rectangle (x0, y0)-(x1, y1).

    Args:
        node_names: Display names; their indices are the link endpoints.
        raw_links: ``(source_index, target_index, value)`` triples.
        x0, y0, x1, y1: Drawing rectangle in pixels.
        node_width: Node rectangle width in pixels.
        node_padding: Minimum vertical gap between nodes in a column.
        iterations: Relaxation passes (d3 default 6).
        alignment: One of ``justify`` / ``left`` / ``right`` / ``center``.

    Returns:
        A :class:`SankeyLayout` with positioned nodes and links.

    Raises:
        ChartedError: On empty input, unknown node refs, negative values,
            self-loops, or cyclic (non-DAG) graphs.
    """
    if alignment not in ALIGNMENTS:
        raise ChartedError(
            f"Unknown Sankey alignment {alignment!r}; choose one of {list(ALIGNMENTS)}."
        )

    nodes, links = _build_graph(node_names, raw_links)
    _compute_node_values(nodes)
    n_cols = _compute_node_depths(nodes)
    _compute_node_heights(nodes)
    n_used = _assign_layers(nodes, n_cols, alignment)

    # Horizontal positions: spread columns evenly across the frame.
    if n_used > 1:
        kx = (x1 - x0 - node_width) / (n_used - 1)
    else:
        kx = 0.0
    for node in nodes:
        node.x0 = x0 + node.layer * kx
        node.x1 = node.x0 + node_width

    columns = _columns(nodes, n_used)
    _initialize_breadths(columns, y0, y1, node_padding)

    # First link-width estimate so target/source-top can stack ribbons.
    for link in links:
        link.width = 0.0
    _set_link_widths(columns, node_padding)
    _reorder_links(nodes)

    # Iterative relaxation (alternating directions), d3-style alpha decay.
    for i in range(iterations):
        alpha = 0.99**i
        _relax_right_to_left(columns, node_padding, alpha)
        for col in columns:
            _resolve_collisions(col, y0, y1, node_padding)
        _reorder_links(nodes)
        _set_link_widths(columns, node_padding)

        _relax_left_to_right(columns, node_padding, alpha)
        for col in columns:
            _resolve_collisions(col, y0, y1, node_padding)
        _reorder_links(nodes)
        _set_link_widths(columns, node_padding)

    _compute_link_breadths(nodes)
    return SankeyLayout(nodes=nodes, links=links)


def _node_ratio(node: SankeyNode) -> float:
    """Pixels of height per unit of flow value for this node."""
    if node.value <= 0:
        return 0.0
    return (node.y1 - node.y0) / node.value


def _set_link_widths(columns: list[list[SankeyNode]], node_padding: float) -> None:
    """Scale every link width to the tighter of its two endpoints' ratios.

    Each node's height encodes ``value * ky``, so a link of value ``v`` at a
    node of value ``V`` and pixel height ``H`` would be ``v / V * H`` wide.
    A link is shared by two nodes whose ratios may differ; taking the smaller
    keeps stacked link widths from overflowing either node, preserving the
    flow-conservation invariant (per-node stacked widths sum to node height
    when the node's own ratio is the binding one).
    """
    for col in columns:
        for node in col:
            ratio = _node_ratio(node)
            for link in node.source_links:
                src_ratio = ratio
                tgt_ratio = _node_ratio(link.target)
                link.width = link.value * min(src_ratio, tgt_ratio)
