"""Tests for the annotation layer (line/box/label primitives).

Annotations are positioned in data coordinates and reprojected through the
chart axes, rendered inside the plot-area group alongside legacy reference
lines (h_lines / v_lines).
"""

from charted import AreaChart, ScatterChart
from charted.charts.annotations import (
    BoxAnnotation,
    LabelAnnotation,
    LineAnnotation,
)


def _chart(**kwargs):
    return ScatterChart(
        x_data=[0, 5, 10],
        y_data=[0, 50, 100],
        **kwargs,
    )


def test_line_annotation_renders_segment():
    """LineAnnotation renders a path/line between reprojected coordinates."""
    chart = _chart(annotations=[LineAnnotation((0, 0), (10, 100))])
    el = LineAnnotation((0, 0), (10, 100)).render(chart)

    x0 = chart.x_axis.reproject(0)
    y0 = chart.plot_height - chart.y_axis.reproject(0)
    x1 = chart.x_axis.reproject(10)
    y1 = chart.plot_height - chart.y_axis.reproject(100)

    html = el.html
    assert el.tag in ("path", "line")
    # Reprojected endpoints appear in the emitted markup.
    assert f"M{x0} {y0} L{x1} {y1}" in html or f'x1="{x0}"' in html

    # And the annotation is present in the full chart SVG.
    svg = chart.svg
    assert el.tag in svg


def test_box_annotation_renders_rect():
    """BoxAnnotation renders a shaded rect over the reprojected ranges."""
    box = BoxAnnotation((0, 10), (0, 100))
    el = box.render(_chart())
    assert el.tag == "rect"

    chart = _chart(annotations=[box])
    svg = chart.svg
    assert "<rect" in svg
    # Box is shaded (has a fill, distinct from stroke-only ref lines).
    assert "fill" in el.html
    # Box covers a non-zero region.
    assert float(el.kwargs["width"]) > 0
    assert float(el.kwargs["height"]) > 0


def test_label_annotation_renders_text():
    """LabelAnnotation renders a <text> element at the reprojected point."""
    label = LabelAnnotation((5, 50), "peak")
    el = label.render(_chart())
    assert el.tag == "text"
    assert "peak" in el.html

    chart = _chart(annotations=[label])
    assert "peak" in chart.svg


def test_existing_h_lines_still_work():
    """Legacy h_lines / v_lines keep producing dashed reference lines."""
    chart = _chart(h_lines=[25.0, 75.0], v_lines=[2.5, 7.5])
    svg = chart.svg
    # Four dashed reference lines as before.
    assert svg.count("stroke-dasharray") >= 4
    assert "6 3" in svg


def test_annotations_clipped_to_plot():
    """User annotations render in a group clipped to the plot area.

    The annotation layer translates to the plot origin (like ref lines), and
    user annotations sit inside a nested group carrying the plot clip path so
    out-of-domain boxes/labels cannot bleed over the axes or off-canvas.
    """
    chart = _chart(annotations=[LineAnnotation((0, 0), (10, 100))])
    svg = chart.svg
    # The plot-area annotation group uses the same translate as ref lines.
    expected_transform = f"translate({chart.left_padding}, {chart.top_padding})"
    assert expected_transform in svg
    # The user-annotation sub-group is clipped to the plot area.
    assert 'clip-path="url(#plot-clip)"' in svg


def test_out_of_domain_annotation_is_clipped():
    """An annotation outside the data domain is wrapped in the clip group.

    Data domain is x in [0, 10], y in [0, 100]. A box well outside that range
    would bleed over the axes/off-canvas if it were not clipped. We assert it
    is emitted inside the clipped sub-group, and that the clip path exists.
    """
    # Box far outside the data domain on both axes.
    out_of_domain = BoxAnnotation(x_range=(50, 100), y_range=(500, 1000))
    chart = _chart(annotations=[out_of_domain])
    svg = chart.svg

    # The clip definition exists and the annotation group references it.
    assert '<clipPath id="plot-clip">' in svg
    assert 'clip-path="url(#plot-clip)"' in svg

    # The out-of-domain rect is emitted inside the clipped group rather than
    # directly in the unclipped translate group. We verify ordering: the
    # clip-path attribute appears before the annotation's rect in the markup.
    clip_idx = svg.index('clip-path="url(#plot-clip)"')
    # Find the rect belonging to the annotation (fill-opacity is box-specific).
    rect_idx = svg.index("fill-opacity", clip_idx)
    assert rect_idx > clip_idx

    # Reference lines, by contrast, stay full-span (unclipped): a chart with
    # only h_lines emits a ref-line group with no nested clip-path child.
    ref_only = _chart(h_lines=[50.0])
    ref_group_html = ref_only._render_reference_lines().html
    assert "clip-path" not in ref_group_html


