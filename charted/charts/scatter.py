from charted.charts.chart import Chart
from charted.html.element import G, Circle
from charted.utils.themes import Theme
from charted.utils.transform import rotate, scale, translate
from charted.utils.types import Vector, Vector2D


class ScatterChart(Chart):
    def __init__(
        self,
        x_data: Vector | Vector2D,
        y_data: Vector | Vector2D,
        width: float = 500,
        height: float = 500,
        title: str | None = None,
        theme: Theme | None = None,
    ):
        super().__init__(
            y_data=y_data,
            x_data=x_data,
            width=width,
            height=height,
            title=title,
            theme=theme,
        )

    @property
    def representation(self) -> G:
        g = G(
            opacity=0.8,
            transform=[
                translate(-self.h_pad, -self.bottom_padding),
                rotate(180, self.width / 2, self.height / 2),
                scale(-1, 1),
                translate(-self.plot_width, 0),
            ],
        )
        for y_values, y_offsets, x_values, color in zip(
            self.y_values,
            self.y_offsets,
            self.x_values,
            self.colors,
        ):
            series = G(fill=color)
            x_offset = 0
            if self.x_labels:
                x_offset += self.x_axis.reproject(1)

            for x, y, y_offset in zip(x_values, y_values, y_offsets):
                x += x_offset
                if self.y_stacked:
                    y += y_offset
                series.add_child(Circle(cx=x, cy=y, r=4))
            g.add_children(series)

        return g
