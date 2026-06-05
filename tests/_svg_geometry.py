"""Canonical SVG geometry utilities for property-based invariant tests.

This module parses a chart's rendered SVG and computes the *absolute*
bounding box of any element by walking the nested ``<g transform=...>``
chain and composing translate/rotate/scale into a single affine matrix.

It is deliberately self-contained and dependency-free (stdlib + charted's
own :class:`~charted.fonts.wrapper.Font` for text width). The previous
fix-agents kept rebuilding ad-hoc SVG parsing; this is the shared version.

Coordinate convention: SVG user space, y grows downward. A bounding box is
``(x_min, y_min, x_max, y_max)`` in absolute (root viewBox) coordinates.
"""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass

from charted.fonts.wrapper import Font
from charted.utils.defaults import DEFAULT_FONT, DEFAULT_FONT_SIZE

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

# (x_min, y_min, x_max, y_max) in absolute viewBox coordinates.
BBox = tuple[float, float, float, float]

# Affine matrix as (a, b, c, d, e, f) mapping
#   x' = a*x + c*y + e
#   y' = b*x + d*y + f
# This matches the SVG transform matrix(a b c d e f) convention.
Matrix = tuple[float, float, float, float, float, float]

_IDENTITY: Matrix = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)

# One shared font used to estimate text width/height, matching charted's
# default rendering font. Tests do not vary the font family.
_FONT = Font(family=DEFAULT_FONT)


# ---------------------------------------------------------------------------
# Matrix algebra
# ---------------------------------------------------------------------------


def matrix_multiply(m1: Matrix, m2: Matrix) -> Matrix:
    """Return the composition ``m1 then m2`` is *not* what this does.

    Returns ``m1 * m2`` in the SVG sense: applying the result to a point is
    equivalent to first applying ``m2`` then ``m1``. SVG composes parent then
    child, so a parent matrix ``P`` and child matrix ``C`` compose to
    ``matrix_multiply(P, C)`` and points are mapped by that product.
    """
    a1, b1, c1, d1, e1, f1 = m1
    a2, b2, c2, d2, e2, f2 = m2
    return (
        a1 * a2 + c1 * b2,
        b1 * a2 + d1 * b2,
        a1 * c2 + c1 * d2,
        b1 * c2 + d1 * d2,
        a1 * e2 + c1 * f2 + e1,
        b1 * e2 + d1 * f2 + f1,
    )


def apply_matrix(m: Matrix, x: float, y: float) -> tuple[float, float]:
    """Map a point ``(x, y)`` through affine matrix ``m``."""
    a, b, c, d, e, f = m
    return (a * x + c * y + e, b * x + d * y + f)


def _translate(tx: float, ty: float) -> Matrix:
    return (1.0, 0.0, 0.0, 1.0, tx, ty)


def _scale(sx: float, sy: float) -> Matrix:
    return (sx, 0.0, 0.0, sy, 0.0, 0.0)


def _rotate(deg: float, cx: float = 0.0, cy: float = 0.0) -> Matrix:
    rad = math.radians(deg)
    cos, sin = math.cos(rad), math.sin(rad)
    rot: Matrix = (cos, sin, -sin, cos, 0.0, 0.0)
    if cx == 0.0 and cy == 0.0:
        return rot
    # rotate(a, cx, cy) == translate(cx,cy) rotate(a) translate(-cx,-cy)
    return matrix_multiply(
        _translate(cx, cy),
        matrix_multiply(rot, _translate(-cx, -cy)),
    )


_TRANSFORM_RE = re.compile(r"(matrix|translate|scale|rotate)\s*\(([^)]*)\)")
_NUM_SPLIT_RE = re.compile(r"[\s,]+")


