"""Tests for curve interpolation on LineChart and AreaChart.

Covers the ``curve=`` option that controls how consecutive data points
join: "linear" (default), "step", and a smooth spline ("cardinal"/"basis").
This is a path-generation change only; data is never altered.
"""

import re

import pytest

from charted.charts.area import AreaChart
from charted.charts.line import LineChart
from charted.utils.curves import cardinal_path, linear_path, step_path


def _line_paths(html: str) -> list[str]:
    """Extract every path ``d`` string from rendered SVG."""
    return re.findall(r'<path d="([^"]*)"', html)


def _series_path(chart) -> str:
    """Return the first path (the line/series boundary) from a chart."""
    paths = _line_paths(chart.html)
    assert paths, "expected at least one path in output"
    return paths[0]


def _coords(path_d: str) -> list[tuple[float, float]]:
    """Walk a path ``d`` string and return the position after each command.

    Understands the absolute commands these curves emit: M (move),
    L (line), H (horizontal), V (vertical), C (cubic, endpoint is the data
    point). Tracking the pen position lets step paths (which split a point
    across H and V) report their true anchors.
    """
    tokens = re.findall(r"([MLHVCZ])([^MLHVCZ]*)", path_d, flags=re.IGNORECASE)
    x = y = 0.0
    out: list[tuple[float, float]] = []
    for cmd, raw in tokens:
        nums = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", raw)]
        up = cmd.upper()
        if up == "M" or up == "L":
            x, y = nums[0], nums[1]
        elif up == "H":
            x = nums[0]
        elif up == "V":
            y = nums[0]
        elif up == "C":
            x, y = nums[-2], nums[-1]
        elif up == "Z":
            continue
        out.append((x, y))
    return out


class TestLinearDefault:
    def test_linear_curve_is_default_polyline(self):
        """Default chart uses only L segments (pins current behavior)."""
        chart = LineChart(data=[10, 20, 30, 25], labels=["a", "b", "c", "d"])
        path = _series_path(chart)
        assert "C" not in path  # no cubic beziers
        assert path.count("L") == 3  # 4 points -> 3 line segments
        assert path.startswith("M")

    def test_linear_explicit_matches_default(self):
        """curve='linear' renders identically to the default."""
        default = LineChart(data=[10, 20, 30], labels=["a", "b", "c"])
        explicit = LineChart(data=[10, 20, 30], labels=["a", "b", "c"], curve="linear")
        assert default.html == explicit.html


class TestStepCurve:
    def test_step_curve_emits_horizontal_then_vertical(self):
        """curve='step' produces axis-aligned segments (H/V commands)."""
        chart = LineChart(
            data=[10, 20, 30, 25], labels=["a", "b", "c", "d"], curve="step"
        )
        path = _series_path(chart)
        assert "H" in path
        assert "V" in path
        assert "C" not in path


class TestCardinalCurve:
    @pytest.mark.parametrize("curve", ["cardinal", "basis"])
    def test_cardinal_curve_emits_cubic_beziers(self, curve):
        """Smooth curves contain C cubic Bezier commands."""
        chart = LineChart(
            data=[10, 20, 30, 25], labels=["a", "b", "c", "d"], curve=curve
        )
        path = _series_path(chart)
        assert "C" in path
        assert path.startswith("M")

    @pytest.mark.parametrize("curve", ["cardinal", "basis"])
    def test_cardinal_starts_and_ends_at_data_points(self, curve):
        """Smoothed path begins/ends at the first/last data point."""
        data = [10, 20, 30, 25]
        linear = LineChart(data=data, labels=["a", "b", "c", "d"])
        curved = LineChart(data=data, labels=["a", "b", "c", "d"], curve=curve)
        lin_coords = _coords(_series_path(linear))
        cur_coords = _coords(_series_path(curved))
        assert cur_coords[0] == lin_coords[0]
        assert cur_coords[-1] == lin_coords[-1]


