"""Anchor tests for the mixed bar+line chart (feature-parity roadmap, feature 2).

Placeholders for charted/charts/combo.py (ComboChart), skipped so the suite
stays green. See docs/feature_parity_roadmap.md section 2.
"""

import pytest

pytestmark = pytest.mark.skip(reason="feature-parity roadmap, not yet implemented")


def test_combo_renders_bars_and_line():
    """One bar series and one line series both render in the same SVG."""
    raise NotImplementedError


def test_combo_shares_x_axis():
    """Bar centers and line points align on the same x tick positions."""
    raise NotImplementedError


def test_combo_secondary_y_axis():
    """A secondary-axis series scales to its own range with right-side labels."""
    raise NotImplementedError


def test_combo_legend_lists_all_series():
    """Legend has one correctly colored entry per series."""
    raise NotImplementedError


def test_combo_requires_at_least_two_series():
    """A single-series combo raises."""
    raise NotImplementedError
