"""Data input utilities for agent-friendly chart creation.

Provides functions to accept various data formats and auto-detect
the best chart type based on data shape.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, cast

from charted.constants import DEFAULT_CHART_HEIGHT, DEFAULT_CHART_WIDTH

if TYPE_CHECKING:
    from charted.charts import Chart


class _ChartFactory(Protocol):
    """Callable producing a chart from keyword-only constructor arguments."""

    def __call__(self, **kwargs: object) -> Chart: ...


def _construct(chart_cls: type[Chart], **kwargs: object) -> Chart:
    """Instantiate a chart class with dynamically-built keyword arguments.

    The keyword arguments are assembled at runtime from heterogeneous user
    data, so they are typed as ``object`` and the concrete subclass signature
    cannot be checked statically. The cast localises that one unavoidable
    dynamic call.
    """
    return cast("_ChartFactory", chart_cls)(**kwargs)


def auto_size(
    data: object, width: float | None = None, height: float | None = None
) -> tuple[float, float]:
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
        w: float
        h: float
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


def from_dict(data: dict[str, object], **kwargs: object) -> Chart:
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

    chart_cls: type[Chart]
    if isinstance(chart_type, str) and chart_type in cls_map:
        chart_cls = cls_map[chart_type]
    else:
        chart_cls = cls_map["BarChart"]

    # Flatten dict-style data into constructor args
    if isinstance(raw, dict):
        for key in ("x_labels", "y_labels", "series", "x_data", "y_data"):
            if key in raw:
                cfg.setdefault(key, raw[key])
        # Map 'series' to 'data' or 'y_data' depending on target chart class
        import inspect

        sig = inspect.signature(chart_cls.__init__)
        valid_params = set(sig.parameters.keys()) - {"self"}
        if "series" in cfg and "data" not in cfg:
            if "data" in valid_params:
                cfg["data"] = cfg.pop("series")
            elif "y_data" in valid_params:
                cfg["y_data"] = cfg.pop("series")
            else:
                cfg.pop("series", None)
    elif raw is not None:
        # Pass raw data back as the chart's data parameter
        cfg["data"] = raw

    # Filter kwargs to only valid params for the chart class
    import inspect

    sig = inspect.signature(chart_cls.__init__)
    valid_params = set(sig.parameters.keys()) - {"self"}
    filtered_cfg = {k: v for k, v in cfg.items() if k in valid_params}
    return _construct(chart_cls, **filtered_cfg)


def from_dataframe(df: object, **kwargs: object) -> Chart:
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

    # Try pandas import: graceful skip if unavailable
    try:
        import pandas as pd  # type: ignore[import-untyped]
    except ImportError:
        pd = None

    chart_type = kwargs.pop("chart_type", None)
    cls_map = _CHART_CLASSES()

    chart_cls: type[Chart]
    if isinstance(chart_type, str) and chart_type in cls_map:
        chart_cls = cls_map[chart_type]
    else:
        chart_cls = cls_map["BarChart"]

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

        return _construct(
            chart_cls,
            y_data=y_data,
            x_labels=x_labels,
            series_names=series_names,
            **kwargs,
        )

    # Dict fallback: column-name -> list
    if isinstance(df, dict):
        keys = list(df.keys())
        if not keys:
            raise ValueError("Empty dict provided. Supply at least one data column.")

        # All column values become series data
        y_data = [v for v in df.values()]
        series_names = keys

        # Use index as x_labels
        x_labels = list(range(len(y_data[0]))) if y_data else []

        # Build kwargs matching the chart class signature
        import inspect

        sig = inspect.signature(chart_cls.__init__)
        valid_params = set(sig.parameters.keys()) - {"self"}
        chart_kwargs: dict[str, object] = {}
        # Map x_labels -> labels for classes that expect labels
        labels_param = "labels" if "labels" in valid_params else "x_labels"
        if labels_param in valid_params:
            chart_kwargs[labels_param] = x_labels
        if "series_names" in valid_params:
            chart_kwargs["series_names"] = series_names
        # Map data param: 'data' or 'y_data'
        data_param = "data" if "data" in valid_params else "y_data"
        chart_kwargs[data_param] = y_data
        # Forward any extra kwargs that match valid params
        for k, v in kwargs.items():
            if k in valid_params:
                chart_kwargs[k] = v
        return _construct(chart_cls, **chart_kwargs)

    raise TypeError(
        f"Expected a pandas DataFrame or dict, got {type(df).__name__}. "
        "Pass a DataFrame with numeric columns or a dict of column -> list."
    )


def auto(data: object, **kwargs: object) -> Chart:
    """Auto-detect chart type from data shape and create the chart.

    Heuristic:
    - 1D list → BarChart or PieChart
    - 2D list (single series) → LineChart or ColumnChart
    - 2D list (multiple series, all same length) → Grouped BarChart
    - 2D matrix (N rows of M values) → HeatmapChart

    Args:
        data: Raw data: list, list-of-lists, or dict.
        **kwargs: Additional chart parameters (title, theme, etc.).

    Returns:
        Chart instance.

    Example:
        >>> chart = auto([10, 20, 30], title="Sales")
        >>> chart = auto([[1, 2, 3], [4, 5, 6]], title="Matrix")
    """
    from charted.charts import _CHART_CLASSES

    cls_map = _CHART_CLASSES()
    chart_cls: type[Chart]

    # Auto-size if width/height not specified
    if "width" not in kwargs and "height" not in kwargs:
        kw_width = kwargs.get("width")
        kw_height = kwargs.get("height")
        w, h = auto_size(
            data,
            kw_width if isinstance(kw_width, (int, float)) else None,
            kw_height if isinstance(kw_height, (int, float)) else None,
        )
        kwargs.setdefault("width", w)
        kwargs.setdefault("height", h)

    # Bubble detection: an explicit `sizes` kwarg, or 2D data shaped as three
    # equal-length rows [x, y, sizes], signals a third numeric dimension that
    # maps to marker radius -> BubbleChart.
    if "sizes" in kwargs and kwargs["sizes"] is not None:
        chart_cls = cls_map["BubbleChart"]
        x: object
        y: object
        if isinstance(data, list) and data and isinstance(data[0], list):
            x, y = data[0], data[1]
        elif isinstance(data, list):
            x = list(range(len(data)))
            y = data
        else:
            x = []
            y = data
        return _construct(chart_cls, x_data=x, y_data=y, **kwargs)

    # Detect shape
    if isinstance(data, list):
        if not data:
            raise ValueError("Empty data list. Provide at least one value.")

        # 1D list: single series
        if not isinstance(data[0], list):
            # Small sets → PieChart, otherwise BarChart
            if len(data) <= 6:
                chart_cls = cls_map["PieChart"]
            else:
                chart_cls = cls_map["BarChart"]
            return _construct(chart_cls, data=data, **kwargs)

        # 2D data
        n_rows = len(data)
        n_cols = len(data[0]) if data[0] else 0

        if n_rows <= 3 and n_cols > 3:
            # Few rows, many columns: could be grouped bar or line
            chart_cls = cls_map["ColumnChart"]
            return _construct(chart_cls, data=data, **kwargs)
        elif n_rows > 3 and n_cols <= 6:
            # Many rows, few columns: line chart
            chart_cls = cls_map["LineChart"]
            return _construct(chart_cls, data=data, **kwargs)
        else:
            # Square-ish matrix: heatmap
            chart_cls = cls_map["HeatmapChart"]
            return _construct(chart_cls, data=data, **kwargs)

    if isinstance(data, dict):
        # Dict of column -> list: use from_dataframe
        return from_dataframe(data, **kwargs)

    raise TypeError(
        f"Unsupported data type: {type(data).__name__}. "
        "Pass a list (1D or 2D) or a dict of column -> list."
    )
