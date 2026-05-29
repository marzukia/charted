"""Anchor tests for opt-in SVG <title> tooltips (feature-parity roadmap, feature 6).

Placeholders for the to_html(tooltips=True) path, skipped so the suite stays
green. See docs/feature_parity_roadmap.md section 6.
"""

import pytest

pytestmark = pytest.mark.skip(reason="feature-parity roadmap, not yet implemented")


def test_to_svg_has_no_titles_by_default():
    """Plain to_svg() output contains no <title> elements (file output inert)."""
    raise NotImplementedError


def test_to_html_tooltips_opt_in():
    """to_html(tooltips=True) injects <title> children; default does not."""
    raise NotImplementedError


def test_tooltip_text_matches_data():
    """Tooltip text for a point equals its label and value."""
    raise NotImplementedError


def test_tooltips_no_javascript():
    """The emitted HTML contains no <script> tag (zero-JS guarantee)."""
    raise NotImplementedError
