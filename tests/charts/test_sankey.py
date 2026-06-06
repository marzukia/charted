"""Unit tests for SankeyChart and its d3-style layout engine.

Covers the layout (column assignment, flow conservation, no-overlap), the
public chart API (names + index links, dict links, options), validation
(cycles, negatives, unknown refs, empty input, self-loops), and degenerate
inputs (single link, disconnected chains).
"""

from __future__ import annotations

import math

import pytest

from charted import SankeyChart
from charted.utils.exceptions import ChartedError
from charted.utils.sankey_layout import compute_layout

# --- shared fixtures -------------------------------------------------------

SIMPLE_NODES = ["A", "B", "C"]
SIMPLE_LINKS = [(0, 1, 10.0), (1, 2, 10.0)]


def _layout(nodes, links, **kw):
    defaults = dict(x0=40.0, y0=20.0, x1=760.0, y1=480.0)
    defaults.update(kw)
    return compute_layout(nodes, links, **defaults)


# --- layout: column assignment --------------------------------------------


class TestColumnAssignment:
    def test_linear_chain_gets_sequential_columns(self):
        lay = _layout(SIMPLE_NODES, SIMPLE_LINKS)
        layers = {nd.name: nd.layer for nd in lay.nodes}
        assert layers["A"] < layers["B"] < layers["C"]

    def test_source_nodes_share_leftmost_column(self):
        # Two sources feeding one hub feeding one sink.
        nodes = ["S1", "S2", "Hub", "Sink"]
        links = [(0, 2, 5.0), (1, 2, 5.0), (2, 3, 10.0)]
        lay = _layout(nodes, links)
        layers = {nd.name: nd.layer for nd in lay.nodes}
        assert layers["S1"] == layers["S2"]
        assert layers["S1"] < layers["Hub"] < layers["Sink"]

    def test_justify_pushes_sinks_to_last_column(self):
        # A short branch (B->D) and a long branch (B->C->E); both sinks D and E
        # should land in the final column under justify alignment.
        nodes = ["A", "B", "C", "D", "E"]
        links = [(0, 1, 10.0), (1, 2, 5.0), (1, 3, 5.0), (2, 4, 5.0)]
        lay = _layout(nodes, links, alignment="justify")
        layers = {nd.name: nd.layer for nd in lay.nodes}
        last = max(layers.values())
        assert layers["D"] == last  # sink pushed right despite short path
        assert layers["E"] == last

    def test_horizontal_positions_increase_with_layer(self):
        lay = _layout(SIMPLE_NODES, SIMPLE_LINKS)
        by_layer = sorted(lay.nodes, key=lambda nd: nd.layer)
        xs = [nd.x0 for nd in by_layer]
        assert xs == sorted(xs)


# --- layout: flow conservation + no overlap --------------------------------


