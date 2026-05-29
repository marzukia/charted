"""Anchor tests for the annotation primitive (feature-parity roadmap, feature 5).

Placeholders for charted/charts/annotations.py (LineAnnotation, BoxAnnotation,
LabelAnnotation), skipped so the suite stays green. See
docs/feature_parity_roadmap.md section 5.
"""

import pytest

pytestmark = pytest.mark.skip(reason="feature-parity roadmap, not yet implemented")


def test_line_annotation_renders_segment():
    """A LineAnnotation draws a segment between reprojected data coordinates."""
    raise NotImplementedError


def test_box_annotation_renders_rect():
    """A BoxAnnotation draws a shaded rect over the reprojected data range."""
    raise NotImplementedError


def test_label_annotation_renders_text():
    """A LabelAnnotation renders text at the reprojected point."""
    raise NotImplementedError


def test_existing_h_lines_still_work():
    """Legacy h_lines/v_lines keep producing the same dashed reference lines."""
    raise NotImplementedError


def test_annotations_clipped_to_plot():
    """Annotations render inside the plot-area group, not over the axes."""
    raise NotImplementedError
