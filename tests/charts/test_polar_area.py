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
