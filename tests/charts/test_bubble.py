"""BubbleChart unit tests.

Bubble charts are scatter plots where each marker's radius encodes a
third numeric value.
"""

import re

import pytest

from charted.charts.bubble import BubbleChart
from charted.charts.scatter import ScatterChart


def _circle_radii(html: str) -> list[float]:
    """Pull every circle radius out of rendered SVG, in document order."""
    return [float(r) for r in re.findall(r'<circle[^>]*\br="([0-9.]+)"', html)]


def _circle_centers(html: str) -> list[tuple[float, float]]:
    """Pull every circle (cx, cy) out of rendered SVG, in document order."""
    centers = []
    for m in re.finditer(r"<circle[^>]*>", html):
        tag = m.group(0)
        cx = re.search(r'\bcx="([\-0-9.]+)"', tag)
        cy = re.search(r'\bcy="([\-0-9.]+)"', tag)
        if cx and cy:
            centers.append((float(cx.group(1)), float(cy.group(1))))
    return centers


class TestBubbleChartHappyPath:
    def test_bubble_radius_encodes_third_dim(self):
        """Marker radius is monotonic in size; largest size -> largest radius."""
        sizes = [1, 5, 3, 9, 2]
        chart = BubbleChart(
            x_data=[0, 1, 2, 3, 4],
            y_data=[10, 20, 30, 40, 50],
            sizes=sizes,
        )
        radii = _circle_radii(chart.html)
        assert len(radii) == len(sizes)

        # Radius must be a monotonic non-decreasing function of size: sorting
        # points by size must sort them by radius too.
        by_size = sorted(zip(sizes, radii), key=lambda p: p[0])
        sorted_radii = [r for _, r in by_size]
        assert sorted_radii == sorted(sorted_radii)

        # Largest size yields the strictly largest radius.
        max_size_idx = sizes.index(max(sizes))
        assert radii[max_size_idx] == max(radii)

    def test_bubble_radius_within_bounds(self):
        """All marker radii sit inside the configured [min_radius, max_radius]."""
        chart = BubbleChart(
            x_data=[0, 1, 2, 3],
            y_data=[5, 6, 7, 8],
            sizes=[2, 8, 14, 20],
            min_radius=6,
            max_radius=30,
        )
        radii = _circle_radii(chart.html)
        assert radii
        assert all(6 <= r <= 30 for r in radii)

    def test_bubble_reuses_scatter_positioning(self):
        """Point centers match a ScatterChart built with the same x/y."""
        x = [0, 1, 2, 3]
        y = [10, 25, 5, 40]
        bubble = BubbleChart(x_data=x, y_data=y, sizes=[1, 2, 3, 4])
        scatter = ScatterChart(x_data=x, y_data=y)

        bubble_centers = _circle_centers(bubble.html)
        scatter_centers = _circle_centers(scatter.html)
        assert bubble_centers == scatter_centers

    def test_bubble_equal_sizes_use_midpoint(self):
        """When every size is equal, radii equal the radius-range midpoint."""
        min_radius, max_radius = 4, 20
        chart = BubbleChart(
            x_data=[0, 1, 2],
            y_data=[1, 2, 3],
            sizes=[5, 5, 5],
            min_radius=min_radius,
            max_radius=max_radius,
        )
        radii = _circle_radii(chart.html)
        assert len(radii) == 3
        assert len(set(radii)) == 1
        expected_midpoint = (min_radius + max_radius) / 2
        assert all(r == pytest.approx(expected_midpoint) for r in radii)


class TestBubbleChartSadPath:
    def test_bubble_negative_size_raises(self):
        """Negative sizes are rejected."""
        with pytest.raises(ValueError):
            BubbleChart(x_data=[0, 1, 2], y_data=[1, 2, 3], sizes=[1, -2, 3])

    def test_bubble_size_length_mismatch_raises(self):
        """sizes must match the number of points."""
        with pytest.raises(ValueError):
            BubbleChart(x_data=[0, 1, 2], y_data=[1, 2, 3], sizes=[1, 2])

    def test_bubble_multi_series_size_mismatch_raises(self):
        """sizes is validated against every series, not just the first."""
        # First series matches sizes (len 3); second series is shorter (len 2).
        with pytest.raises(ValueError, match="series 1"):
            BubbleChart(
                x_data=[[0, 1, 2], [0, 1]],
                y_data=[[1, 2, 3], [4, 5]],
                sizes=[1, 2, 3],
            )

    def test_bubble_multi_series_matching_sizes_ok(self):
        """sizes apply per point index across all series when lengths match."""
        chart = BubbleChart(
            x_data=[[0, 1, 2], [0, 1, 2]],
            y_data=[[1, 2, 3], [4, 5, 6]],
            sizes=[1, 5, 3],
        )
        radii = _circle_radii(chart.html)
        # Two series of three points each: six circles total.
        assert len(radii) == 6
        # sizes[i] drives point i in every series, so the per-index radius
        # repeats across series.
        assert radii[:3] == radii[3:]


class TestBubbleChartAuto:
    def test_auto_with_sizes_creates_bubble(self):
        """auto() routes to BubbleChart when a sizes third dimension is given."""
        from charted import auto

        chart = auto([[0, 1, 2], [10, 20, 30]], sizes=[1, 5, 3])
        assert isinstance(chart, BubbleChart)


class TestBubbleChartConfig:
    def test_config_round_trip(self):
        """to_config()/from_config() preserves sizes and radius bounds."""
        chart = BubbleChart(
            x_data=[0, 1, 2],
            y_data=[3, 4, 5],
            sizes=[1, 2, 3],
            min_radius=5,
            max_radius=25,
            title="Bubbles",
        )
        cfg = chart.to_config()
        assert cfg["chart_type"] == "BubbleChart"
        assert cfg["sizes"] == [1, 2, 3]
        assert cfg["min_radius"] == 5
        assert cfg["max_radius"] == 25

        from charted.charts.chart import Chart

        rebuilt = Chart.from_config(cfg)
        assert isinstance(rebuilt, BubbleChart)
        assert rebuilt.sizes == [1, 2, 3]
        assert rebuilt.min_radius == 5
        assert rebuilt.max_radius == 25


class TestBubbleSizeLegendAndHue:
    """Issue #66: size-scale legend and optional hue dimension."""

    def test_size_legend_off_by_default(self):
        html = BubbleChart(x_data=[1, 2, 3], y_data=[1, 2, 3], sizes=[5, 10, 20]).html
        assert "size_legend" not in html

    def test_size_legend_renders_title_and_reference_bubbles(self):
        html = BubbleChart(
            x_data=[1, 2, 3],
            y_data=[1, 2, 3],
            sizes=[5, 12, 40],
            size_legend=True,
            size_legend_title="Population",
        ).html
        assert "Population" in html
        # the max size value should appear as a reference label in the legend
        assert "40" in html

    def test_hue_adds_gradient_and_varies_fill(self):
        html = BubbleChart(
            x_data=[1, 2, 3],
            y_data=[1, 2, 3],
            sizes=[5, 12, 40],
            size_legend=True,
            hue=[0, 5, 10],
            hue_title="Year",
        ).html
        assert "Year" in html
        fills = set(re.findall(r'<circle[^>]*\bfill="([^"]+)"', html))
        # hue interpolation should produce more than one distinct fill colour
        assert len(fills) > 1

    def test_invalid_size_legend_value_raises(self):
        with pytest.raises(ValueError):
            BubbleChart(
                x_data=[1, 2], y_data=[1, 2], sizes=[5, 10], size_legend="left"
            )
