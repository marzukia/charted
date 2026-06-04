from dataclasses import dataclass
from typing import NamedTuple, TypedDict

# Re-export exceptions from exceptions.py for backward compatibility


# A JSON-schema definition fragment. JSON schemas are recursive objects whose
# values are themselves schemas, primitives, or lists of either; ``object`` is
# the precise type for these heterogeneous leaves.
JSONSchema = dict[str, object]


class ChartedConfig(TypedDict, total=False):
    """Parsed ``.chartedrc`` configuration.

    Produced by :func:`charted.config.load_config`. Every key carries a default
    so consumers can ``.get`` safely; ``total=False`` reflects that a loaded TOML
    file may omit any of them.
    """

    font: str
    font_size: int
    title_font_size: int
    colors: list[str]
    width: float
    height: float
    theme: object | None
    charts: dict[str, object]
    pie: dict[str, object]
    bar: dict[str, object]
    column: dict[str, object]
    theme_section: dict[str, object]


# Data dict produced by the CLI loaders (``load_data`` / ``_parse_csv``) and the
# dict-config import path. Keys map directly onto chart constructor parameters,
# so the values are heterogeneous (raw vectors, labels, series dicts, scalars).
# ``object`` keeps it type-safe while permitting arbitrary constructor kwargs.
ChartDataDict = dict[str, object]


class SeriesStyleConfig(TypedDict, total=False):
    """Per-series styling overrides."""

    fill: str | None
    stroke: str | None
    stroke_width: float | None
    stroke_dasharray: str | None
    marker_shape: str | None  # "circle" | "square" | "diamond" | "none"
    marker_size: float | None
    fill_opacity: float | None
    stroke_opacity: float | None
    area_fill: bool | None
    area_fill_opacity: float | None
    show_markers: bool | None


class ReferenceLineDict(TypedDict, total=False):
    """One entry of the ``reference_lines`` convenience API.

    ``value`` is required in practice (validated by the chart); ``axis``
    defaults to ``"y"`` and ``label`` to ``None`` during normalisation.
    """

    value: float
    axis: str  # "x" | "y"
    label: str | None


class ValueLabelOptions(TypedDict, total=False):
    """Keyword options forwarded to ``charted.utils.value_format.format_value``.

    Mirrors that function's keyword-only parameters so the resolved value-label
    options can be splatted into it with full type checking. The ``format`` key
    is handled separately and is not part of this options mapping.
    """

    decimals: int | None
    prefix: str
    suffix: str
    currency_symbol: str
    thousands_sep: str
    percent_scale: bool


class ValueLabelConfig(TypedDict, total=False):
    """Normalised ``value_labels`` config from ``Chart._normalize_value_labels``.

    ``format`` selects the formatter; the remaining keys are forwarded to
    ``format_value`` (see :class:`ValueLabelOptions`).
    """

    format: str
    decimals: int | None
    prefix: str
    suffix: str
    currency_symbol: str
    thousands_sep: str
    percent_scale: bool


class PointStyleConfig(TypedDict, total=False):
    """Per-point marker styling overrides for scatter charts.

    Every field is optional; any omitted field falls back to the per-series
    style (``series_styles``)/shape-cycle resolution and finally the defaults.
    """

    marker_shape: (
        str | None
    )  # "circle" | "square" | "diamond" | "triangle" | "star" | "none"
    marker_size: float | None
    fill: str | None
    opacity: float | None


class CharMetrics(TypedDict):
    """Width and height of a single glyph at a given font size.

    The generator (:func:`charted.fonts.utils.create_font_definition`) writes
    integer pixel metrics from tkinter, so every definition file holds ints.
    """

    width: int
    height: int


# A loaded font-definition JSON file (``charted/fonts/definitions/*.json``).
# Outer key is the font size as a string, inner key the character code as a
# string, mapping to that glyph's measured metrics.
FontDefinition = dict[str, dict[str, CharMetrics]]


Labels = list[str]

Vector = list[float]
Vector2D = list[Vector]


class ComboSeriesDict(TypedDict, total=False):
    """One series entry for a combo (mixed bar/line/area) chart.

    ``data`` is the only field a caller must supply; ``type`` defaults to
    ``"line"``, ``axis`` to ``"primary"`` and ``name`` to ``None`` during
    normalisation inside :class:`charted.charts.combo.ComboChart`.
    """

    data: Vector
    type: str  # "bar" | "column" | "line" | "area"
    axis: str  # "primary" | "secondary"
    name: str | None


class MeasuredText(NamedTuple):
    text: str
    width: float
    height: float
    # Optional wrapped lines. When a label is wrapped to fit a width budget,
    # this holds the individual line strings (the renderer emits one tspan per
    # line). ``None`` means the label is a single line and renders as before.
    lines: list[str] | None = None


class Coordinate(NamedTuple):
    x: float
    y: float


class AxisDimension(NamedTuple):
    min_value: float
    max_value: float
    # `count` shadows tuple.count; keeping the public field name (used widely as
    # AxisDimension.count) means accepting this known NamedTuple/mypy clash.
    count: float  # type: ignore[assignment]

    @property
    def value_range(self) -> float:
        return self.max_value - self.min_value


@dataclass
class AxisValues:
    """Structured container for axis data to avoid connascence of position.

    Replaces the tuple (data, labels, zero_index) that was prone to
    ordering errors. Using a dataclass provides:
    - Self-documenting field names
    - Type safety via dataclass validation
    - Easier refactoring and maintenance
    """

    data: Vector2D | None = None
    labels: list[str] | None = None
    zero_index: bool = True
