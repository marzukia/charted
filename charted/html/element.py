from typing import Any, Dict, List, Union

Children = List["Element"]


class Element(object):
    tag: str
    kwargs: Dict[str, str] = {}
    children: Children = []
    class_name: Union[str, None] = None

    def __init__(self, parent: Any = None, **kwargs):
        self.parent = parent

        _kwargs = {k: v for k, v in kwargs.copy().items() if k != "class_name"}
        class_name = getattr(kwargs, "class_name", None)
        if class_name:
            _kwargs["class"] = class_name

        for key, value in _kwargs.items():
            if type(value) is list:
                _kwargs[key] = " ".join(value)

        self.kwargs: Dict[str, str] = {**self.kwargs, **_kwargs}

        if self.class_name:
            self.kwargs["class"] = self.class_name

        self.children: list = []

    def __new__(cls, *args, **kwargs) -> "Element":
        instance = super().__new__(cls)
        instance.children = []
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
        return "".join(
            child.html if type(child) is not str else child for child in self.children
        )

    def add_child(self, child: "Element") -> "Element":
        """Add a child element to the current element.

        Args:
            child (Element): The child element to add.

        Returns:
            Element: The current element instance after adding the child.
        """
        if child:
            self.children.append(child)
        return self

    def add_children(self, *children: Children) -> "Element":
        """Add multiple child elements to the current element.

        Args:
            children (Children): An iterable containing the child elements to add.

        Returns:
            Element: The current element instance after adding the children.
        """
        for child in children:
            if child:
                self.add_child(child)
        return self

    def __repr__(self) -> str:
        return self.html


class Svg(Element):
    tag = "svg"
    kwargs = {
        "xmlns": "http://www.w3.org/2000/svg",
    }

    @classmethod
    def calculate_viewbox(cls, width: float, height: float) -> str:
        return f"0 0 {width} {height}"


class G(Element):
    tag = "g"


class Circle(Element):
    tag = "circle"


class Path(Element):
    tag = "path"

    @classmethod
    def get_path(cls, x: float, y: float, width: float, height: float) -> List[str]:
        return " ".join(
            [
                f"M{x} {y}",
                f"h{width}",
                f"v{height}",
                f"h{-width}",
                f"v{-1 * height}Z",
            ]
        )


class Text(Element):
    tag = "text"

    def __init__(self, text: str = None, **kwargs):
        super().__init__(**kwargs)
        self.add_child(text)
