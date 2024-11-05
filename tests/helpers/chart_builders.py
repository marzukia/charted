"""Pre-built chart configurations for testing."""

from charted import (
    BarChart,
    ColumnChart,
    LineChart,
    PieChart,
    RadarChart,
    ScatterChart,
)


def build_bar_chart(
    labels=None,
    data=None,
    **kwargs,
) -> BarChart:
    """Build a bar chart with default test data.

    Args:
        labels: Category labels (default: ["A", "B", "C"])
        data: Bar values (default: [10, 20, 30])
        **kwargs: Additional arguments passed to BarChart

    Returns:
        Configured BarChart instance
    """
    if labels is None:
        labels = ["A", "B", "C"]
    if data is None:
        data = [10, 20, 30]

    return BarChart(data=data, labels=labels, **kwargs)


def build_column_chart(
    labels=None,
    data=None,
    stacked=True,
    **kwargs,
) -> ColumnChart:
    """Build a column chart with default test data.

    Args:
        labels: Category labels (default: ["Q1", "Q2", "Q3"])
        data: Column values (default: [100, 150, 200])
        stacked: Whether to stack multiple series
        **kwargs: Additional arguments passed to ColumnChart

    Returns:
        Configured ColumnChart instance
    """
    if labels is None:
        labels = ["Q1", "Q2", "Q3"]
    if data is None:
        data = [100, 150, 200]

    return ColumnChart(data=data, labels=labels, y_stacked=stacked, **kwargs)


def build_line_chart(
    labels=None,
    data=None,
    **kwargs,
) -> LineChart:
    """Build a line chart with default test data.

    Args:
        labels: X-axis labels (default: ["Jan", "Feb", "Mar"])
        data: Line values (default: [65, 59, 80])
        **kwargs: Additional arguments passed to LineChart

    Returns:
        Configured LineChart instance
    """
    if labels is None:
        labels = ["Jan", "Feb", "Mar"]
    if data is None:
        data = [65, 59, 80]

    return LineChart(data=data, labels=labels, **kwargs)


def build_pie_chart(
    labels=None,
    data=None,
    doughnut=False,
    **kwargs,
) -> PieChart:
    """Build a pie chart with default test data.

    Args:
        labels: Slice labels (default: ["A", "B", "C"])
        data: Slice values (default: [25, 35, 40])
        doughnut: Whether to render as doughnut chart
        **kwargs: Additional arguments passed to PieChart

    Returns:
        Configured PieChart instance
    """
    if labels is None:
        labels = ["A", "B", "C"]
    if data is None:
        data = [25, 35, 40]

    inner_radius = 0.5 if doughnut else 0
    return PieChart(data=data, labels=labels, inner_radius=inner_radius, **kwargs)


def build_radar_chart(
    labels=None,
    data=None,
    **kwargs,
) -> RadarChart:
    """Build a radar chart with default test data.

    Args:
        labels: Axis labels (default: ["A", "B", "C", "D", "E"])
        data: Axis values (default: [30, 40, 50, 60, 70])
        **kwargs: Additional arguments passed to RadarChart

    Returns:
        Configured RadarChart instance
    """
    if labels is None:
        labels = ["A", "B", "C", "D", "E"]
    if data is None:
        data = [30, 40, 50, 60, 70]

    return RadarChart(data=data, labels=labels, **kwargs)


def build_scatter_chart(
    x_data=None,
    y_data=None,
    **kwargs,
) -> ScatterChart:
    """Build a scatter chart with default test data.

    Args:
        x_data: X coordinates (default: [1, 2, 3, 4, 5])
        y_data: Y coordinates (default: [10, 20, 30, 40, 50])
        **kwargs: Additional arguments passed to ScatterChart

    Returns:
        Configured ScatterChart instance
    """
    if x_data is None:
        x_data = [1, 2, 3, 4, 5]
    if y_data is None:
        y_data = [10, 20, 30, 40, 50]

    return ScatterChart(x_data=x_data, y_data=y_data, **kwargs)


# Multi-series chart builders


def build_multi_series_bar(
    num_series=3,
    num_categories=4,
    **kwargs,
) -> BarChart:
    """Build a multi-series bar chart.

    Args:
        num_series: Number of data series
        num_categories: Number of categories per series
        **kwargs: Additional arguments passed to BarChart

    Returns:
        Configured BarChart instance with multiple series
    """
    labels = [f"Category {i}" for i in range(num_categories)]
    data = [[i * 10 + j for j in range(num_categories)] for i in range(num_series)]

    return BarChart(data=data, labels=labels, **kwargs)


def build_multi_series_column(
    num_series=2,
    num_categories=5,
    stacked=False,
    **kwargs,
) -> ColumnChart:
    """Build a multi-series column chart.

    Args:
        num_series: Number of data series
        num_categories: Number of categories per series
        stacked: Whether to stack columns
        **kwargs: Additional arguments passed to ColumnChart

    Returns:
        Configured ColumnChart instance with multiple series
    """
    labels = [f"Q{i + 1}" for i in range(num_categories)]
    data = [[i * 20 + j for j in range(num_categories)] for i in range(num_series)]

    return ColumnChart(data=data, labels=labels, y_stacked=stacked, **kwargs)
