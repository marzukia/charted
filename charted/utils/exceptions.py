"""Custom exceptions with agent-friendly error messages.

Each exception tells the agent *what to fix*, not just what went wrong.
"""


class ChartedError(Exception):
    """Base exception for all charted errors."""


class InvalidValue(ChartedError):
    def __init__(self, name: str, value: float):
        self.name = name
        self.value = value
        super().__init__(self.__str__())

    def __str__(self) -> str:
        return f"'{self.value}' is not a valid value for '{self.name}'"


class NoDataError(ChartedError):
    def __init__(self, msg: str | None = None):
        default_msg = (
            "No data was provided to the chart element. "
            "Pass data via the 'data', 'x_data', or 'y_data' parameter. "
            "Example: chart = BarChart(data=[10, 20, 30])"
        )
        super().__init__(msg if msg is not None else default_msg)


class DataShapeError(ChartedError):
    def __init__(self, expected: str, actual: str, detail: str = ""):
        self.expected = expected
        self.actual = actual
        self.detail = detail
        super().__init__(self.__str__())

    def __str__(self) -> str:
        msg = f"Data shape mismatch: expected {self.expected} but got {self.actual}. "
        if self.detail:
            msg += self.detail
        msg += (
            "Try reshaping your data or using a different chart type. "
            "For 1D data use BarChart or PieChart. "
            "For 2D data use LineChart, ColumnChart, or HeatmapChart."
        )
        return msg


class LabelMismatchError(ChartedError):
    def __init__(self, n_labels: int, n_data: int, axis: str = "x"):
        self.n_labels = n_labels
        self.n_data = n_data
        self.axis = axis
        super().__init__(self.__str__())

    def __str__(self) -> str:
        return (
            f"Label count mismatch: {self.n_labels} {self.axis}-labels "
            f"provided but data has {self.n_data} values. "
            f"Ensure len({self.axis}_labels) matches the data dimensions. "
            f"Example: {self.axis}_labels=['A', 'B', 'C'] for 3 data points."
        )


class ThemeError(ChartedError):
    def __init__(self, msg: str):
        super().__init__(
            f"Theme error: {msg}. "
            "Use Theme.from_preset('light'), Theme.from_preset('dark'), "
            "or construct a Theme() directly."
        )


class PaletteError(ChartedError):
    def __init__(self, name: str):
        from charted.themes.core import NAMED_PALETTES

        super().__init__(
            f"Unknown color palette: '{name}'. "
            f"Available palettes: {list(NAMED_PALETTES.keys())}. "
            "Example: palette='viridis' or palette=['#ff0', '#0f0', '#00f']"
        )


class UnknownChartTypeError(ChartedError):
    def __init__(self, chart_type: str):
        super().__init__(
            f"Unknown chart type: '{chart_type}'. "
            "Available types: BarChart, ColumnChart, LineChart, ScatterChart, "
            "PieChart, AreaChart, RadarChart, BoxPlot, Histogram, HeatmapChart, "
            "GanttChart, BubbleChart, ComboChart, PolarAreaChart. "
            "Use charted.auto(data) to auto-detect."
        )


class InvalidDataError(ChartedError):
    """Raised when chart data is invalid (wrong format, NaN values, etc.)."""

    pass


class ValidationError(ChartedError):
    """Raised when validation fails (theme, data, etc.)."""

    pass


class RenderError(ChartedError):
    """Raised when chart rendering fails."""

    pass
