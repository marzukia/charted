"""Data loading utilities for charted.

Provides functions to load data from various file formats (CSV, JSON, TSV)
without requiring external dependencies like pandas.
"""

__all__ = ["load_data", "load_csv", "load_json"]

import csv
import json
from pathlib import Path


def load_data(
    source: str | Path,
    x_col: str | None = None,
    y_col: str | None = None,
    delimiter: str | None = None,
) -> tuple[list[str], list[float], list[str]]:
    """Load data from a file and return x_data, y_data, and labels.

    Auto-detects file format based on extension (.csv, .tsv, .json).

    Args:
        source: Path to the data file.
        x_col: Column name for x-axis data (required for CSV/TSV).
        y_col: Column name for y-axis data (required for CSV/TSV).
        delimiter: Field delimiter for CSV/TSV (auto-detected if None).

    Returns:
        Tuple of (x_data, y_data, labels) where:
        - x_data: List of x-axis values (strings or numbers)
        - y_data: List of y-axis values (floats)
        - labels: List of series/label names

    Raises:
        FileNotFoundError: If the source file doesn't exist.
        ValueError: If required columns are missing or data is invalid.

    Example:
        >>> # CSV with columns: Quarter, Revenue
        >>> x, y, labels = load_data("sales.csv", x_col="Quarter", y_col="Revenue")
        >>>
        >>> # JSON array of numbers
        >>> x, y, labels = load_data("data.json")
        >>>
        >>> # JSON object with data and labels
        >>> x, y, labels = load_data("metrics.json")
    """
    source = Path(source)

    if not source.exists():
        raise FileNotFoundError(f"Data file not found: {source}")

    suffix = source.suffix.lower()

    if suffix in (".csv", ".tsv"):
        return _load_csv(source, x_col, y_col, delimiter)
    elif suffix == ".json":
        return _load_json(source)
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Use .csv, .tsv, or .json")


def _load_csv(
    path: Path,
    x_col: str | None,
    y_col: str | None,
    delimiter: str | None,
) -> tuple[list[str], list[float], list[str]]:
    """Load data from a CSV or TSV file."""
    if delimiter is None:
        delimiter = "\t" if path.suffix == ".tsv" else ","

    if x_col is None or y_col is None:
        raise ValueError("x_col and y_col are required for CSV/TSV files")

    x_data: list[str] = []
    y_data: list[float] = []
    labels: list[str] = []

    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=delimiter)

        # Validate columns exist
        if reader.fieldnames is None:
            raise ValueError(f"Empty or invalid CSV file: {path}")

        if x_col not in reader.fieldnames:
            raise ValueError(
                f"Column '{x_col}' not found in {path}. Available: {reader.fieldnames}"
            )
        if y_col not in reader.fieldnames:
            raise ValueError(
                f"Column '{y_col}' not found in {path}. Available: {reader.fieldnames}"
            )

        for row in reader:
            x_data.append(row[x_col])
            try:
                y_data.append(float(row[y_col]))
            except (ValueError, TypeError):
                raise ValueError(
                    f"Invalid numeric value in column '{y_col}': {row[y_col]}"
                )

    # Use y_col name as series label
    labels = [y_col]

    return x_data, y_data, labels


def _load_json(path: Path) -> tuple[list[str], list[float], list[str]]:
    """Load data from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle different JSON structures
    if isinstance(data, list):
        # Simple array of numbers: [1, 2, 3]
        if all(isinstance(x, (int, float)) for x in data):
            x_data = [str(i) for i in range(len(data))]
            y_data = [float(x) for x in data]
            labels = [path.stem]
            return x_data, y_data, labels

        # Array of objects: [{"label": "Q1", "value": 100}, ...]
        if all(isinstance(x, dict) for x in data):
            # Try common key names
            value_keys = ["value", "y", "data", "amount", "count"]
            label_keys = ["label", "x", "name", "category"]

            value_key = next((k for k in value_keys if k in data[0]), None)
            label_key = next((k for k in label_keys if k in data[0]), None)

            if value_key is None:
                raise ValueError(
                    f"No numeric value key found in JSON objects. "
                    f"Available keys: {list(data[0].keys())}"
                )

            x_data = [str(item.get(label_key, i)) for i, item in enumerate(data)]
            y_data = [float(item[value_key]) for item in data]
            labels = [path.stem]

            return x_data, y_data, labels

    elif isinstance(data, dict):
        # Object with explicit data and labels
        # {"data": [1,2,3], "labels": ["a","b","c"]}
        if "data" in data and "labels" in data:
            x_data = [str(x) for x in data["labels"]]
            y_data = [float(x) for x in data["data"]]
            labels = [data.get("title", path.stem)]
            return x_data, y_data, labels

        # Object with single series: {"Q1": 100, "Q2": 200}
        if all(isinstance(v, (int, float)) for v in data.values()):
            x_data = list(data.keys())
            y_data = [float(v) for v in data.values()]
            labels = [path.stem]
            return x_data, y_data, labels
    raise ValueError(
        f"Unsupported JSON structure in {path}. "
        "Expected array of numbers, array of objects, "
        "or object with 'data' and 'labels'"
    )


def load_csv(
    path: str | Path,
    x_col: str,
    y_col: str,
    delimiter: str | None = None,
) -> tuple[list[str], list[float], list[str]]:
    """Load data from a CSV file.

    Convenience wrapper around load_data for CSV files.

    Args:
        path: Path to the CSV file.
        x_col: Column name for x-axis.
        y_col: Column name for y-axis.
        delimiter: Field delimiter (comma by default, tab for .tsv).

    Returns:
        Tuple of (x_data, y_data, labels).

    Example:
        >>> x, y, labels = load_csv("sales.csv", x_col="Quarter", y_col="Revenue")
    """
    return load_data(path, x_col=x_col, y_col=y_col, delimiter=delimiter)


def load_json(path: str | Path) -> tuple[list[str], list[float], list[str]]:
    """Load data from a JSON file.

    Convenience wrapper around load_data for JSON files.

    Args:
        path: Path to the JSON file.

    Returns:
        Tuple of (x_data, y_data, labels).

    Example:
        >>> x, y, labels = load_json("sales.json")
    """
    return load_data(path)