class TestEndpoints:
    @pytest.mark.parametrize("curve", ["linear", "step", "cardinal", "basis"])
    def test_curve_passes_through_endpoints(self, curve):
        """Every curve type anchors its path at the first/last data point.

        Cardinal interpolates its endpoints by definition. The basis
        implementation here is documented to also pin the endpoints
        (rather than the classic B-spline behavior of floating inside the
        convex hull), so markers/labels stay aligned with the line.
        """
        data = [10, 20, 30, 25]
        linear = LineChart(data=data, labels=["a", "b", "c", "d"])
        target = LineChart(data=data, labels=["a", "b", "c", "d"], curve=curve)
        lin_coords = _coords(_series_path(linear))
        tgt_coords = _coords(_series_path(target))
        assert tgt_coords[0] == lin_coords[0]
        assert tgt_coords[-1] == lin_coords[-1]


class TestAreaCurve:
    def test_area_curve_matches_line_curve(self):
        """AreaChart(curve='cardinal') fills under the same smoothed boundary.

        The area and line use different coordinate spaces (the line group is
        flipped by an SVG transform, the area flips manually), so the byte
        strings differ. The shared invariant is the boundary shape: both
        emit one cubic segment per inter-point gap, and the area then closes
        down to a baseline. Compare the cubic structure of the top boundary.
        """
        data = [10, 20, 30, 25]
        line = LineChart(data=data, labels=["a", "b", "c", "d"], curve="cardinal")
        area = AreaChart(data=data, labels=["a", "b", "c", "d"], curve="cardinal")

        line_path = _series_path(line)
        area_path = _series_path(area)

        line_cubics = line_path.count("C")
        area_cubics = area_path.count("C")
        assert line_cubics == len(data) - 1
        # Area's top boundary has the same number of cubic segments as the line.
        assert area_cubics == line_cubics

    def test_area_curve_is_valid_svg(self):
        area = AreaChart(
            data=[10, 20, 30, 25], labels=["a", "b", "c", "d"], curve="cardinal"
        )
        path = _series_path(area)
        assert path.startswith("M")
        assert "C" in path
        assert path.rstrip().lower().endswith("z")  # closed fill


class TestInvalidCurve:
    def test_invalid_curve_raises(self):
        with pytest.raises(ValueError):
            LineChart(data=[10, 20, 30], labels=["a", "b", "c"], curve="wiggle")

    def test_invalid_curve_raises_area(self):
        with pytest.raises(ValueError):
            AreaChart(data=[10, 20, 30], labels=["a", "b", "c"], curve="wiggle")


class TestConfigRoundTrip:
    def test_to_config_round_trips_curve(self):
        chart = LineChart(data=[10, 20, 30], labels=["a", "b", "c"], curve="cardinal")
        cfg = chart.to_config()
        assert cfg["curve"] == "cardinal"
        rebuilt = LineChart.from_config(cfg)
        assert rebuilt.curve == "cardinal"


class TestPureCurveFunctions:
    """Direct tests of the pure path-builder functions."""

    def test_linear_path_only_L(self):
        d = linear_path([(0, 0), (1, 1), (2, 0)])
        assert d.startswith("M0 0")
        assert d.count("L") == 2
        assert "C" not in d

    def test_step_path_axis_aligned(self):
        d = step_path([(0, 0), (2, 4), (4, 4)])
        assert "H" in d
        assert "V" in d

    def test_cardinal_path_cubic(self):
        d = cardinal_path([(0, 0), (1, 2), (2, 1), (3, 3)])
        assert d.startswith("M0 0")
        assert "C" in d

    def test_cardinal_single_point(self):
        d = cardinal_path([(5, 5)])
        assert d.strip() == "M5 5"

    def test_cardinal_two_points_is_a_line(self):
        d = cardinal_path([(0, 0), (4, 4)])
        # With only two points there is nothing to smooth.
        assert d.startswith("M0 0")
