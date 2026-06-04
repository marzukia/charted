"""Regression tests for issue #58.

Pie, radar, heatmap and polar-area used to ignore the theme palette and
render the default pastel colours regardless of the active preset. These
tests assert each of the four honours ``Theme.from_preset('high-contrast')``
so its resolved colours differ from the default theme.
"""

from charted.charts.heatmap import HeatmapChart
from charted.charts.pie import PieChart
from charted.charts.polar_area import PolarAreaChart
from charted.charts.radar import RadarChart
from charted.themes.core import Theme

HIGH_CONTRAST = Theme.from_preset("high-contrast")


def test_pie_honours_high_contrast_palette():
    data = [25, 35, 40]
    default = PieChart(data=data)
    hc = PieChart(data=data, theme=HIGH_CONTRAST)

    assert hc.colors != default.colors
    # The first slices should match the okabe-ito preset palette.
    assert hc.colors[0] == HIGH_CONTRAST.colors[0]
    assert hc.colors[1] == HIGH_CONTRAST.colors[1]


def test_polar_area_honours_high_contrast_palette():
    data = [10, 20, 30, 15]
    default = PolarAreaChart(data=data)
    hc = PolarAreaChart(data=data, theme=HIGH_CONTRAST)

    assert hc.colors != default.colors
    assert hc.colors[0] == HIGH_CONTRAST.colors[0]


def test_radar_honours_high_contrast_palette():
    data = [[20, 35, 30], [30, 25, 40]]
    labels = ["A", "B", "C"]
    default = RadarChart(data=data, labels=labels)
    hc = RadarChart(data=data, labels=labels, theme=HIGH_CONTRAST)

    assert hc.colors != default.colors
    assert hc.colors[0] == HIGH_CONTRAST.colors[0]
    assert hc.colors[1] == HIGH_CONTRAST.colors[1]


def test_heatmap_honours_high_contrast_palette():
    data = [[1, 2, 3], [4, 5, 6]]
    default = HeatmapChart(data=data)
    hc = HeatmapChart(data=data, theme=HIGH_CONTRAST)

    assert (hc.low_color, hc.high_color) != (default.low_color, default.high_color)
    assert hc.low_color == HIGH_CONTRAST.colors[0]
    assert hc.high_color == HIGH_CONTRAST.colors[1]


def test_default_palettes_unchanged():
    """The default (no-theme) renders must keep their historical colours."""
    assert PieChart(data=[1, 2, 3]).colors[:2] == ["#5fab9e", "#f58b51"]
    assert RadarChart(data=[[1, 2]], labels=["a", "b"]).colors[0] == "#5fab9e"
    hm = HeatmapChart(data=[[1, 2], [3, 4]])
    assert (hm.low_color, hm.high_color) == ("#5fab9e", "#f58b51")


def test_heatmap_explicit_colors_still_honoured():
    """An explicit low/high override must win over the theme palette."""
    hm = HeatmapChart(
        data=[[1, 2], [3, 4]],
        low_color="#111111",
        high_color="#eeeeee",
        theme=HIGH_CONTRAST,
    )
    assert hm.low_color == "#111111"
    assert hm.high_color == "#eeeeee"
