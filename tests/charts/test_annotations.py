"""Tests for the annotation layer (line/box/label primitives).

Annotations are positioned in data coordinates and reprojected through the
chart axes, rendered inside the plot-area group alongside legacy reference
lines (h_lines / v_lines).
"""

from charted import ScatterChart
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
    """Annotations render inside the plot-area group, not over the axes."""
    chart = _chart(annotations=[LineAnnotation((0, 0), (10, 100))])
    svg = chart.svg
    # The plot-area annotation group uses the same translate as ref lines.
    expected_transform = f"translate({chart.left_padding}, {chart.top_padding})"
    assert expected_transform in svg


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
