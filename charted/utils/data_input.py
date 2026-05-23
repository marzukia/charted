"""Data input utilities for agent-friendly chart creation.

Provides functions to accept various data formats and auto-detect
the best chart type based on data shape.
"""

from __future__ import annotations

from typing import Any

from charted.constants import DEFAULT_CHART_HEIGHT, DEFAULT_CHART_WIDTH


def auto_size(data, width: float | None = None, height: float | None = None):
    """Calculate canvas dimensions based on data size.

    If width/height are not provided, scale up for datasets larger
    than the default 500x500 canvas.

    Args:
        data: Raw data (list or list-of-lists).
        width: Optional explicit width.
        height: Optional explicit height.

    Returns:
        Tuple of (width, height).
    """
    if width is not None and height is not None:
        return width, height

    # Estimate data size
    if isinstance(data, list):
        if not data:
            return DEFAULT_CHART_WIDTH, DEFAULT_CHART_HEIGHT
        if isinstance(data[0], list):
            n_rows = len(data)
            n_cols = len(data[0]) if data[0] else 0
        else:
            n_rows = 1
            n_cols = len(data)

        # Scale: 50px per data point, min 500x500
        if width is None:
            w = max(DEFAULT_CHART_WIDTH, n_cols * 50)
        else:
            w = width
        if height is None:
            h = max(DEFAULT_CHART_HEIGHT, n_rows * 50)
        else:
            h = height
        return w, h

    return DEFAULT_CHART_WIDTH, DEFAULT_CHART_HEIGHT


def from_dict(data: dict, **kwargs) -> Any:
    """Create a chart from a dict-based config.

    Expects a dict with at least ``data`` key containing the raw data,
    and an optional ``chart_type`` key. Remaining keys are passed as
    constructor arguments.

    Args:
        data: Dict with chart configuration.
        **kwargs: Override any config key.

    Returns:
        Chart instance.

    Example:
        >>> cfg = {
        ...     "chart_type": "BarChart",
        ...     "data": {"x_labels": ["A", "B"], "series": [[10, 20]]},
        ...     "title": "Sales",
        ... }
        >>> chart = from_dict(cfg)
    """
    from charted.charts import _CHART_CLASSES

    cfg = dict(data)
    cfg.update(kwargs)

    chart_type = cfg.pop("chart_type", None)
    raw = cfg.pop("data", None)
    cls_map = _CHART_CLASSES()

    if chart_type and chart_type in cls_map:
        chart_cls = cls_map[chart_type]
    else:
        chart_cls = cls_map.get("BarChart")

    # Flatten dict-style data into constructor args
    if isinstance(raw, dict):
        for key in ("x_labels", "y_labels", "series", "x_data", "y_data"):
            if key in raw:
                cfg.setdefault(key, raw[key])

    return chart_cls(**cfg)


def from_dataframe(df, **kwargs) -> Any:
    """Create a chart from a pandas DataFrame.

    Accepts an optional ``pandas.DataFrame``. If pandas is not installed,
    falls back to accepting a dict of column-name -> list.

    The first numeric column becomes y_data. The index (or first column
    of strings) becomes x_labels.

    Args:
        df: A pandas DataFrame, or a dict mapping column names to lists.
        **kwargs: Override any chart parameter.

    Returns:
        Chart instance.

    Raises:
        ImportError: If pandas is required but not available.
    """
    from charted.charts import _CHART_CLASSES

    # Try pandas import — graceful skip if unavailable
    try:
        import pandas as pd
    except ImportError:
        pd = None  # type: ignore

    chart_type = kwargs.pop("chart_type", None)
    cls_map = _CHART_CLASSES()

    if chart_type and chart_type in cls_map:
        chart_cls = cls_map[chart_type]
    else:
        chart_cls = cls_map.get("BarChart")

    if pd is not None and isinstance(df, pd.DataFrame):
        numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        if not numeric_cols:
            raise ValueError(
                "DataFrame has no numeric columns. "
                "Provide at least one numeric column as y_data."
            )

        y_data = [df[c].tolist() for c in numeric_cols]
        series_names = list(numeric_cols)

        # Use index or first string column as x_labels
        if df.index.name:
            x_labels = df.index.tolist()
        elif df.columns.dtype == "object":
            x_labels = df.index.tolist()
        else:
            x_labels = list(range(len(df)))

        return chart_cls(
            y_data=y_data, x_labels=x_labels, series_names=series_names, **kwargs
        )

    # Dict fallback: column-name -> list
    if isinstance(df, dict):
        keys = list(df.keys())
        if not keys:
            raise ValueError("Empty dict provided. Supply at least one data column.")

        # Pick first numeric-ish column as y_data
        y_data = [v for v in df.values()]
        series_names = keys

        # Use first key as x_labels if it's not numeric
        x_labels = list(range(len(y_data[0]))) if y_data else []

        return chart_cls(
            y_data=y_data, x_labels=x_labels, series_names=series_names, **kwargs
        )

    raise TypeError(
        f"Expected a pandas DataFrame or dict, got {type(df).__name__}. "
        "Pass a DataFrame with numeric columns or a dict of column -> list."
    )


def auto(data, **kwargs) -> Any:
    """Auto-detect chart type from data shape and create the chart.

    Heuristic:
    - 1D list → BarChart or PieChart
    - 2D list (single series) → LineChart or ColumnChart
    - 2D list (multiple series, all same length) → Grouped BarChart
    - 2D matrix (N rows of M values) → HeatmapChart

    Args:
        data: Raw data — list, list-of-lists, or dict.
        **kwargs: Additional chart parameters (title, theme, etc.).

    Returns:
        Chart instance.

    Example:
        >>> chart = auto([10, 20, 30], title="Sales")
        >>> chart = auto([[1, 2, 3], [4, 5, 6]], title="Matrix")
    """
    from charted.charts import _CHART_CLASSES

    cls_map = _CHART_CLASSES()

    # Auto-size if width/height not specified
    if "width" not in kwargs and "height" not in kwargs:
        w, h = auto_size(data, kwargs.get("width"), kwargs.get("height"))
        kwargs.setdefault("width", w)
        kwargs.setdefault("height", h)

    # Detect shape
    if isinstance(data, list):
        if not data:
            raise ValueError("Empty data list. Provide at least one value.")

        # 1D list — single series
        if not isinstance(data[0], list):
            # Small sets → PieChart, otherwise BarChart
            if len(data) <= 6:
                chart_cls = cls_map.get("PieChart")
            else:
                chart_cls = cls_map.get("BarChart")
            return chart_cls(data=data, **kwargs)

        # 2D data
        n_rows = len(data)
        n_cols = len(data[0]) if data[0] else 0

        if n_rows <= 3 and n_cols > 3:
            # Few rows, many columns — could be grouped bar or line
            chart_cls = cls_map.get("ColumnChart")
            return chart_cls(y_data=data, **kwargs)
        elif n_rows > 3 and n_cols <= 6:
            # Many rows, few columns — line chart
            chart_cls = cls_map.get("LineChart")
            return chart_cls(y_data=data, **kwargs)
        else:
            # Square-ish matrix — heatmap
            chart_cls = cls_map.get("HeatmapChart")
            return chart_cls(data=data, **kwargs)

    if isinstance(data, dict):
        # Dict of column -> list — use from_dataframe
        return from_dataframe(data, **kwargs)

    raise TypeError(
        f"Unsupported data type: {type(data).__name__}. "
        "Pass a list (1D or 2D) or a dict of column -> list."
    )
