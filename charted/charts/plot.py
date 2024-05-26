from typing import Tuple, Union
from charted.html.element import G, Line, Rect
from charted.utils import (
    Bounds,
    Vector,
    calculate_axis_coordinates,
    svg_translate,
)


class PlotGrid(G):
    class_name: str = "plot-grid"

    def __init__(
        self,
        width: float,
        height: float,
        x_coordinates: Vector = None,
        y_coordinates: Vector = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        self.x_coordinates = x_coordinates
        self.y_coordinates = y_coordinates
        self.add_children(self.x_grid_lines, self.y_grid_lines)

    @property
    def x_grid_lines(self) -> G:
        g = G(class_name="plot-grid-x-lines", stroke="#ccc")

        if not self.x_coordinates:
            return g

        for x in self.x_coordinates:
            line = Line(x1=x, x2=x, y1=0, y2=self.height)
            g.add_child(line)

        return g

    @property
    def y_grid_lines(self) -> G:
        g = G(class_name="plot-grid-y-lines", stroke="#ccc")

        if not self.y_coordinates:
            return g

        for y in self.y_coordinates:
            line = Line(x1=0, x2=self.width, y1=y, y2=y)
            g.add_child(line)

        return g


class Plot(G):
    class_name: str = "plot"

    def __init__(
        self,
        width: float,
        height: float,
        padding: float,
        bounds: Bounds,
        x_coordinates: Vector = None,
        y_coordinates: Vector = None,
        no_x: int = None,
        no_y: int = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.bounds = bounds
        self.height = height
        self.width = width
        self.padding = padding
        self.x_coordinates, self.y_coordinates = self._validate_coordinates(
            x_coordinates,
            y_coordinates,
            no_x,
            no_y,
        )
        self.add_children(self.plot_area, self.grid)

    def _validate_coordinates(
        self,
        x_coordinates: Union[Vector, None],
        y_coordinates: Union[Vector, None],
        no_x: int,
        no_y: int,
    ) -> Tuple[Vector, Vector]:
        if not x_coordinates and not no_x:
            raise Exception("Requires x_coordinates or no_x")

        if not y_coordinates and not no_y:
            raise Exception("Requires y_coordinates or no_y")

        if no_x:
            x_coordinates = calculate_axis_coordinates(self.width, no_x)
        elif x_coordinates:
            x_coordinates = x_coordinates

        if no_y:
            y_coordinates = calculate_axis_coordinates(self.height, no_y)
        if y_coordinates:
            y_coordinates = y_coordinates

        return (x_coordinates, y_coordinates)

    @property
    def plot_area(self) -> Rect:
        return Rect(
            fill="white",
            stroke="#bbb",
            x=self.bounds.x1,
            y=self.bounds.y1,
            width=self.width,
            height=self.height,
        )

    @property
    def grid(self) -> PlotGrid:
        return PlotGrid(
            width=self.width,
            height=self.height,
            x1=self.bounds.x1,
            y1=self.bounds.y1,
            x_coordinates=self.x_coordinates,
            y_coordinates=self.y_coordinates,
            transform=svg_translate(self.bounds.x1, self.bounds.y1),
        )
