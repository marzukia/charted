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

    def test_combo_bar_center_equals_line_vertex(self):
        """B1: each bar center x equals the matching line vertex x.

        The line must render against the same column-band centers, not its own
        unpadded i/(n-1)*plot_w positions (which drift off the bars/ticks and
        overflow the plot edge on the last point).
        """
        chart = ComboChart(
            series=[
                {"data": [10, 20, 30], "type": "bar", "name": "Bars"},
                {"data": [3, 6, 9], "type": "line", "name": "Line"},
            ],
            labels=["A", "B", "C"],
        )
        # Band centers the columns are drawn at: x_values + x_offset.
        band_centers = [round(x + chart.x_offset, 1) for x in chart.x_values[0]]

        # Pull the line path vertices out of the rendered SVG.
        svg = chart.svg
        line_d = re.search(r'<path d="(M[^"]*)" fill="none"', svg).group(1)
        verts = [
            round(float(m.split()[0]), 1)
            for m in re.findall(r"[ML]([\d.]+ [\d.]+)", line_d)
        ]
        assert verts == band_centers, (
            f"line vertices {verts} != bar band centers {band_centers}"
        )
        # And the last vertex must sit inside the plot, not at the right edge.
        assert verts[-1] < chart.plot_width

    def test_combo_line_color_matches_legend_swatch(self):
        """B2: the rendered line stroke uses its per-series color, not palette[0].

        A single line in a combo previously always rendered as palette[0] while
        its legend swatch showed the correct per-series color.
        """
        chart = ComboChart(
            series=[
                {"data": [10, 20, 30], "type": "bar", "name": "Bars"},
                {"data": [3, 6, 9], "type": "line", "name": "Line"},
            ],
            labels=["A", "B", "C"],
        )
        colors = chart.colors
        # The line is series index 1, so its color is colors[1], not colors[0].
        line_color = colors[1]
        svg = chart.svg
        # The <g> wrapping the line path carries the stroke color.
        m = re.search(
            r'<g fill="white" stroke="([^"]+)"[^>]*>'
            r'<path d="M[^"]*" fill="none"/>',
            svg,
        )
        assert m, "could not locate the rendered line group"
        assert m.group(1) == line_color, (
            f"line stroke {m.group(1)} != per-series color {line_color} "
            f"(palette[0] is {colors[0]})"
        )


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
        # Secondary axis must live in the normal element tree, so .html and
        # .svg agree (the CLI and visual tests render .html).
        assert chart.html == chart.svg
        svg = chart.svg

        # The actual secondary tick label TEXT is present...
        sec_labels = [lbl.text for lbl in sec.labels if lbl.text]
        assert sec_labels, "secondary axis should expose tick labels"
        for text in sec_labels:
            assert f">{text}<" in svg, f"secondary label {text!r} missing from SVG"

        # ...and the secondary axis group is anchored at x ~= left_padding +
        # plot_width (a small fixed gutter past the right plot edge).
        right_x = chart.left_padding + chart.plot_width
        group_xs = [float(m) for m in re.findall(r"translate\(x?=?([\d.]+)", svg)]
        assert any(abs(x - right_x) <= 12 for x in group_xs), (
            f"no secondary axis group near right edge x={right_x}; "
            f"found translate x positions {group_xs}"
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