def parse_transform(transform: str | None) -> Matrix:
    """Parse an SVG ``transform`` attribute into a single affine matrix.

    Supports ``matrix``, ``translate``, ``scale`` and ``rotate`` (with or
    without a centre), composed left to right exactly as SVG does.
    """
    if not transform:
        return _IDENTITY
    result = _IDENTITY
    for kind, raw_args in _TRANSFORM_RE.findall(transform):
        args = [float(a) for a in _NUM_SPLIT_RE.split(raw_args.strip()) if a != ""]
        if kind == "matrix" and len(args) == 6:
            m: Matrix = (args[0], args[1], args[2], args[3], args[4], args[5])
        elif kind == "translate":
            tx = args[0] if args else 0.0
            ty = args[1] if len(args) > 1 else 0.0
            m = _translate(tx, ty)
        elif kind == "scale":
            sx = args[0] if args else 1.0
            sy = args[1] if len(args) > 1 else sx
            m = _scale(sx, sy)
        elif kind == "rotate":
            deg = args[0] if args else 0.0
            if len(args) >= 3:
                m = _rotate(deg, args[1], args[2])
            else:
                m = _rotate(deg)
        else:
            m = _IDENTITY
        result = matrix_multiply(result, m)
    return result


def _local_bbox(corners: list[tuple[float, float]], m: Matrix) -> BBox:
    """Map local corner points through ``m`` and return their abs bbox."""
    pts = [apply_matrix(m, x, y) for x, y in corners]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


# ---------------------------------------------------------------------------
# Element wrapper
# ---------------------------------------------------------------------------


def _strip_ns(tag: str) -> str:
    """Drop the ``{namespace}`` prefix ElementTree prepends to tags."""
    return tag.rsplit("}", 1)[-1]


@dataclass
class SvgElement:
    """A leaf SVG element paired with its absolute (composed) matrix."""

    tag: str
    attrib: dict[str, str]
    matrix: Matrix
    text: str | None

    def bbox(self) -> BBox:
        """Absolute bounding box of this element in viewBox coordinates."""
        tag = self.tag
        if tag == "text":
            return self._text_bbox()
        if tag == "rect":
            return self._rect_bbox()
        if tag == "line":
            return self._line_bbox()
        if tag == "circle":
            return self._circle_bbox()
        if tag == "path":
            return self._path_bbox()
        # Unknown leaf: collapse to its transform origin.
        ox, oy = apply_matrix(self.matrix, 0.0, 0.0)
        return (ox, oy, ox, oy)

    # -- per-tag local boxes ------------------------------------------------

    def _font_size(self) -> int:
        raw = self.attrib.get("font-size")
        if raw is None:
            return DEFAULT_FONT_SIZE
        try:
            return int(round(float(raw)))
        except ValueError:
            return DEFAULT_FONT_SIZE

    def _text_bbox(self) -> BBox:
        x = float(self.attrib.get("x", "0") or "0")
        y = float(self.attrib.get("y", "0") or "0")
        text = self.text or ""
        size = self._font_size()
        width = _FONT.measure_width(text, size)
        # Height: font cap/ascent estimate. measure() reports per-glyph height;
        # fall back to the font size so the box is never zero-height.
        _, h = _FONT.measure(text, size)
        height = float(h) if h else float(size)

        anchor = self.attrib.get("text-anchor", "start")
        if anchor == "middle":
            x0 = x - width / 2.0
        elif anchor == "end":
            x0 = x - width
        else:
            x0 = x

        # Vertical placement from the baseline. dominant-baseline central /
        # middle centres the glyph box on y; otherwise treat y as the
        # baseline and grow the box upward by the height.
        baseline = self.attrib.get("dominant-baseline", "")
        if baseline in ("central", "middle"):
            y0 = y - height / 2.0
        elif baseline in ("hanging", "text-before-edge", "bottom"):
            y0 = y
        else:
            y0 = y - height
        corners = [
            (x0, y0),
            (x0 + width, y0),
            (x0 + width, y0 + height),
            (x0, y0 + height),
        ]
        return _local_bbox(corners, self.matrix)

    def _rect_bbox(self) -> BBox:
        x = float(self.attrib.get("x", "0") or "0")
        y = float(self.attrib.get("y", "0") or "0")
        w = float(self.attrib.get("width", "0") or "0")
        h = float(self.attrib.get("height", "0") or "0")
        corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        return _local_bbox(corners, self.matrix)

    def _line_bbox(self) -> BBox:
        x1 = float(self.attrib.get("x1", "0") or "0")
        y1 = float(self.attrib.get("y1", "0") or "0")
        x2 = float(self.attrib.get("x2", "0") or "0")
        y2 = float(self.attrib.get("y2", "0") or "0")
        corners = [(x1, y1), (x2, y2)]
        return _local_bbox(corners, self.matrix)

    def _circle_bbox(self) -> BBox:
        cx = float(self.attrib.get("cx", "0") or "0")
        cy = float(self.attrib.get("cy", "0") or "0")
        r = float(self.attrib.get("r", "0") or "0")
        corners = [
            (cx - r, cy - r),
            (cx + r, cy - r),
            (cx + r, cy + r),
            (cx - r, cy + r),
        ]
        return _local_bbox(corners, self.matrix)

    def _path_bbox(self) -> BBox:
        pts = _path_points(self.attrib.get("d", ""))
        if not pts:
            ox, oy = apply_matrix(self.matrix, 0.0, 0.0)
            return (ox, oy, ox, oy)
        return _local_bbox(pts, self.matrix)


