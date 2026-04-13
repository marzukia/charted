from charted.charts.chart import Chart
from charted.html.element import G, Circle, Path
from charted.utils.themes import Theme
from charted.utils.types import Labels, Vector, Vector2D


class LineChart(Chart):
    def __init__(
        self,
        data: Vector | Vector2D,
        x_data: Vector | Vector2D | None = None,
        labels: Labels | None = None,
        width: float = 500,
        height: float = 500,
        zero_index: bool = True,
        title: str | None = None,
        theme: Theme | None = None,
        series_names: list[str] | None = None,
    ):
        super().__init__(
            y_data=data,
            x_data=x_data,
            x_labels=labels,
            width=width,
            height=height,
            title=title,
            zero_index=zero_index,
            theme=theme,
            series_names=series_names,
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
            transform=[*self.get_base_transform()],
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

            for i, (x, y, y_offset) in enumerate(zip(x_values, y_values, y_offsets)):
                x += self.x_offset
                y = self._apply_stacking(y, y_offset)
                if i == 0:
                    path.append(f"M{x} {y}")
                else:
                    path.append(f"L{x} {y}")

                marker_size = self.theme["marker"]["marker_size"]
                if marker_size:
                    c = Circle(cx=x, cy=y, r=marker_size)
                    points.append(c)
            line = Path(d=path, fill="none")
            series.add_children(line, *points)
            g.add_children(series)

        return g
