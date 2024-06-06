from typing import Tuple, Union
from charted.charts.plane import Plane
from charted.html.element import G, Path
from charted.utils.column import calculate_axis_coordinates, get_path
from charted.utils.transform import translate
from charted.utils.types import Bounds, Vector


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
        self.add_children(self.grid_lines)

    @property
    def grid_lines(self) -> G:
        paths = []
        for x in self.x_coordinates:
            paths += [f"M{x} 0", f"v{self.height}z"]

        for y in self.y_coordinates:
            paths += [f"M0 {y}", f"h{self.width}z"]

        return Path(
            class_name="plot-grid-y-lines",
            stroke="#ccc",
            d=paths,
        )


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
        y0: float = None,
        x0: float = None,
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
            x0,
            y0,
        )
        self.add_children(self.plot_area, self.grid)

    def _validate_coordinates(
        self,
        x_coordinates: Union[Vector, None],
        y_coordinates: Union[Vector, None],
        no_x: int,
        no_y: int,
        x0: float,
        y0: float,
    ) -> Tuple[Vector, Vector]:
        if not x_coordinates and not no_x:
            raise Exception("Requires x_coordinates or no_x")

        if not y_coordinates and not no_y:
            raise Exception("Requires y_coordinates or no_y")

        if no_x:
            x_coordinates = calculate_axis_coordinates(self.width, no_x, x0)
        elif x_coordinates:
            x_coordinates = x_coordinates

        if no_y:
            y_coordinates = calculate_axis_coordinates(self.height, no_y, y0)
        if y_coordinates:
            y_coordinates = y_coordinates

        return (x_coordinates, y_coordinates)

    @property
    def plane(self) -> Plane:
        return Plane(
            height=self.height,
            width=self.width,
            data=self.data,
        )

    @property
    def plot_area(self) -> Path:
        return Path(
            d=get_path(
                x=self.bounds.x1,
                y=self.bounds.y1,
                width=self.width,
                height=self.height,
            ),
            fill="white",
            stroke="#bbb",
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
            transform=translate(self.bounds.x1, self.bounds.y1),
        )
