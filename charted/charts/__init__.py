"""Chart types - exports all available chart classes."""

from .area import AreaChart
from .bar import BarChart
from .box import BoxPlot
from .chart import Chart
from .column import ColumnChart
from .gantt import GanttChart
from .heatmap import HeatmapChart
from .histogram import Histogram
from .line import LineChart
from .pie import PieChart
from .radar import RadarChart
from .scatter import ScatterChart

__all__ = [
    "AreaChart",
    "BarChart",
    "BoxPlot",
    "Chart",
    "ColumnChart",
    "GanttChart",
    "HeatmapChart",
    "Histogram",
    "LineChart",
    "PieChart",
    "RadarChart",
    "ScatterChart",
]


def _CHART_CLASSES() -> dict:
    """Return a mapping of chart type names to their classes.

    Used by Chart.from_config() to instantiate the right subclass.
    """
    return {
        "AreaChart": AreaChart,
        "BarChart": BarChart,
        "BoxPlot": BoxPlot,
        "ColumnChart": ColumnChart,
        "GanttChart": GanttChart,
        "HeatmapChart": HeatmapChart,
        "Histogram": Histogram,
        "LineChart": LineChart,
        "PieChart": PieChart,
        "RadarChart": RadarChart,
        "ScatterChart": ScatterChart,
    }
