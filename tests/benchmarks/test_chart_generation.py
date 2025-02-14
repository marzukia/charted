"""Performance benchmarks for chart generation.

Run with: uv run pytest tests/benchmarks/ --benchmark-autosave
View results: uv run pytest tests/benchmarks/ --benchmark-only
"""

import pytest


@pytest.mark.benchmark(group="bar-chart")
def test_bar_chart_small_data(benchmark):
    """Benchmark bar chart generation with small dataset (10 points)."""
    from charted import BarChart

    def generate():
        return BarChart(data=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

    chart = benchmark(generate)
    # Force SVG generation
    _ = chart.html
    assert chart is not None


@pytest.mark.benchmark(group="bar-chart")
def test_bar_chart_medium_data(benchmark):
    """Benchmark bar chart generation with medium dataset (100 points)."""
    from charted import BarChart

    def generate():
        return BarChart(data=list(range(1, 101)))

    chart = benchmark(generate)
    _ = chart.html
    assert chart is not None


@pytest.mark.benchmark(group="bar-chart")
def test_bar_chart_large_data(benchmark):
    """Benchmark bar chart generation with large dataset (1000 points)."""
    from charted import BarChart

    def generate():
        return BarChart(data=list(range(1, 1001)))

    chart = benchmark(generate)
    _ = chart.html
    assert chart is not None


@pytest.mark.benchmark(group="column-chart")
def test_column_chart_small_data(benchmark):
    """Benchmark column chart generation with small dataset."""
    from charted import ColumnChart

    def generate():
        return ColumnChart(data=[10, 20, 30, 40, 50], labels=["A", "B", "C", "D", "E"])

    chart = benchmark(generate)
    _ = chart.html


@pytest.mark.benchmark(group="column-chart")
def test_column_chart_multi_series(benchmark):
    """Benchmark column chart with multiple series."""
    from charted import ColumnChart

    def generate():
        return ColumnChart(
            data=[[10, 20, 30], [15, 25, 35], [12, 22, 32]],
            labels=["A", "B", "C"],
        )

    chart = benchmark(generate)
    _ = chart.html


@pytest.mark.benchmark(group="line-chart")
def test_line_chart_small_data(benchmark):
    """Benchmark line chart generation with small dataset."""
    from charted import LineChart

    def generate():
        return LineChart(data=[10, 20, 30, 40, 50])

    chart = benchmark(generate)
    _ = chart.html


@pytest.mark.benchmark(group="line-chart")
def test_line_chart_large_data(benchmark):
    """Benchmark line chart with large dataset."""
    from charted import LineChart

    def generate():
        return LineChart(data=list(range(1, 501)))

    chart = benchmark(generate)
    _ = chart.html


@pytest.mark.benchmark(group="pie-chart")
def test_pie_chart_small_data(benchmark):
    """Benchmark pie chart generation with small dataset."""
    from charted import PieChart

    def generate():
        return PieChart(data=[25, 35, 40], labels=["A", "B", "C"])

    chart = benchmark(generate)
    _ = chart.html


@pytest.mark.benchmark(group="pie-chart")
def test_pie_chart_many_slices(benchmark):
    """Benchmark pie chart with many slices."""
    from charted import PieChart

    def generate():
        return PieChart(data=list(range(1, 21)))  # 20 slices

    chart = benchmark(generate)
    _ = chart.html


@pytest.mark.benchmark(group="scatter-chart")
def test_scatter_chart_small_data(benchmark):
    """Benchmark scatter chart generation."""
    from charted import ScatterChart

    def generate():
        return ScatterChart(x_data=[1, 2, 3, 4, 5], y_data=[10, 20, 30, 40, 50])

    chart = benchmark(generate)
    _ = chart.html


@pytest.mark.benchmark(group="scatter-chart")
def test_scatter_chart_large_data(benchmark):
    """Benchmark scatter chart with many points."""
    from charted import ScatterChart

    def generate():
        return ScatterChart(x_data=list(range(1, 201)), y_data=list(range(1, 201)))

    chart = benchmark(generate)
    _ = chart.html


@pytest.mark.benchmark(group="radar-chart")
def test_radar_chart_small_data(benchmark):
    """Benchmark radar chart generation."""
    from charted import RadarChart

    def generate():
        return RadarChart(data=[30, 40, 50, 60, 70], labels=["A", "B", "C", "D", "E"])

    chart = benchmark(generate)
    _ = chart.html


@pytest.mark.benchmark(group="theme")
def test_theme_loading(benchmark):
    """Benchmark theme loading and application."""
    from charted.themes.core import Theme

    def create_theme():
        return Theme()

    theme = benchmark(create_theme)
    assert theme is not None


@pytest.mark.benchmark(group="theme")
def test_theme_with_custom_colors(benchmark):
    """Benchmark theme with custom color generation."""
    from charted import Theme

    def create_theme():
        return Theme(colors=["#FF0000", "#00FF00", "#0000FF"])

    theme = benchmark(create_theme)
    assert len(theme.colors) == 3


@pytest.mark.benchmark(group="validation")
def test_data_validation_small(benchmark):
    """Benchmark data validation with small dataset."""
    from charted.utils.data_model import DataModel

    def validate():
        return DataModel.validate_data(list(range(1, 51)))

    result = benchmark(validate)
    assert len(result) == 1


@pytest.mark.benchmark(group="validation")
def test_data_validation_large(benchmark):
    """Benchmark data validation with large dataset."""
    from charted.utils.data_model import DataModel

    def validate():
        return DataModel.validate_data(list(range(1, 5001)))

    result = benchmark(validate)
    assert len(result) == 1


@pytest.mark.benchmark(group="svg-output")
def test_svg_generation_size(benchmark):
    """Benchmark SVG generation and measure output size."""
    from charted import BarChart

    def generate_and_measure():
        chart = BarChart(data=list(range(1, 101)))
        svg = chart.html
        return len(svg)

    size = benchmark(generate_and_measure)
    assert size > 0


@pytest.mark.benchmark(group="multi-series")
def test_multi_series_chart_generation(benchmark):
    """Benchmark multi-series chart with varying series counts."""
    from charted import BarChart

    def generate():
        # Generate 5 series with 20 data points each
        data = [list(range(i, i + 20)) for i in range(0, 100, 20)]
        return BarChart(data=data)

    chart = benchmark(generate)
    _ = chart.html