# ---------------------------------------------------------------------------
# Minimal SVG path parser (absolute vertices only)
# ---------------------------------------------------------------------------

_PATH_TOKEN_RE = re.compile(r"([MmLlHhVvCcSsQqTtAaZz])|(-?\d*\.?\d+(?:[eE][-+]?\d+)?)")


def _path_points(d: str) -> list[tuple[float, float]]:
    """Extract on-curve vertices from a path's ``d`` string.

    Handles the absolute and relative commands charted emits (M/L/H/V/C/A/Z).
    Control points of curves are ignored; only the on-curve endpoints are
    collected, which is sufficient to bound the rectangles, polygons and arcs
    charted draws. Returns the visited vertices in absolute path coordinates.
    """
    tokens: list[tuple[str, float]] = []
    for cmd, num in _PATH_TOKEN_RE.findall(d):
        if cmd:
            tokens.append(("cmd", 0.0))
            tokens[-1] = ("cmd:" + cmd, 0.0)
        else:
            tokens.append(("num", float(num)))

    pts: list[tuple[float, float]] = []
    x = y = 0.0
    start_x = start_y = 0.0
    i = 0
    n = len(tokens)
    cur_cmd = ""

    def read_nums(count: int) -> list[float] | None:
        nonlocal i
        out: list[float] = []
        for _ in range(count):
            if i >= n or not tokens[i][0].startswith("num"):
                return None
            out.append(tokens[i][1])
            i += 1
        return out

    while i < n:
        kind, _val = tokens[i]
        if kind.startswith("cmd:"):
            cur_cmd = kind.split(":", 1)[1]
            i += 1
            if cur_cmd in ("Z", "z"):
                x, y = start_x, start_y
                pts.append((x, y))
            continue
        if not cur_cmd:
            i += 1
            continue

        c = cur_cmd
        rel = c.islower()
        cu = c.upper()
        if cu == "M":
            nums = read_nums(2)
            if nums is None:
                break
            x = x + nums[0] if rel else nums[0]
            y = y + nums[1] if rel else nums[1]
            start_x, start_y = x, y
            pts.append((x, y))
            cur_cmd = "l" if rel else "L"
        elif cu == "L":
            nums = read_nums(2)
            if nums is None:
                break
            x = x + nums[0] if rel else nums[0]
            y = y + nums[1] if rel else nums[1]
            pts.append((x, y))
        elif cu == "H":
            nums = read_nums(1)
            if nums is None:
                break
            x = x + nums[0] if rel else nums[0]
            pts.append((x, y))
        elif cu == "V":
            nums = read_nums(1)
            if nums is None:
                break
            y = y + nums[0] if rel else nums[0]
            pts.append((x, y))
        elif cu == "C":
            nums = read_nums(6)
            if nums is None:
                break
            x = x + nums[4] if rel else nums[4]
            y = y + nums[5] if rel else nums[5]
            pts.append((x, y))
        elif cu == "S":
            nums = read_nums(4)
            if nums is None:
                break
            x = x + nums[2] if rel else nums[2]
            y = y + nums[3] if rel else nums[3]
            pts.append((x, y))
        elif cu == "Q":
            nums = read_nums(4)
            if nums is None:
                break
            x = x + nums[2] if rel else nums[2]
            y = y + nums[3] if rel else nums[3]
            pts.append((x, y))
        elif cu == "T":
            nums = read_nums(2)
            if nums is None:
                break
            x = x + nums[0] if rel else nums[0]
            y = y + nums[1] if rel else nums[1]
            pts.append((x, y))
        elif cu == "A":
            nums = read_nums(7)
            if nums is None:
                break
            x = x + nums[5] if rel else nums[5]
            y = y + nums[6] if rel else nums[6]
            pts.append((x, y))
        else:
            i += 1
    return pts


