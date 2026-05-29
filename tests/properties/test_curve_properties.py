"""Property-based tests for curve interpolation.

Invariant: a curved path emits the same number of anchor vertices as the
input had points. Smoothing changes how points join, never how many there
are, so no data point may be dropped.
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from charted.utils.curves import cardinal_path, linear_path, step_path


def _anchor_count(path_d: str, curve: str) -> int:
    """Count the data-point anchors in a generated path string.

    - linear: one M plus one L per subsequent point.
    - step: one M, then each subsequent point contributes an H then a V
      (the V lands on the point's y, the H carries its x).
    - cardinal: one M, then one C cubic per subsequent point (the C's
      endpoint is the data point).
    """
    if curve == "linear":
        return path_d.count("M") + path_d.count("L")
    if curve == "cardinal":
        # Each later point is one cubic C; the 2-point case degrades to an L.
        return path_d.count("M") + path_d.count("C") + path_d.count("L")
    if curve == "step":
        # Each step adds a V landing on the new point; M anchors the first.
        return path_d.count("M") + path_d.count("V")
    raise ValueError(curve)


@st.composite
def point_lists(draw):
    n = draw(st.integers(min_value=2, max_value=20))
    xs = sorted(
        draw(
            st.lists(
                st.floats(
                    min_value=-1000,
                    max_value=1000,
                    allow_nan=False,
                    allow_infinity=False,
                ),
                min_size=n,
                max_size=n,
                unique=True,
            )
        )
    )
    pts = []
    for x in xs:
        y = draw(
            st.floats(
                min_value=-1000,
                max_value=1000,
                allow_nan=False,
                allow_infinity=False,
            )
        )
        pts.append((x, y))
    return pts


@given(points=point_lists())
@settings(max_examples=200)
def test_step_preserves_vertex_count(points):
    d = step_path(points)
    assert _anchor_count(d, "step") == len(points)


@given(points=point_lists())
@settings(max_examples=200)
def test_cardinal_preserves_vertex_count(points):
    d = cardinal_path(points)
    assert _anchor_count(d, "cardinal") == len(points)


@given(points=point_lists())
@settings(max_examples=200)
def test_linear_preserves_vertex_count(points):
    d = linear_path(points)
    assert _anchor_count(d, "linear") == len(points)
