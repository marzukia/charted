from charted.html.element import G, Element, Line, Path, Rect, Svg, Text


class ElementTestClass(Element):
    tag = "test"


def test_element_html():
    element = ElementTestClass(a="foo", b="bar")
    assert element.html == '<test a="foo" b="bar"/>'


def test_element_array_kwargs():
    element = ElementTestClass(a=["foo", "bar"])
    assert element.html == '<test a="foo bar"/>'


def test_element_case_handling():
    element = ElementTestClass(foo_bar="foo")
    assert element.html == '<test foo-bar="foo"/>'


def test_element_class_override():
    element = ElementTestClass(a="foo", b="bar", **{"class": "foobar"})
    assert element.html == '<test a="foo" b="bar" class="foobar"/>'


def test_element_parent_reference():
    parent = ElementTestClass(id="parent")
    child = ElementTestClass(id="child", parent=parent)
    assert child.parent.html == '<test id="parent"/>'


def test_element_add_child():
    parent = ElementTestClass(id="parent")
    child = ElementTestClass(id="child", parent=parent)
    expected = '<test id="parent"><test id="child"/></test>'
    parent.add_child(child)
    assert parent.html == expected


def test_element_add_children():
    parent = ElementTestClass(id="parent")
    child1 = ElementTestClass(id="child1", parent=parent)
    child2 = ElementTestClass(id="child2", parent=parent)
    parent.add_children(child1, child2)
    expected = '<test id="parent"><test id="child1"/><test id="child2"/></test>'
    assert parent.html == expected


def test_svg():
    instance = Svg()
    assert instance.html == '<svg xmlns="http://www.w3.org/2000/svg"/>'


def test_rect():
    instance = Rect(x=0, y=0, height=50, width=50)
    assert instance.html == '<rect x="0" y="0" height="50" width="50"/>'


def test_g():
    instance = G()
    child = Path(d=["M0 0", "H50", "Z"])
    instance.add_child(child)
    assert instance.html == '<g><path d="M0 0 H50 Z"/></g>'


def test_path():
    instance = Path(d=["M0 0", "H50", "Z"])
    assert instance.html == '<path d="M0 0 H50 Z"/>'


def test_line():
    instance = Line(x1=0, x2=1, y1=0, y2=1)
    assert instance.html == '<line x1="0" x2="1" y1="0" y2="1"/>'


def test_text():
    instance = Text(text="foobar")
    assert instance.html == "<text>foobar</text>"
