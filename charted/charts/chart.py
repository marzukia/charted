from charted.charts.plot import Plot
from charted.html.element import Svg
from charted.html.formatter import format_html
from charted.utils.plot import calculate_plot_corners
from charted.utils.svg import calculate_viewbox


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
            viewBox=calculate_viewbox(width, height),
            **kwargs,
        )
        self.width = width
        self.height = height
        self.padding = padding

    @property
    def plot(self) -> Plot:
        return Plot(
            bounds=calculate_plot_corners(self.width, self.height, self.padding),
            width=self.width,
            height=self.height,
            padding=self.padding,
        )

    def __repr__(self):
        return format_html(self.html)
