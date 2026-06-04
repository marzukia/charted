"""Tests for gridline major/minor hierarchy and weight control."""

from charted.charts.line import LineChart
from charted.themes.core import Theme


def _grid_html(theme):
    chart = LineChart(data=[[1, 2, 3, 4, 5]], theme=theme)
    return chart.y_axis.grid_lines


def test_default_theme_renders_single_weight_grid():
    """With no hierarchy fields set, the grid is a single Path as before."""
    grid = _grid_html(Theme())
    assert grid.tag == "path"
    html = grid.html
    # No explicit stroke-width: the SVG default of 1 is kept.
    assert "stroke-width" not in html
    assert "<g>" not in html


def test_grid_width_sets_major_stroke_width():
    grid = _grid_html(Theme(grid_width=2.0))
    assert grid.tag == "path"
    assert 'stroke-width="2.0"' in grid.html


def test_minor_divisions_emit_grouped_two_tier_grid():
    """Minor divisions produce a group: lighter minor lines under major lines."""
    grid = _grid_html(Theme(grid_width=1.0, minor_grid_divisions=4))
    assert grid.tag == "g"
    assert len(grid.children) == 2
    minor_path, major_path = grid.children
    # Minor lines render first (underneath) at half the major width by default.
    assert 'stroke-width="0.5"' in minor_path.html
    assert 'stroke-width="1.0"' in major_path.html
    # Minor grid has strictly more lines than the major grid.
    assert major_path.html.count("h") < minor_path.html.count("h")


def test_minor_grid_color_and_width_overrides():
    theme = Theme(
        grid_width=1.0,
        minor_grid_divisions=2,
        minor_grid_color="#abcdef",
        minor_grid_width=0.3,
    )
    grid = _grid_html(theme)
    minor_path = grid.children[0]
    assert 'stroke="#abcdef"' in minor_path.html
    assert 'stroke-width="0.3"' in minor_path.html


def test_resolved_minor_grid_defaults():
    """Minor width defaults to half the major; minor color derives a light tier."""
    theme = Theme(grid_width=4.0, minor_grid_divisions=2)
    assert theme.resolved_minor_grid_width == 2.0
    # With no major width set, half of the SVG default (1) is used.
    assert Theme(minor_grid_divisions=2).resolved_minor_grid_width == 0.5
    # Derived minor color differs from (is lighter than) the major grid color.
    assert theme.resolved_minor_grid_color != theme.resolved_grid_color


def test_one_division_draws_no_minor_lines():
    """A single division means no minor lines fall between majors."""
    grid = _grid_html(Theme(minor_grid_divisions=1))
    # divisions <= 1 yields no minor coords, so it stays a single Path.
    assert grid.tag == "path"
