"""Pytest configuration and shared fixtures for charted tests."""

import pytest


@pytest.fixture
def sample_bar_data():
    """Sample data for bar chart tests."""
    return {
        "labels": ["A", "B", "C", "D"],
        "data": [10, 20, 30, 40],
    }


@pytest.fixture
def sample_multi_series_data():
    """Sample multi-series data for chart tests."""
    return {
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "data": [[10, 20, 30], [15, 25, 35], [12, 22, 32]],
    }


@pytest.fixture
def sample_pie_data():
    """Sample data for pie chart tests."""
    return {
        "labels": ["Product A", "Product B", "Product C"],
        "data": [25, 35, 40],
    }


@pytest.fixture
def sample_scatter_data():
    """Sample data for scatter plot tests."""
    return {
        "x_data": [1, 2, 3, 4, 5],
        "y_data": [10, 20, 30, 40, 50],
    }


@pytest.fixture
def sample_line_data():
    """Sample data for line chart tests."""
    return {
        "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
        "data": [65, 59, 80, 81, 56],
    }


@pytest.fixture
def large_dataset():
    """Large dataset for performance testing."""
    return list(range(1, 1001))


@pytest.fixture
def edge_case_data():
    """Edge case data for robustness testing."""
    return {
        "single_value": [42],
        "zeros": [0, 0, 0],
        "negative": [-10, -20, -30],
        "mixed": [-10, 0, 10],
        "very_large": [1e9, 2e9, 3e9],
        "very_small": [1e-9, 2e-9, 3e-9],
        "decimal": [1.5, 2.5, 3.5],
    }


@pytest.fixture
def unicode_labels():
    """Unicode labels for internationalization testing."""
    return ["α", "β", "γ", "δ", "ε"]  # Greek letters


@pytest.fixture
def empty_data():
    """Empty data for error handling tests."""
    return {"labels": [], "data": []}


@pytest.fixture
def invalid_data():
    """Invalid data for error handling tests."""
    return {
        "negative_pie": [-10, -20, -30],  # Invalid for pie charts
        "zero_sum": [0, 0, 0],  # Invalid for pie charts
        "nan_values": [10, float("nan"), 30],
        "infinity_values": [10, float("inf"), 30],
    }


@pytest.fixture
def custom_theme_colors():
    """Custom theme with specific colors."""
    return {
        "colors": ["#FF0000", "#00FF00", "#0000FF"],
        "background_color": "#FFFFFF",
    }


@pytest.fixture
def accessible_theme_colors():
    """Theme with high-contrast, colorblind-safe colors."""
    # Based on ColorBrewer and WCAG guidelines
    return {
        "colors": ["#000000", "#555555", "#AAAAAA"],  # Grayscale for maximum contrast
        "background_color": "#FFFFFF",
    }


@pytest.fixture
def temp_output_path(tmp_path):
    """Temporary path for output files."""
    return tmp_path / "output.svg"


# Configure hypothesis for all property tests
try:
    from hypothesis import HealthCheck, settings

    settings.register_profile(
        "ci",
        max_examples=100,
        suppress_health_check=[HealthCheck.too_slow],
    )
    settings.load_profile("ci")
except ImportError:
    pass  # Hypothesis not installed
