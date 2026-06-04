"""PolarAreaChart unit tests.

Polar area charts are pie charts where every slice spans an equal angle
and the slice radius encodes the value.
"""

import math
import re

import pytest

from charted.charts.polar_area import PolarAreaChart


def _arc_radii(html: str) -> list[float]:
    """Extract the arc radius from each slice path 'A r r ...' command."""
    radii = []
    for m in re.finditer(r"A ([0-9.]+) [0-9.]+ 0 [01] 1", html):
        radii.append(float(m.group(1)))
    return radii


class TestPolarAreaHappyPath:
    def test_polar_area_equal_angles(self):
        """N values -> N slices, each spanning 360/N degrees."""
        values = [10, 20, 30, 40]
        chart = PolarAreaChart(data=values)
        angles = chart.slice_angles()
        assert len(angles) == len(values)
        expected = 360 / len(values)
        for start, end in angles:
            assert math.isclose(end - start, expected, abs_tol=1e-6)

    def test_polar_area_radius_encodes_value(self):
        """Slice radius is monotonic in value; largest value -> outermost."""
        values = [5, 1, 9, 3]
        chart = PolarAreaChart(data=values)
        radii = chart.slice_radii()
        assert len(radii) == len(values)

        by_value = sorted(zip(values, radii), key=lambda p: p[0])
        sorted_radii = [r for _, r in by_value]
        assert sorted_radii == sorted(sorted_radii)

        max_idx = values.index(max(values))
        assert radii[max_idx] == max(radii)

    def test_polar_area_renders_paths(self):
        """Chart renders slice paths."""
        chart = PolarAreaChart(data=[10, 20, 30], labels=["A", "B", "C"])
        html = chart.html
        assert "<path" in html.lower()
        assert "svg" in html.lower()

    def test_polar_area_single_slice_renders_full_circle(self):
        """N == 1 spans the whole circle (0..360); the slice must render as a
        full circle, not the zero-area sliver that ``_get_slice_path`` produces
        when ``angle_span % 360 == 0``.
        """
        chart = PolarAreaChart(data=[42])
        # Radial scale rings render first; grab the first slice path element.
        path_d = next(
            child.kwargs["d"]
            for child in chart.representation.children
            if "d" in child.kwargs
        )

        # A full circle path is two semicircle arcs with the large-arc/sweep
        # flags '1 1', as emitted by _get_full_circle_path. The degenerate
        # slice path instead starts with a move-to-center then a line ("M cx
        # cy L ...") and has no usable area.
        assert path_d.count(" 1 1 ") == 2
        assert " L " not in path_d  # not the center-anchored sliver

        # The rendered radius must be the (single) slice radius, not zero.
        radii = _arc_radii(chart.html)
        assert radii
        assert all(r > 0 for r in radii)
        assert math.isclose(radii[0], chart.slice_radii()[0], abs_tol=1e-6)


class TestPolarAreaSadPath:
    def test_polar_area_negative_value_raises(self):
        """Negative values are rejected."""
        with pytest.raises(ValueError):
            PolarAreaChart(data=[10, -5, 20])

    def test_polar_area_empty_raises(self):
        """Empty data is rejected."""
        with pytest.raises(ValueError):
            PolarAreaChart(data=[])


class TestPolarAreaConfig:
    def test_config_round_trip(self):
        """to_config()/from_config() preserves data and labels."""
        chart = PolarAreaChart(data=[10, 20, 30], labels=["A", "B", "C"], title="Polar")
        cfg = chart.to_config()
        assert cfg["chart_type"] == "PolarAreaChart"

        from charted.charts.chart import Chart

        rebuilt = Chart.from_config(cfg)
        assert isinstance(rebuilt, PolarAreaChart)
        assert rebuilt._pie_data == [10, 20, 30]


class TestPolarAreaRadialGrid:
    """Radial scale rings and numeric ring labels (issue #62)."""

    def test_radial_rings_rendered(self):
        """Concentric rings are drawn behind the slices, one per nice tick."""
        chart = PolarAreaChart(data=[10, 20, 30, 15], radial_levels=5)
        html = chart.html
        # Each ring is a <circle ... fill="none" ...>; count those.
        ring_count = html.count('fill="none"')
        # Ring values snap to round numbers, so the count is the nice-tick count.
        assert ring_count == len(chart._radial_scale()[1])

    def test_radial_labels_present_by_default(self):
        """Ring labels are round numbers, with the outer ring at the nice max."""
        chart = PolarAreaChart(data=[10, 20, 30, 15], radial_levels=5)
        html = chart.html
        # data max 30 snaps to ticks 5, 10, 15, 20, 25, 30.
        assert ">30<" in html  # nice max at the outer ring
        assert ">5<" in html  # round inner tick (not 30 * 1/5 == 6)

    def test_radial_labels_can_be_disabled(self):
        """show_radial_labels=False keeps rings but drops their labels."""
        chart = PolarAreaChart(
            data=[10, 20, 30, 15], radial_levels=5, show_radial_labels=False
        )
        html = chart.html
        assert html.count('fill="none"') == len(chart._radial_scale()[1])
        assert ">30<" not in html

    def test_rings_use_theme_grid_color(self):
        """Rings adopt the theme's resolved grid colour (dark preset)."""
        from charted.themes.core import Theme

        theme = Theme.from_preset("dark")
        chart = PolarAreaChart(data=[10, 20, 30], theme=theme)
        html = chart.html
        assert theme.resolved_grid_color.lower() in html.lower()
