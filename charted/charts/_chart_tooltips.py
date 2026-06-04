"""Tooltip methods for charts.

Extracted from the :class:`~charted.charts.chart.Chart` base class to reduce
its size. The methods are unchanged; they are mixed back into ``Chart`` via
the class bases, so they continue to operate on the same ``self``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from charted.html.element import Title
    from charted.utils.types import MeasuredText, Vector2D


class ChartTooltipMixin:
    """Tooltip behavior for :class:`Chart`.

    Provides the opt-in HTML-only native ``<title>`` hover labels. These rely on
    attributes supplied by the concrete chart class (``x_labels``,
    ``series_names``, ``y_data``, ``_tooltips``); they are declared here only for
    type checking.
    """

    if TYPE_CHECKING:
        _tooltips: bool
        series_names: list[str] | None

        @property
        def x_labels(self) -> list[MeasuredText] | None: ...

        @property
        def y_data(self) -> Vector2D: ...

    def _tooltip_label(self, series_idx: int, point_idx: int) -> str:
        """Build the tooltip text for one data point.

        Format is ``"<label>: <value>"`` when a category label is available,
        otherwise just the value. The series name is prefixed when there is
        more than one series so multi-series marks stay distinguishable.
        """
        value = self._tooltip_value(series_idx, point_idx)
        label = None
        if self.x_labels and point_idx < len(self.x_labels):
            lbl = self.x_labels[point_idx]
            label = lbl.text if hasattr(lbl, "text") else str(lbl)

        series_name = None
        if self.series_names and series_idx < len(self.series_names):
            series_name = self.series_names[series_idx]

        multi_series = len(self.y_data) > 1

        if label is not None:
            if multi_series:
                prefix = (
                    series_name
                    if series_name is not None
                    else f"Series {series_idx + 1}"
                )
                return f"{prefix} - {label}: {value}"
            return f"{label}: {value}"
        if series_name is not None:
            return f"{series_name}: {value}"
        if multi_series:
            return f"Series {series_idx + 1}: {value}"
        return str(value)

    def _tooltip_value(self, series_idx: int, point_idx: int) -> float | str:
        """Return the raw data value for a point (overridable per chart)."""
        data = self.y_data
        if series_idx < len(data) and point_idx < len(data[series_idx]):
            value = data[series_idx][point_idx]
            if isinstance(value, float) and value.is_integer():
                return int(value)
            return value
        return ""

    def _tooltip_title(self, series_idx: int, point_idx: int) -> "Title | None":
        """Return a ``Title`` element for a mark, or None when tooltips off."""
        if not self._tooltips:
            return None
        from charted.html.element import Title

        return Title(self._tooltip_label(series_idx, point_idx))