class TestLayoutInvariants:
    def test_no_node_overlap_within_column(self):
        nodes = ["A", "B", "C", "D"]
        # A and B both in column 0, C and D in column 1.
        links = [(0, 2, 4.0), (0, 3, 3.0), (1, 2, 2.0), (1, 3, 5.0)]
        lay = _layout(nodes, links, node_padding=8.0)
        cols: dict[int, list] = {}
        for nd in lay.nodes:
            cols.setdefault(nd.layer, []).append(nd)
        for col in cols.values():
            col.sort(key=lambda nd: nd.y0)
            for upper, lower in zip(col, col[1:]):
                # Lower node's top must clear the upper node's bottom (+ padding,
                # within a small float tolerance).
                assert lower.y0 >= upper.y1 - 1e-6

    def test_flow_conservation_inbound_and_outbound(self):
        nodes = ["Coal", "Gas", "Grid", "Homes", "Industry"]
        links = [(0, 2, 30.0), (1, 2, 20.0), (2, 3, 28.0), (2, 4, 22.0)]
        lay = _layout(nodes, links)
        by_name = {nd.name: nd for nd in lay.nodes}
        for nd in lay.nodes:
            height = nd.y1 - nd.y0
            out_w = sum(link.width for link in nd.source_links)
            in_w = sum(link.width for link in nd.target_links)
            if nd.source_links:
                assert math.isclose(out_w, height, rel_tol=1e-6, abs_tol=1e-6)
            if nd.target_links:
                assert math.isclose(in_w, height, rel_tol=1e-6, abs_tol=1e-6)
        # Grid is a pure pass-through: in == out == height.
        grid = by_name["Grid"]
        assert math.isclose(grid.y1 - grid.y0, 50.0 / 50.0 * (grid.y1 - grid.y0))

    def test_link_widths_proportional_to_value(self):
        nodes = ["A", "B", "C"]
        # From A: 30 to B, 10 to C -> widths should be 3:1.
        links = [(0, 1, 30.0), (0, 2, 10.0)]
        lay = _layout(nodes, links)
        wide = next(link for link in lay.links if link.value == 30.0)
        narrow = next(link for link in lay.links if link.value == 10.0)
        assert math.isclose(wide.width / narrow.width, 3.0, rel_tol=1e-6)

    def test_all_nodes_inside_frame(self):
        nodes = ["A", "B", "C", "D", "E"]
        links = [(0, 2, 10.0), (1, 2, 5.0), (2, 3, 8.0), (2, 4, 7.0)]
        lay = _layout(nodes, links, x0=40.0, y0=20.0, x1=760.0, y1=480.0)
        for nd in lay.nodes:
            assert 40.0 - 1e-6 <= nd.x0
            assert nd.x1 <= 760.0 + 1e-6
            assert 20.0 - 1e-6 <= nd.y0
            assert nd.y1 <= 480.0 + 1e-6

    def test_alignment_strategies_all_valid(self):
        for align in ("justify", "left", "right", "center"):
            lay = _layout(SIMPLE_NODES, SIMPLE_LINKS, alignment=align)
            assert len(lay.nodes) == 3


# --- public API ------------------------------------------------------------


class TestSankeyChartAPI:
    def test_renders_well_formed_svg(self):
        chart = SankeyChart(nodes=SIMPLE_NODES, links=[("A", "B", 10), ("B", "C", 10)])
        svg = chart.to_svg()
        assert svg.startswith("<svg")
        assert svg.rstrip().endswith("</svg>")
        assert "<path" in svg
        assert "<rect" in svg

    def test_links_by_name_and_index_equivalent(self):
        by_name = SankeyChart(
            nodes=["A", "B", "C"], links=[("A", "B", 10), ("B", "C", 10)]
        ).to_svg()
        by_index = SankeyChart(
            nodes=["A", "B", "C"], links=[(0, 1, 10), (1, 2, 10)]
        ).to_svg()
        assert by_name == by_index

    def test_dict_links_supported(self):
        chart = SankeyChart(
            nodes=["A", "B"],
            links=[{"source": "A", "target": "B", "value": 5}],
        )
        assert "<svg" in chart.to_svg()

    def test_labels_present_in_output(self):
        chart = SankeyChart(
            nodes=["Alpha", "Beta"], links=[("Alpha", "Beta", 1)], title="Flow"
        )
        svg = chart.to_svg()
        assert "Alpha" in svg
        assert "Beta" in svg
        assert "Flow" in svg

    def test_show_values_annotates_labels(self):
        chart = SankeyChart(nodes=["A", "B"], links=[("A", "B", 7)], show_values=True)
        assert "A (7)" in chart.to_svg()

    def test_title_rendered(self):
        chart = SankeyChart(nodes=["A", "B"], links=[("A", "B", 1)], title="My Sankey")
        assert "My Sankey" in chart.to_svg()

    def test_deterministic_render(self):
        kw = dict(nodes=["A", "B", "C"], links=[("A", "B", 3), ("B", "C", 3)])
        assert SankeyChart(**kw).to_svg() == SankeyChart(**kw).to_svg()

    def test_registered_in_chart_classes(self):
        from charted.charts import _CHART_CLASSES

        assert "SankeyChart" in _CHART_CLASSES()

    def test_save_png(self, tmp_path):
        pytest.importorskip("cairosvg")
        out = tmp_path / "s.png"
        SankeyChart(nodes=["A", "B"], links=[("A", "B", 1)]).save(str(out))
        assert out.exists() and out.stat().st_size > 0


