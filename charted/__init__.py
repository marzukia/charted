# flake8: noqa
from charted.charts.chart import Chart
from charted.charts.column import ColumnChart
from charted.charts.line import LineChart
from charted.charts.scatter import ScatterChart
from charted.utils.themes import Theme
from charted.utils.types import Labels, Vector, Vector2D

__version__ = "0.1.0"
__all__ = [
    "Chart",
    "ColumnChart",
    "LineChart",
    "ScatterChart",
    "column_chart",
    "line_chart",
    "scatter_chart",
    "chart",
]


def column_chart(
    data: Vector | Vector2D,
    labels: Labels | None = None,
    column_gap: float = 0.50,
    width: float = 500,
    height: float = 500,
    zero_index: bool = True,
    title: str | None = None,
    theme: Theme | None = None,
) -> ColumnChart:
    """Create a column chart with the given data and options."""
    return ColumnChart(
        data=data,
        labels=labels,
        column_gap=column_gap,
        width=width,
        height=height,
        zero_index=zero_index,
        title=title,
        theme=theme,
    )


def line_chart(
    data: Vector | Vector2D,
    labels: Labels | None = None,
    width: float = 500,
    height: float = 500,
    zero_index: bool = True,
    title: str | None = None,
    theme: Theme | None = None,
) -> LineChart:
    """Create a line chart with the given data and options."""
    return LineChart(
        data=data,
        labels=labels,
        width=width,
        height=height,
        zero_index=zero_index,
        title=title,
        theme=theme,
    )


def scatter_chart(
    x_data: Vector | Vector2D,
    y_data: Vector | Vector2D,
    labels: Labels | None = None,
    width: float = 500,
    height: float = 500,
    zero_index: bool = True,
    title: str | None = None,
    theme: Theme | None = None,
) -> ScatterChart:
    """Create a scatter chart with the given data and options."""
    return ScatterChart(
        x_data=x_data,
        y_data=y_data,
        labels=labels,
        width=width,
        height=height,
        zero_index=zero_index,
        title=title,
        theme=theme,
    )


def chart(
    data: Vector | Vector2D | None = None,
    x_data: Vector | Vector2D | None = None,
    y_data: Vector | Vector2D | None = None,
    x_labels: Labels | None = None,
    y_labels: Labels | None = None,
    width: float = 500,
    height: float = 500,
    zero_index: bool = True,
    title: str | None = None,
    theme: Theme | None = None,
) -> Chart:
    """Create a generic chart with the given data and options."""
    return Chart(
        width=width,
        height=height,
        x_data=x_data,
        y_data=y_data,
        x_labels=x_labels,
        y_labels=y_labels,
        zero_index=zero_index,
        title=title,
        theme=theme,
    )
