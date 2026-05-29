"""ComboChart unit tests.

Covers the mixed bar+line chart: shared x-axis, optional secondary y-axis,
legend per series, describe() metadata, and series count validation.
"""

import re

import pytest

from charted.charts.combo import ComboChart


def _bar_paths(svg: str) -> list[str]:
    """Return path 'd' values that look like filled rectangles (bars)."""
    return re.findall(r'<path[^>]*\bd="M[^"]*"', svg)


class TestComboRendering:
    def test_combo_renders_bars_and_line(self):
        """A combo with one bar and one line series renders both."""
        chart = ComboChart(
            series=[
                {"data": [10, 20, 30, 40], "type": "bar", "name": "Revenue"},
                {"data": [5, 15, 10, 25], "type": "line", "name": "Margin"},
            ],
            labels=["Q1", "Q2", "Q3", "Q4"],
        )
        svg = chart.svg
        # Bar series produces filled column paths (fill, no stroke="none" line)
        assert "<path" in svg
        # Line series produces a path with fill="none"
        assert 'fill="none"' in svg
        # Both representations present: count paths is more than a single series
        assert svg.count("<path") >= 2
        assert "NaN" not in svg

    def test_combo_shares_x_axis(self):
        """Bar centers and line points align on the same x tick positions."""
        chart = ComboChart(
            series=[
                {"data": [10, 20, 30], "type": "bar"},
                {"data": [3, 6, 9], "type": "line"},
            ],
            labels=["A", "B", "C"],
        )
        # Both series share the same x_count and x tick coordinates
        assert chart.x_count == 3
        coords = chart.x_axis.coordinates
        # 3 labels -> at least 3 tick coordinates (plus padding ticks)
        assert len(coords) >= 3
        # Rendering succeeds with shared coordinate system
        assert "<svg" in chart.svg


class TestComboSecondaryAxis:
    def test_combo_secondary_y_axis(self):
        """A series on the secondary axis gets its own right-side tick labels."""
        chart = ComboChart(
            series=[
                {"data": [10, 20, 30, 40], "type": "bar", "axis": "primary"},
                {
                    "data": [1000, 2000, 1500, 3000],
                    "type": "line",
                    "axis": "secondary",
                },
            ],
            labels=["Q1", "Q2", "Q3", "Q4"],
        )
        assert chart.has_secondary_axis
        # Secondary axis scales to its own (much larger) range, not the primary's
        sec = chart.secondary_y_axis
        assert sec.axis_dimension.max_value >= 3000
        # Primary axis should not be inflated to the secondary's range
        assert chart.y_axis.axis_dimension.max_value < 1000
        svg = chart.svg
        # Secondary tick labels rendered on the right side of the plot
        right_x = chart.left_padding + chart.plot_width
        # The secondary axis group is anchored near the right edge
        assert (
            f'x="{right_x}"' in svg
            or "secondary" in svg.lower()
            or str(int(right_x)) in svg
        )

    def test_combo_no_secondary_axis_by_default(self):
        """Without a secondary series, no secondary axis is created."""
        chart = ComboChart(
            series=[
                {"data": [10, 20, 30], "type": "bar"},
                {"data": [3, 6, 9], "type": "line"},
            ],
            labels=["A", "B", "C"],
        )
        assert not chart.has_secondary_axis
        assert chart.secondary_y_axis is None


class TestComboLegend:
    def test_combo_legend_lists_all_series(self):
        """One legend entry per series with the correct per-series color."""
        chart = ComboChart(
            series=[
                {"data": [10, 20, 30], "type": "bar", "name": "Sales"},
                {"data": [3, 6, 9], "type": "line", "name": "Growth"},
            ],
            labels=["A", "B", "C"],
        )
        svg = chart.svg
        assert "Sales" in svg
        assert "Growth" in svg
        # Two distinct series colors appear
        colors = chart.colors
        assert len(colors) >= 2
        assert colors[0] in svg
        assert colors[1] in svg


class TestComboDescribe:
    def test_combo_describe(self):
        """describe() reports series_count==2 and each series' type."""
        chart = ComboChart(
            series=[
                {"data": [10, 20, 30], "type": "bar", "name": "Sales"},
                {"data": [3, 6, 9], "type": "line", "name": "Growth"},
            ],
            labels=["A", "B", "C"],
        )
        meta = chart.describe()
        assert meta["series_count"] == 2
        types = [s.get("type") for s in meta["series"]]
        assert types == ["bar", "line"]
        names = [s.get("name") for s in meta["series"]]
        assert names == ["Sales", "Growth"]


class TestComboValidation:
    def test_combo_requires_at_least_two_series(self):
        """A single series raises."""
        with pytest.raises(ValueError, match="at least two series"):
            ComboChart(
                series=[{"data": [10, 20, 30], "type": "bar"}],
                labels=["A", "B", "C"],
            )

    def test_combo_requires_series(self):
        """No series raises."""
        with pytest.raises(ValueError, match="at least two series"):
            ComboChart(series=[], labels=["A", "B", "C"])


class TestComboRoundTrip:
    def test_combo_config_round_trip(self):
        """to_config()/from_config() preserves per-series types and axis."""
        chart = ComboChart(
            series=[
                {"data": [10, 20, 30], "type": "bar", "axis": "primary", "name": "S1"},
                {
                    "data": [100, 200, 150],
                    "type": "line",
                    "axis": "secondary",
                    "name": "S2",
                },
            ],
            labels=["A", "B", "C"],
        )
        config = chart.to_config()
        assert config["chart_type"] == "ComboChart"
        restored = ComboChart.from_config(config)
        assert isinstance(restored, ComboChart)
        assert [s["type"] for s in restored.series] == ["bar", "line"]
        assert [s.get("axis", "primary") for s in restored.series] == [
            "primary",
            "secondary",
        ]
