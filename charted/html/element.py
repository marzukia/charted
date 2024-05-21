from typing import Dict, List, Self, Type

Children = List["Element"]


class Element(object):
    tag: str
    kwargs: Dict[str, str] = {}
    children: Children = []

    def __new__(cls: Type["Element"], **kwargs) -> "Element":
        instance = super().__new__(cls)
        instance.kwargs = {**(instance.kwargs or {}), **kwargs}
        instance.children = instance.children or []
        return instance

    @property
    def attributes(self) -> str:
        """Generate the attributes passed in as kwargs as a string.

        Returns:
            str: A string representing HTML attributes in the format "key1="value1" key2="value2" ...".
        """
        string = ""
        if len(self.kwargs) > 0:
            string += " "
            attributes_array = []
            for k, v in self.kwargs.items():
                attributes_array.append(f'{k.replace("_", "-")}="{v}"')
            string += " ".join(attributes_array)
        return string

    @property
    def html(self) -> str:
        """Generate HTML markup for the element.

        Returns:
            str: A string containing the HTML markup for the element.
        """
        if not self.children:
            return f"<{self.tag}{self.attributes}/>"
        return f"<{self.tag}{self.attributes}>{self.children_html}</{self.tag}>"

    @property
    def children_html(self) -> str:
        """Generate HTML for children elements.

        Returns:
            str: A string containing the HTML markup for all child elements.
        """
        return "".join(child.html for child in self.children)

    def add_child(self, child: "Element") -> Self:
        """Add a child element to the current element.

        Args:
            child (Element): The child element to add.

        Returns:
            Element: The current element instance after adding the child.
        """
        self.children.append(child)
        return self

    def add_children(self, children: Children) -> Self:
        """Add multiple child elements to the current element.

        Args:
            children (Children): An iterable containing the child elements to add.

        Returns:
            Element: The current element instance after adding the children.
        """
        for child in children:
            self.add_child(child)
        return self

    def __repr__(self) -> str:
        return self.html


class Svg(Element):
    tag = "svg"
    kwargs = {
        "xmlns": "http://www.w3.org/2000/svg",
    }


class Rect(Element):
    tag = "rect"


class G(Element):
    tag = "g"


class Line(Element):
    tag = "line"
