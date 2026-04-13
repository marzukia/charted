from charted.charts.chart import Chart
from charted.html.element import G, Path
from charted.utils.themes import Theme
from charted.utils.transform import translate
from charted.utils.types import Labels, Vector, Vector2D


class ColumnChart(Chart):
    y_stacked: bool = True

    def __init__(
        self,
        data: Vector | Vector2D | None = None,
        labels: Labels = None,
        column_gap: float = 0.50,
        width: float = 500,
        height: float = 500,
        zero_index: bool = True,
        title: str | None = None,
        theme: Theme | None = None,
        y_labels: Labels = None,
        series_names: list[str] | None = None,
        y_stacked: bool = True,
    ):
        self.column_gap = column_gap
        self.y_stacked = y_stacked
        super().__init__(
            width=width,
            height=height,
            y_data=data,
            x_labels=labels,
            y_labels=y_labels,
            title=title,
            zero_index=zero_index,
            theme=theme,
            series_names=series_names,
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
                *self.base_transform,
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
                paths.append(Path(d=paths, fill=color))

        return g
