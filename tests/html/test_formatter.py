from charted.html.element import G, Path, Svg, Title
from charted.html.formatter import format_html, indent_line


def test_title_element_renders_text():
    title = Title("Feb: 59")
    assert title.html == "<title>Feb: 59</title>"


def test_title_element_nests_inside_mark():
    rect = Path()
    rect.add_child(Title("Sales: 10"))
    assert "<title>Sales: 10</title>" in rect.html


def test_indent_line():
    g = G()
    indented = indent_line(g.html, 1, 2)
    indented_twice = indent_line(g.html, 2, 2)
    assert indented == "  <g/>"
    assert indented_twice == "    <g/>"


def test_format_html():
    svg = Svg().add_child(G().add_child(Path()))
    formatted = format_html(svg.html)
    expected = """\
<svg xmlns="http://www.w3.org/2000/svg">
  <g>
    <path/>
  </g>
</svg>
"""
    assert formatted.strip() == expected.strip()