# ---------------------------------------------------------------------------
# Document parsing
# ---------------------------------------------------------------------------


@dataclass
class ParsedSvg:
    """A parsed chart SVG with its viewBox and flattened leaf elements."""

    viewbox: BBox
    elements: list[SvgElement]

    def texts(self) -> list[SvgElement]:
        return [e for e in self.elements if e.tag == "text"]

    def rects(self) -> list[SvgElement]:
        return [e for e in self.elements if e.tag == "rect"]

    def paths(self) -> list[SvgElement]:
        return [e for e in self.elements if e.tag == "path"]


def parse_svg(svg: str) -> ParsedSvg:
    """Parse a chart SVG string into a :class:`ParsedSvg`.

    Walks the element tree, composing every ancestor ``transform`` into each
    leaf's absolute matrix. ``<defs>`` content (clip paths, gradients) is
    skipped because it does not paint directly.
    """
    root = ET.fromstring(svg)
    viewbox = _parse_viewbox(root)
    elements: list[SvgElement] = []
    _walk(root, _IDENTITY, elements)
    return ParsedSvg(viewbox=viewbox, elements=elements)


def _parse_viewbox(root: ET.Element) -> BBox:
    vb = root.get("viewBox")
    if vb:
        nums = [float(p) for p in _NUM_SPLIT_RE.split(vb.strip()) if p != ""]
        if len(nums) == 4:
            return (nums[0], nums[1], nums[0] + nums[2], nums[1] + nums[3])
    w = float(root.get("width", "0") or "0")
    h = float(root.get("height", "0") or "0")
    return (0.0, 0.0, w, h)


_LEAF_TAGS = {
    "text",
    "rect",
    "line",
    "circle",
    "path",
    "polygon",
    "polyline",
    "ellipse",
}
_SKIP_TAGS = {"defs", "clipPath", "linearGradient", "radialGradient", "filter"}


def _walk(node: ET.Element, parent_m: Matrix, out: list[SvgElement]) -> None:
    tag = _strip_ns(node.tag)
    if tag in _SKIP_TAGS:
        return
    local = parse_transform(node.get("transform"))
    matrix = matrix_multiply(parent_m, local)
    if tag in _LEAF_TAGS:
        out.append(
            SvgElement(
                tag=tag,
                attrib=dict(node.attrib),
                matrix=matrix,
                text=(node.text or "").strip() or None,
            )
        )
    for child in node:
        _walk(child, matrix, out)


# ---------------------------------------------------------------------------
# Geometry predicates
# ---------------------------------------------------------------------------


