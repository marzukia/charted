"""Chart types - exports all available chart classes."""

from .area import AreaChart
from .bar import BarChart
from .box import BoxPlot
from .bubble import BubbleChart
from .chart import Chart
from .column import ColumnChart
from .combo import ComboChart
from .gantt import GanttChart
from .heatmap import HeatmapChart
from .histogram import Histogram
from .line import LineChart
from .pie import PieChart
from .polar_area import PolarAreaChart
from .radar import RadarChart
from .sankey import SankeyChart
from .scatter import ScatterChart

__all__ = [
    "AreaChart",
    "BarChart",
    "BoxPlot",
    "BubbleChart",
    "Chart",
    "ColumnChart",
    "ComboChart",
    "GanttChart",
    "HeatmapChart",
    "Histogram",
    "LineChart",
    "PieChart",
    "PolarAreaChart",
    "RadarChart",
    "SankeyChart",
    "ScatterChart",
]


def _CHART_CLASSES() -> dict[str, type[Chart]]:
    """Return a mapping of chart type names to their classes.

    Used by Chart.from_config() to instantiate the right subclass.
    """
    return {
        "AreaChart": AreaChart,
        "BarChart": BarChart,
        "BoxPlot": BoxPlot,
        "BubbleChart": BubbleChart,
        "ColumnChart": ColumnChart,
        "ComboChart": ComboChart,
        "GanttChart": GanttChart,
        "HeatmapChart": HeatmapChart,
        "Histogram": Histogram,
        "LineChart": LineChart,
        "PieChart": PieChart,
        "PolarAreaChart": PolarAreaChart,
        "RadarChart": RadarChart,
        "SankeyChart": SankeyChart,
        "ScatterChart": ScatterChart,
    }
