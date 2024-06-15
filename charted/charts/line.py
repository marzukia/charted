from charted.charts.chart import Chart
from charted.html.element import G, Circle, Path
from charted.utils.transform import rotate, scale, translate
from charted.utils.types import Labels, Vector, Vector2D


class LineChart(Chart):
    def __init__(
        self,
        data: Vector | Vector2D,
        x_data: Vector | Vector2D | None = None,
        labels: Labels | None = None,
        width: float = 500,
        height: float = 500,
        h_padding: float = 0.1,
        v_padding: float = 0.1,
        zero_index: bool = True,
        title: str | None = None,
        colors: list[str] | None = None,
    ):
        super().__init__(
            y_data=data,
            x_data=x_data,
            x_labels=labels,
            width=width,
            height=height,
            h_padding=h_padding,
            v_padding=v_padding,
            title=title,
            colors=colors,
            zero_index=zero_index,
        )

    def validate_x_data(self, data: Vector | Vector2D | None) -> Vector2D:
        validated_data = super().validate_x_data(data)
        if validated_data:
            if len(validated_data) != 1:
                raise Exception("x_data cannot be 2D for LineChart instance.")
        return validated_data

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
            series = G(fill="white", stroke=color, stroke_width=2)
            points = []
            path = []
            x_offset = 0

            if self.x_labels:
                x_offset += self.x_axis.reproject(1)

            for i, (x, y, y_offset) in enumerate(zip(x_values, y_values, y_offsets)):
                x += x_offset
                if self.y_stacked:
                    y += y_offset
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
