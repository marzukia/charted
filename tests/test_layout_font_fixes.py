"""Tests pinning the layout and font fixes (y-tick gutter, star legend,
font-family fallback, font embedding, stacked area)."""

from charted import AreaChart, ColumnChart
from charted.html.element import G


class TestYTickGutter:
    def test_left_padding_reserves_for_wide_numeric_ticks(self):
        narrow = ColumnChart([[1, 2, 3]], labels=["a", "b", "c"])
        wide = ColumnChart([[100000, 200000, 150000]], labels=["a", "b", "c"])
        # Wide numeric ticks ("200,000") force a larger gutter so they do not
        # clip off the left edge.
        assert wide.left_padding > narrow.left_padding

    def test_numeric_tick_labels_feed_the_layout(self):
        c = ColumnChart([[120000, 200000]], labels=["a", "b"])
        assert len(c.layout.y_labels) > 0
        assert max(lab.width for lab in c.layout.y_labels) > c.h_pad


class TestFontFamilyFallback:
    def test_sans_serif_fallback_added(self):
        svg = ColumnChart([[1, 2, 3]], labels=["a", "b", "c"]).to_svg()
        assert 'font-family="DejaVu Sans, sans-serif"' in svg

    def test_monospace_fonts_fall_back_to_monospace(self):
        # Monospace families get a monospace fallback, sans families sans-serif.
        assert 'font-family="JetBrains Mono, monospace"' in G(
            font_family="JetBrains Mono"
        ).attributes
        assert 'font-family="Roboto, sans-serif"' in G(font_family="Roboto").attributes


class TestFontEmbedding:
    def test_embed_fonts_inlines_font_face(self):
        chart = ColumnChart([[1, 2, 3]], labels=["a", "b", "c"])
        embedded = chart.to_svg(embed_fonts=True)
        plain = chart.to_svg()
        assert "@font-face" in embedded
        assert "base64," in embedded
        assert "@font-face" not in plain
        assert len(embedded) > len(plain)


class TestAreaStacked:
    def test_area_stacks_by_default(self):
        assert AreaChart([[1, 2], [3, 4]]).y_stacked is True

    def test_area_overlap_mode_available(self):
        assert AreaChart([[1, 2], [3, 4]], stacked=False).y_stacked is False

    def test_stacked_area_y_domain_covers_totals(self):
        stacked = AreaChart([[10, 20], [30, 40]], stacked=True)
        overlap = AreaChart([[10, 20], [30, 40]], stacked=False)
        # Stacking lifts the value-axis max toward the per-point totals.
        assert stacked.y_axis.axis_dimension.max_value > overlap.y_axis.axis_dimension.max_value


class TestDarkThemeContrast:
    def test_dark_background_flips_text_light(self):
        from charted import Theme

        t = Theme(background_color="#0d1b2a")
        # root_color (drives tick/grid/axis-title colors) flips light on dark
        assert t.root_color == "#FFFFFF"
        # legend color also adapts so the WCAG contrast check passes (no raise)
        assert t.legend_font_color != "#444444"

    def test_light_background_keeps_black_root(self):
        from charted import Theme

        assert Theme().root_color == "#000000"

    def test_explicit_root_color_respected_on_dark(self):
        from charted import Theme

        t = Theme(background_color="#0d1b2a", root_color="#ff0000")
        assert t.root_color == "#ff0000"


class TestYAxisTitlePlacement:
    def test_y_title_hugs_axis_not_canvas_edge(self):
        import re

        from charted import LineChart

        c = LineChart(
            [[42, 30, 13]],
            labels=["a", "b", "c"],
            y_label="Deaths per 1,000 live births",
            width=900,
        )
        m = re.search(r'<text[^>]*x="([-0-9.]+)"[^>]*rotate\(-90', c.to_svg())
        assert m is not None
        # The title now tucks beside the tick labels instead of the old fixed
        # canvas-edge position (x == font_size ~= 14).
        assert float(m.group(1)) > 20