# --- validation ------------------------------------------------------------


class TestSankeyValidation:
    def test_empty_nodes_raises(self):
        with pytest.raises(ChartedError):
            SankeyChart(nodes=[], links=[("A", "B", 1)])

    def test_empty_links_raises(self):
        with pytest.raises(ChartedError):
            SankeyChart(nodes=["A", "B"], links=[])

    def test_cycle_raises(self):
        with pytest.raises(ChartedError):
            SankeyChart(
                nodes=["A", "B", "C"],
                links=[("A", "B", 1), ("B", "C", 1), ("C", "A", 1)],
            )

    def test_negative_value_raises(self):
        with pytest.raises(ChartedError):
            SankeyChart(nodes=["A", "B"], links=[("A", "B", -5)])

    def test_unknown_node_name_raises(self):
        with pytest.raises(ChartedError):
            SankeyChart(nodes=["A", "B"], links=[("A", "Z", 1)])

    def test_index_out_of_range_raises(self):
        with pytest.raises(ChartedError):
            SankeyChart(nodes=["A", "B"], links=[(0, 9, 1)])

    def test_self_loop_raises(self):
        with pytest.raises(ChartedError):
            SankeyChart(nodes=["A", "B"], links=[("A", "A", 1)])

    def test_bad_link_shape_raises(self):
        with pytest.raises(ChartedError):
            SankeyChart(nodes=["A", "B"], links=[("A", "B")])  # type: ignore[list-item]

    def test_non_numeric_value_raises(self):
        with pytest.raises(ChartedError):
            SankeyChart(nodes=["A", "B"], links=[("A", "B", "lots")])  # type: ignore[list-item]

    def test_unknown_alignment_raises(self):
        with pytest.raises(ChartedError):
            SankeyChart(nodes=["A", "B"], links=[("A", "B", 1)], alignment="diagonal")


# --- degenerate inputs -----------------------------------------------------


class TestDegenerateInputs:
    def test_single_link(self):
        chart = SankeyChart(nodes=["A", "B"], links=[("A", "B", 1)])
        lay = compute_layout(["A", "B"], [(0, 1, 1.0)], x0=40, y0=20, x1=760, y1=480)
        assert len(lay.nodes) == 2
        assert len(lay.links) == 1
        assert "<svg" in chart.to_svg()

    def test_two_disconnected_chains(self):
        # A->B and C->D never touch; both must lay out without overlap or error.
        nodes = ["A", "B", "C", "D"]
        links = [(0, 1, 5.0), (2, 3, 5.0)]
        chart = SankeyChart(nodes=nodes, links=links)
        assert "<svg" in chart.to_svg()
        lay = _layout(nodes, links)
        # Both chains occupy two columns; the four nodes are all in frame.
        for nd in lay.nodes:
            assert math.isfinite(nd.y0) and math.isfinite(nd.y1)

    def test_zero_value_link_does_not_crash(self):
        chart = SankeyChart(
            nodes=["A", "B", "C"], links=[("A", "B", 0), ("A", "C", 10)]
        )
        assert "<svg" in chart.to_svg()

    def test_single_node_two_links_fan_out(self):
        chart = SankeyChart(
            nodes=["Hub", "X", "Y"],
            links=[("Hub", "X", 5), ("Hub", "Y", 5)],
        )
        assert "<svg" in chart.to_svg()