def bbox_inside_viewbox(el: SvgElement, viewbox: BBox, tol: float = 1.0) -> bool:
    """True when ``el``'s absolute bbox lies within ``viewbox`` (± ``tol``)."""
    x0, y0, x1, y1 = el.bbox()
    vx0, vy0, vx1, vy1 = viewbox
    return x0 >= vx0 - tol and y0 >= vy0 - tol and x1 <= vx1 + tol and y1 <= vy1 + tol


def bbox_inside_box(inner: BBox, outer: BBox, tol: float = 1.0) -> bool:
    """True when ``inner`` lies within ``outer`` (± ``tol``)."""
    x0, y0, x1, y1 = inner
    ox0, oy0, ox1, oy1 = outer
    return x0 >= ox0 - tol and y0 >= oy0 - tol and x1 <= ox1 + tol and y1 <= oy1 + tol


def boxes_overlap(a: BBox, b: BBox, tol: float = 0.0) -> bool:
    """True when boxes ``a`` and ``b`` overlap by more than ``tol`` on both axes.

    A positive ``tol`` shrinks each box before testing, so edge-touching or
    sub-pixel kissing boxes are not counted as overlapping.
    """
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    x_overlap = min(ax1, bx1) - max(ax0, bx0)
    y_overlap = min(ay1, by1) - max(ay0, by0)
    return x_overlap > tol and y_overlap > tol


# ---------------------------------------------------------------------------
# Chart-specific extractors
# ---------------------------------------------------------------------------


def plot_area_box(svg: str) -> BBox | None:
    """Return the absolute plot-area rectangle, if the chart defines one.

    charted emits a ``<clipPath id="plot-clip"><rect .../></clipPath>`` whose
    rect carries the plot width/height, and positions the plotted content with
    a sibling ``<g transform="translate(left, top)">``. The plot area is that
    rect translated by the gridline group's offset. We recover the offset from
    the first axis/gridline group's ``transform``.
    """
    root = ET.fromstring(svg)
    clip_rect = None
    for el in root.iter():
        if _strip_ns(el.tag) == "clipPath" and el.get("id") == "plot-clip":
            for child in el:
                if _strip_ns(child.tag) == "rect":
                    clip_rect = child
                    break
    if clip_rect is None:
        return None
    w = float(clip_rect.get("width", "0") or "0")
    h = float(clip_rect.get("height", "0") or "0")

    # Find the plot offset: the most common translate among top-level <g>
    # groups that contain gridline paths. charted uses translate(left, top)
    # for the axis groups. Take the first group with a translate that has a
    # non-zero left offset and a child <path>.
    offset = _find_plot_offset(root)
    if offset is None:
        return None
    left, top = offset
    return (left, top, left + w, top + h)


def _find_plot_offset(root: ET.Element) -> tuple[float, float] | None:
    """Heuristically find the plot group's (left, top) translate offset.

    charted positions gridlines with ``transform="translate(left, top)"`` on
    the gridline ``<path>`` (or its parent ``<g>``), where ``top`` is the plot
    top margin. The plot left/top is the most common ``(left, top)`` among
    pure-translate transforms that share the same ``top`` and the largest
    ``left`` (axis tick-label groups sit a few px further left, so they are
    excluded by taking the max-left member of the dominant ``top`` row).
    """
    translates: list[tuple[float, float]] = []
    for el in root.iter():
        tag = _strip_ns(el.tag)
        if tag in _SKIP_TAGS:
            continue
        raw = el.get("transform")
        if not raw:
            continue
        m = parse_transform(raw)
        a, b, c, d, e, f = m
        is_translate = (
            math.isclose(a, 1.0)
            and math.isclose(b, 0.0)
            and math.isclose(c, 0.0)
            and math.isclose(d, 1.0)
        )
        if is_translate and e > 0 and f > 0:
            translates.append((e, f))
    if not translates:
        return None
    # Group by top (f); the plot's top margin is the smallest positive f that
    # recurs. Within that row, the plot-left is the largest left offset
    # (tick-label groups are shifted left of the true plot origin).
    top = min(f for _, f in translates)
    row = [(e, f) for e, f in translates if math.isclose(f, top)]
    return max(row, key=lambda p: p[0])


