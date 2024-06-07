from charted.html.element import G, Element, Path, Svg, Text


class TestElement:
    def setup_method(self, method):
        class ElementTestClass(Element):
            tag = "test"

        self.cls = ElementTestClass
        self.tag = self.cls.tag

    def test_html(self):
        element = self.cls(a="foo", b="bar")
        expected = f'<{self.tag} a="foo" b="bar"/>'
        assert element.html == expected

    def test_array_kwargs(self):
        element = self.cls(a=["foo", "bar"])
        expected = f'<{self.tag} a="foo bar"/>'
        assert element.html == expected

    def test_case_handling(self):
        element = self.cls(foo_bar="foo")
        expected = f'<{self.tag} foo-bar="foo"/>'
        assert element.html == expected

    def test_class_override(self):
        element = self.cls(a="foo", b="bar", **{"class": "foobar"})
        expected = f'<{self.tag} a="foo" b="bar" class="foobar"/>'
        assert element.html == expected

    def test_parent_reference(self):
        parent = self.cls(id="parent")
        child = self.cls(id="child", parent=parent)
        assert child.parent.html == f'<{self.tag} id="parent"/>'

    def test_add_child(self):
        parent = self.cls(id="parent")
        child = self.cls(id="child", parent=parent)
        expected = f'<{self.tag} id="parent"><{self.tag} id="child"/></{self.tag}>'
        parent.add_child(child)
        assert parent.html == expected

    def test_add_children(self):
        parent = self.cls(id="parent")
        child1 = self.cls(id="child1", parent=parent)
        child2 = self.cls(id="child2", parent=parent)
        parent.add_children(child1, child2)
        expected = f'<{self.tag} id="parent"><{self.tag} id="child1"/><{self.tag} id="child2"/></{self.tag}>'
        assert parent.html == expected


class TestSvg:
    def setup_method(self, method):
        self.cls = Svg
        self.tag = self.cls.tag

    def test_html(self):
        instance = self.cls()
        assert instance.html == f'<{self.tag} xmlns="http://www.w3.org/2000/svg"/>'


class TestG(TestElement):
    def setup_method(self, method):
        self.cls = G
        self.tag = self.cls.tag


class TestPath(TestElement):
    def setup_method(self, method):
        self.cls = Path
        self.tag = self.cls.tag


class TestText:
    def setup_method(self, method):
        self.cls = Text
        self.tag = self.cls.tag

    def test_text(self):
        instance = self.cls(text="foobar")
        assert instance.html == f"<{self.tag}>foobar</{self.tag}>"
