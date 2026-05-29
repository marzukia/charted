"""Pure curve-interpolation helpers for line and area charts.

Each function takes a list of ``(x, y)`` points and returns an SVG path
``d`` string. These are path-generation only: the points themselves are
never moved or dropped, only the way consecutive points join changes.

Supported curves:

- ``linear``: straight ``L`` segments between points (the default).
- ``step``: axis-aligned segments, horizontal to the next x, then
  vertical to the next y.
- ``cardinal`` / ``basis``: a smooth Catmull-Rom spline expressed as
  cubic Beziers. The spline interpolates (passes exactly through) every
  data point, including the first and last. ``basis`` is an alias for the
  same behavior here: it is documented to pin its endpoints rather than
  float inside the convex hull like a classic uniform B-spline, so
  markers and labels stay aligned with the rendered line.
"""

from __future__ import annotations

Point = tuple[float, float]

#: Curve names accepted by the charts.
VALID_CURVES = ("linear", "step", "cardinal", "basis")

#: Default Catmull-Rom tension. 0 gives the standard, fairly loose spline;
#: higher values tighten it toward straight lines.
DEFAULT_TENSION = 0.0


def _fmt(value: float) -> str:
    """Format a coordinate for an SVG path.

    Mirrors ``line_renderer.round_coordinate``: round to one decimal and
    stringify. Integer inputs stay integer-formatted ("3"), floats keep a
    decimal ("3.0"), which is what the existing renderer emits.
    """
    rounded = round(value, 1)
    return str(rounded)


def linear_path(points: list[Point]) -> str:
    """Build a polyline path: ``M`` then one ``L`` per following point."""
    if not points:
        return ""
    parts = [f"M{_fmt(points[0][0])} {_fmt(points[0][1])}"]
    for x, y in points[1:]:
        parts.append(f"L{_fmt(x)} {_fmt(y)}")
    return " ".join(parts)


def step_path(points: list[Point]) -> str:
    """Build an axis-aligned step path.

    From each point, move horizontally to the next point's x, then
    vertically onto the next point's y. The vertical move lands the path
    exactly on every data point.
    """
    if not points:
        return ""
    parts = [f"M{_fmt(points[0][0])} {_fmt(points[0][1])}"]
    for x, y in points[1:]:
        parts.append(f"H{_fmt(x)}")
        parts.append(f"V{_fmt(y)}")
    return " ".join(parts)


def cardinal_path(points: list[Point], tension: float = DEFAULT_TENSION) -> str:
    """Build a smooth Catmull-Rom spline as cubic Beziers.

    The curve interpolates every point. Endpoints are handled by
    duplicating the first and last points, so the path starts at the first
    data point and ends at the last. Each segment between two consecutive
    points is one cubic ``C`` command, so the number of anchor vertices
    equals the number of input points.

    Args:
        points: Ordered ``(x, y)`` data points.
        tension: Catmull-Rom tension in ``[0, 1]``. 0 is the standard
            spline; 1 collapses control points toward the endpoints
            (straighter lines).
    """
    n = len(points)
    if n == 0:
        return ""
    if n == 1:
        return f"M{_fmt(points[0][0])} {_fmt(points[0][1])}"
    if n == 2:
        # Nothing to smooth between two points.
        return linear_path(points)

    # Scale factor for control-point handles. Standard Catmull-Rom uses
    # 1/6 of the chord between neighbours; tension shrinks that toward 0.
    scale = (1.0 - tension) / 6.0

    parts = [f"M{_fmt(points[0][0])} {_fmt(points[0][1])}"]
    for i in range(n - 1):
        p0 = points[i - 1] if i > 0 else points[0]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[i + 2] if i + 2 < n else points[n - 1]

        c1x = p1[0] + (p2[0] - p0[0]) * scale
        c1y = p1[1] + (p2[1] - p0[1]) * scale
        c2x = p2[0] - (p3[0] - p1[0]) * scale
        c2y = p2[1] - (p3[1] - p1[1]) * scale

        parts.append(
            f"C{_fmt(c1x)} {_fmt(c1y)} "
            f"{_fmt(c2x)} {_fmt(c2y)} "
            f"{_fmt(p2[0])} {_fmt(p2[1])}"
        )
    return " ".join(parts)


#: ``basis`` shares the cardinal implementation (endpoint-pinned spline).
basis_path = cardinal_path


def curve_path(curve: str, points: list[Point]) -> str:
    """Dispatch to the path builder for ``curve``.

    Raises:
        ValueError: If ``curve`` is not a recognized name.
    """
    if curve == "linear":
        return linear_path(points)
    if curve == "step":
        return step_path(points)
    if curve in ("cardinal", "basis"):
        return cardinal_path(points)
    raise ValueError(
        f"Unknown curve {curve!r}. Valid options: {', '.join(VALID_CURVES)}"
    )