def x_axis_tick_label_boxes(parsed: ParsedSvg) -> list[BBox]:
    """Return absolute bboxes of the x-axis tick labels.

    Heuristic: x-axis tick labels are the run of text elements sharing the
    largest y-translation (they sit along the bottom axis). We group text
    elements by their absolute baseline y (rounded) and return the lowest
    such group with more than one member.
    """
    texts = parsed.texts()
    if not texts:
        return []
    rows: dict[int, list[BBox]] = {}
    for t in texts:
        if not (t.text and t.text.strip()):
            continue
        box = t.bbox()
        key = int(round((box[1] + box[3]) / 2.0))
        rows.setdefault(key, []).append(box)
    if not rows:
        return []
    # x-axis labels are along the bottom: the row with the largest centre-y
    # that has at least two labels.
    multi = {k: v for k, v in rows.items() if len(v) >= 2}
    if not multi:
        return []
    bottom_key = max(multi.keys())
    return multi[bottom_key]


_RECT_SUBPATH_RE = re.compile(
    r"M\s*(-?[\d.eE+-]+)\s+(-?[\d.eE+-]+)\s*"
    r"h\s*(-?[\d.eE+-]+)\s*"
    r"v\s*(-?[\d.eE+-]+)\s*"
    r"h\s*(-?[\d.eE+-]+)\s*"
    r"v\s*(-?[\d.eE+-]+)\s*[Zz]"
)


def _rect_subpaths(d: str) -> list[BBox]:
    """Return the local bboxes of every ``M x y h w v h h v v Z`` rect in ``d``.

    charted draws bars, columns and histogram bins as one or more closed
    ``h/v`` rectangles inside a single ``<path d>``. Each match yields the
    rect's local (pre-transform) bounding box.
    """
    boxes: list[BBox] = []
    for mx, my, hw, vh, _hw2, _vh2 in _RECT_SUBPATH_RE.findall(d):
        x = float(mx)
        y = float(my)
        w = float(hw)
        h = float(vh)
        x0, x1 = (x, x + w) if w >= 0 else (x + w, x)
        y0, y1 = (y, y + h) if h >= 0 else (y + h, y)
        boxes.append((x0, y0, x1, y1))
    return boxes


def _is_canvas(box: BBox, viewbox: BBox, tol: float = 0.5) -> bool:
    """True when ``box`` is (approximately) the full viewBox canvas rect."""
    return all(abs(b - v) <= tol for b, v in zip(box, viewbox))


def bar_boxes(parsed: ParsedSvg) -> list[BBox]:
    """Return absolute bboxes of bar/column/histogram-bin rectangles.

    Bars and columns are filled ``<path>`` elements whose ``d`` is one or more
    closed ``h/v`` rectangles. Histogram bins are filled ``<rect>`` elements.
    Gridlines and axes are stroked paths with ``fill="none"`` and the canvas
    background is the full-viewBox rect; both are excluded.
    """
    out: list[BBox] = []
    vb = parsed.viewbox
    for el in parsed.paths():
        fill = el.attrib.get("fill", "")
        if not fill or fill.lower() == "none":
            continue
        for local in _rect_subpaths(el.attrib.get("d", "")):
            lx0, ly0, lx1, ly1 = local
            corners = [(lx0, ly0), (lx1, ly0), (lx1, ly1), (lx0, ly1)]
            box = _local_bbox(corners, el.matrix)
            if not _is_canvas(box, vb):
                out.append(box)
    for el in parsed.rects():
        fill = el.attrib.get("fill", "")
        if not fill or fill.lower() == "none":
            continue
        box = el.bbox()
        if not _is_canvas(box, vb):
            out.append(box)
    return out
