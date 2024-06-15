from charted.charts.chart import Chart
from charted.html.element import G, Path
from charted.utils.transform import rotate, scale, translate
from charted.utils.types import Labels, Vector, Vector2D


class ColumnChart(Chart):
    y_stacked: bool = True

    def __init__(
        self,
        data: Vector | Vector2D,
        labels: Labels = None,
        column_gap: float = 0.50,
        width: float = 500,
        height: float = 500,
        h_padding: float = 0.1,
        v_padding: float = 0.1,
        zero_index: bool = True,
        title: str | None = None,
        colors: list[str] | None = None,
    ):
        self.column_gap = column_gap
        super().__init__(
            width=width,
            height=height,
            h_padding=h_padding,
            v_padding=v_padding,
            y_data=data,
            x_labels=labels,
            title=title,
            colors=colors,
            zero_index=zero_index,
        )

    @property
    def x_width(self) -> float:
        return self.plot_width / (self.x_count + (self.x_count + 1) * self.column_gap)

    @property
    def representation(self) -> G:
        dy = 0
        if self.y_axis.axis_dimension.min_value < 0:
            dy = self.y_axis.reproject(abs(self.y_axis.axis_dimension.min_value))

        g = G(
            opacity="0.8",
            transform=[
                translate(-self.h_pad, -self.bottom_padding),
                rotate(180, self.width / 2, self.height / 2),
                scale(-1, 1),
                translate(-self.plot_width, self.y_axis.zero),
                translate(-self.x_width / 2, dy),
            ],
        )
        for y_values, y_offsets, x_values, color in zip(
            self.y_values,
            self.y_offsets,
            self.x_values,
            self.colors,
        ):
            x_offset = 0
            if self.x_labels:
                x_offset += self.x_axis.reproject(1)
            paths = []
            for x, y, y_offset in zip(x_values, y_values, y_offsets):
                x += x_offset
                paths.append(Path.get_path(x, y_offset, self.x_width, y))
            g.add_child(Path(d=paths, fill=color))

        return g
