"""Tests for the high-contrast theme's heavier defaults and contrast floor (#69)."""

from charted.charts.line import LineChart
from charted.charts.scatter import ScatterChart
from charted.themes.core import Theme
from charted.utils.colors import calculate_contrast_ratio, enforce_contrast_floor


def test_high_contrast_heavier_stroke_and_label_tokens():
    """High-contrast carries thicker strokes and larger/bolder labels."""
    theme = Theme.from_preset("high-contrast")
    assert theme.resolved_series_stroke_width == 3.0
    assert theme.marker_size == 5.0
    assert theme.resolved_reference_line_width == 2.5
    assert theme.resolved_axis_label_font_size == 14
    assert theme.axis_label_font_weight == "bold"
    assert theme.title_font_size == 18


def test_default_themes_keep_historical_defaults():
    """Standard themes are untouched: 2px lines, 12px normal labels, no floor."""
    for name in ("light", "dark"):
        theme = Theme.from_preset(name)
        assert theme.resolved_series_stroke_width == 2
        assert theme.resolved_axis_label_font_size == 12
        assert theme.axis_label_font_weight is None
        assert theme.contrast_floor is None
    base = Theme()
    assert base.resolved_series_stroke_width == 2
    assert base.resolved_colors == base.colors


def test_contrast_floor_darkens_washed_out_palette():
    """Every resolved high-contrast palette colour clears 3:1 on white."""
    theme = Theme.from_preset("high-contrast")
    assert theme.contrast_floor == 3.0
    for original, resolved in zip(theme.colors, theme.resolved_colors):
        ratio = calculate_contrast_ratio(resolved, theme.background_color)
        assert ratio >= 3.0 - 1e-9
    # Yellow #f0e442 fails 3:1 on white and must have actually changed.
    assert "#f0e442" in theme.colors
    assert "#f0e442" not in theme.resolved_colors


def test_enforce_contrast_floor_leaves_passing_colors_alone():
    """A colour already above the floor is returned unchanged."""
    # Pure black on white is 21:1, well above any reasonable floor.
    assert enforce_contrast_floor("#000000", "#ffffff", 3.0) == "#000000"


def test_high_contrast_line_emits_thicker_stroke():
    """A high-contrast line chart serializes a 3px series stroke."""
    chart = LineChart(data=[1, 2, 3], theme=Theme.from_preset("high-contrast"))
    assert 'stroke-width="3.0"' in chart.html


def test_high_contrast_scatter_enlarges_markers():
    """Scatter picks up the theme's explicit marker size in high-contrast."""
    chart = ScatterChart(
        x_data=[1, 2, 3],
        y_data=[1, 2, 3],
        theme=Theme.from_preset("high-contrast"),
    )
    # Default scatter markers are r=4; high-contrast bumps to 5.
    assert 'r="5"' in chart.html or 'r="5.0"' in chart.html