def test_h_lines_implemented_via_annotations():
    """Legacy h_lines / v_lines are expressed internally as LineAnnotations."""
    chart = _chart(h_lines=[25.0], v_lines=[2.5])
    anns = chart._collect_annotations()
    assert any(isinstance(a, LineAnnotation) for a in anns)
    # One h_line + one v_line => at least two line annotations.
    assert sum(isinstance(a, LineAnnotation) for a in anns) >= 2


def test_annotations_round_trip_via_config():
    """to_config() includes annotations so charts can be recreated."""
    chart = _chart(
        annotations=[
            LineAnnotation((0, 0), (10, 100)),
            BoxAnnotation((0, 5), (0, 50)),
            LabelAnnotation((5, 50), "mid"),
        ]
    )
    cfg = chart.to_config()
    assert "annotations" in cfg
    assert len(cfg["annotations"]) == 3


def test_from_config_reconstructs_and_renders():
    """from_config(to_config(c)) rebuilds real annotation objects and renders.

    The serialized form stores annotations as dicts. Without reconstruction,
    render() would raise AttributeError ('dict' has no attribute 'render').
    This asserts the rebuilt chart renders identically to the original.
    """
    original = _chart(
        annotations=[
            LineAnnotation((0, 0), (10, 100)),
            BoxAnnotation((0, 5), (0, 50)),
            LabelAnnotation((5, 50), "mid"),
        ]
    )
    original_svg = original.svg

    cfg = original.to_config()
    # Serialized annotations are plain dicts at this point.
    assert all(isinstance(a, dict) for a in cfg["annotations"])

    rebuilt = ScatterChart.from_config(cfg)

    # Annotations were reconstructed into real objects with render().
    assert len(rebuilt._annotations) == 3
    assert isinstance(rebuilt._annotations[0], LineAnnotation)
    assert isinstance(rebuilt._annotations[1], BoxAnnotation)
    assert isinstance(rebuilt._annotations[2], LabelAnnotation)
    # JSON-style lists were coerced back to tuples.
    assert isinstance(rebuilt._annotations[0].start, tuple)
    assert isinstance(rebuilt._annotations[1].x_range, tuple)
    # Private _ref_* fields are not present in the serialized dicts.
    assert all(not any(k.startswith("_") for k in a) for a in cfg["annotations"])

    # Rendering does not raise and matches the original byte-for-byte.
    assert rebuilt.svg == original_svg


def test_from_config_round_trip_simulates_json():
    """A JSON round-trip (tuples become lists) still reconstructs correctly."""
    import json

    original = _chart(
        annotations=[
            LineAnnotation((1, 2), (3, 4)),
            BoxAnnotation((0, 5), (0, 50)),
        ]
    )
    cfg = json.loads(json.dumps(original.to_config()))
    rebuilt = ScatterChart.from_config(cfg)
    # render() must not raise even though tuples arrived as lists.
    rebuilt.svg  # noqa: B018
    assert rebuilt._annotations[0].start == (1, 2)


def test_area_chart_accepts_and_renders_annotations():
    """AreaChart threads annotations through to the plot-area layer."""
    chart = AreaChart(
        data=[10, 20, 30, 40],
        annotations=[
            BoxAnnotation(x_range=(1, 2), y_range=(10, 30)),
            LabelAnnotation(point=(2, 30), text="spike"),
        ],
    )
    svg = chart.svg
    assert "spike" in svg
    assert "<rect" in svg
    # Drawn inside the clipped user-annotation group.
    assert 'clip-path="url(#plot-clip)"' in svg
