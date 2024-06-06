from charted.charts.plot import Plot
from charted.html.element import Svg
from charted.html.formatter import format_html
from charted.utils.types import Bounds


class Chart(Svg):
    def __init__(
        self,
        width: float,
        height: float,
        padding: float,
        **kwargs,
    ):
        super().__init__(
            width=width,
            height=height,
            viewBox=self.calculate_viewbox(width, height),
            **kwargs,
        )
        self.width = width
        self.height = height
        self.padding = padding

    @classmethod
    def calculate_plot_corners(
        cls,
        width: float,
        height: float,
        padding: float = 0,
    ) -> Bounds:
        x_padding = width * padding
        y_padding = height * padding
        x1 = 0 + x_padding
        x2 = width - x_padding
        y1 = 0 + y_padding
        y2 = height - y_padding
        return Bounds(x1, x2, y1, y2)

    @property
    def plot(self) -> Plot:
        return Plot(
            parent=self,
            bounds=self.calculate_plot_corners(
                self.width,
                self.height,
                self.padding,
            ),
            width=self.width,
            height=self.height,
            padding=self.padding,
        )

    def __repr__(self):
        return format_html(self.html)
