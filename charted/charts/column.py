from collections import defaultdict
from charted.charts.chart import Chart
from charted.charts.plot import Plot
from charted.html.element import G, Path
from charted.utils.transform import rotate, translate
from charted.utils.types import Vector, Vector2D


class Column(Chart):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_children(
            self.container,
            self.plot,
            self.series,
            self.zero_line,
            self.axes,
        )
        if self.title_text:
            self.add_child(self.title)

    @classmethod
    def get_bounds(cls, y_data: Vector2D, **kwargs):
        agg = defaultdict(list)
        n = len(y_data[0])
        for i in range(n):
            for arr in y_data:
                agg[i].append(arr[i])

        min_x = 0
        min_y = min([sum([x for x in i if x <= 0]) for i in agg.values()])
        max_x = n - 1
        max_y = max([sum([x for x in i if x >= 0]) for i in agg.values()])

        return (
            min_x,
            min_y,
            max_x,
            max_y,
        )

    @property
    def x_count(self) -> int:
        return len(self.data[0])

    @property
    def x_width(self, spacing: float = 0.5) -> float:
        width = self.plot_width / (self.x_count + (self.x_count + 1) * spacing)
        return width

    @property
    def x_ticks(self) -> Vector:
        return [
            ((self.plot_width / self.x_count) * i) + (self.x_width / 4)
            for i in range(0, self.x_count)
        ]

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
    def y_offset(self) -> Vector2D:
        offsets = []
        negative_offsets = [0] * self.x_count
        positive_offsets = [0] * self.x_count

        for row in self.data:
            row_offsets = []
            for i, y in enumerate(row):
                current_offset = 0
                if y >= 0:
                    current_offset = positive_offsets[i]
                    positive_offsets[i] += y
                elif y < 0:
                    current_offset = negative_offsets[i]
                    negative_offsets[i] -= abs(y)
                row_offsets.append(current_offset)
            offsets.append(row_offsets)

        return [[self._reproject_y(y) for y in arr] for arr in offsets]

    @property
    def series(self) -> G:
        dx = self.h_pad
        dy = self.v_pad

        if self.min_y < 0:
            dy += self._reproject_y(abs(self.min_y))

        g = G(
            transform=[
                rotate(180, self.width / 2, self.height / 2),
                translate(x=dx, y=dy),
            ]
        )
        for y_values, y_offsets, color in zip(
            self.y_values, self.y_offset, self.colors
        ):
            paths = []
            for x, y, offset in zip(
                self.x_ticks,
                reversed(y_values),
                reversed(y_offsets),
            ):
                path = Path.get_path(x, offset, self.x_width, y)
                paths.append(path)
            g.add_child(Path(d=paths, fill=color))

        return g

    @property
    def zero_line(self) -> Path:
        dy = (self.height * self.padding) + self.y_zero
        dx = self.width * self.padding
        return Path(
            d=[f"M{dx} {dy}", f"h{self.plot_width}z"],
            stroke="black",
        )

    @property
    def plot(self) -> Plot:
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
            # TODO: Remove this hardcoded no_y
            no_y=5,
            x_coordinates=[i - (self.x_width / 4) for i in self.x_ticks],
        )
