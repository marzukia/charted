"""SVG Element: Defs wrapper for definitions."""

from .element import Element


class Defs(Element):
    tag = "defs"


class ClipPath(Element):
    tag = "clipPath"
