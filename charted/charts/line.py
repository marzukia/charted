from typing import List, Tuple
from charted.charts.chart import Chart
from charted.charts.plot import Plot
from charted.html.element import Circle, G, Path
from charted.utils.transform import rotate, translate
from charted.utils.types import Vector, Vector2D


class Line(Chart):
    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if self.labels:
            self.labels = [*self.labels, " "]

        self.add_children(
            self.container,
            self.plot,
            self.zero_line,
            self.axes,
            self.points,
        )
        if self.title_text:
            self.add_child(self.title)

    @classmethod
    def get_bounds(cls, y_data: Vector2D, x_data: Vector2D = []):
        y_agg = [item for sublist in y_data for item in sublist]
        x_agg = [item for sublist in x_data for item in sublist]

        min_y = min(y_agg)
        max_y = max(y_agg)

        if len(x_agg) == 0:
            min_x = 0
            max_x = len(y_data[0]) - 1
        else:
            min_x = min(x_agg)
            max_x = max(x_agg)

        return (
            min_x,
            min_y,
            max_x,
            max_y,
        )

    @property
    def x_count(self) -> int:
        cnt = len(self.data[0])
        if self.x_data:
            return cnt
        return cnt + 1

    @property
    def x_width(self) -> float:
        return self.plot_width / self.x_count

    @property
    def x_ticks(self) -> Vector:
        return [(self.plot_width / self.x_count) * i for i in range(0, self.x_count)]

    @property
    def y_values(self) -> Vector2D:
        data = []
        for arr in self.data:
            row = []
            for y in arr:
                v = self._reproject_y(abs(y))
                if y < 0:
                    v = -v
                row.append(v)
            data.append(row)
        return data

    @property
    def x_values(self) -> Vector2D:
        if not self.x_data:
            return self.x_ticks * self.x_count

        data = []
        for arr in self.x_data:
            row = []
            for x in arr:
                v = self._reproject_x(abs(x))
                if x < 0:
                    v = -v
                row.append(v)
            data.append(row)

        if len(data) != len(self.y_data):
            if not len(data) == 1:
                raise Exception("x_data and y_data do not")

            data *= len(self.y_data)

        return data

    @property
    def coordinates(self) -> List[List[Tuple[float, float]]]:
        return [(x, y) for x, y in zip(self.x_values, self.y_values)]

    @property
    def points(self) -> G:
        dx = self.h_pad
        dy = self.v_pad

        if self.min_y < 0:
            dy += self._reproject_y(abs(self.min_y))

        g = G(
            transform=[
                rotate(180, self.width / 2, self.height / 2),
                translate(x=(dx + self.x_zero), y=dy),
            ],
        )

        for y_values, x_values, color in zip(
            self.y_values,
            self.x_values,
            self.colors,
        ):
            series = G(fill="white", stroke=color, stroke_width=2)
            points = []
            path = []
            for i, (x, y) in enumerate(zip(x_values, reversed(y_values))):
                if i == 0:
                    path.append(f"M{x} {y}")
                else:
                    path.append(f"L{x} {y}")
                c = Circle(cx=x, cy=y, r=4)
                points.append(c)
            line = Path(d=path, fill="none")
            series.add_children(line, *points)
            g.add_children(series)

        return g

    @property
    def zero_line(self) -> G:
        g = G(stroke="black")

        dy = self.v_pad + self.y_zero
        dx = self.h_pad + self.x_zero

        h_line = Path(d=[f"M{self.h_pad} {dy}", f"h{self.plot_width}z"])
        v_line = Path(d=[f"M{dx} {self.v_pad}", f"v{self.plot_height}z"])

        g.add_children(h_line, v_line)

        return g

    @property
    def plot(self) -> Plot:
        count = self.x_count - 1
        kwargs = {
            "no_x": count,
            "no_y": count,
        }

        if not self.x_data:
            kwargs = {
                "no_x": 5,
                "no_y": 5,
            }

        return Plot(
            parent=self,
            bounds=self.calculate_plot_corners(
                self.width,
                self.height,
                self.padding,
            ),
            width=self.plot_width,
            height=self.plot_height,
            padding=self.padding,
            **kwargs,
        )
