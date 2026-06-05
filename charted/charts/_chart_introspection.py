"""Introspection methods for charts.

Extracted from the :class:`~charted.charts.chart.Chart` base class to reduce
its size. The methods are unchanged; they are mixed back into ``Chart`` via
the class bases, so they continue to operate on the same ``self``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from charted.utils.data_model import DataModel
    from charted.utils.types import MeasuredText


class ChartIntrospectionMixin:
    """Read-only metadata behavior for :class:`Chart`.

    Provides ``describe``, a structured-metadata accessor for agent workflows.
    It relies on attributes supplied by the concrete chart class (``_width``,
    ``_height``, ``_title``, ``data_model``, ``series_names`` and others); they
    are declared here only for type checking. The ``_pie_data`` / ``_pie_labels``
    attributes live on subclasses and are read under ``hasattr`` guards, so they
    are not declared here.
    """

    if TYPE_CHECKING:
        _width: float
        _height: float
        _title: MeasuredText | None
        series_names: list[str] | None
        data_model: DataModel

        @property
        def x_labels(self) -> list[MeasuredText] | None: ...

        @property
        def y_labels(self) -> list[MeasuredText] | None: ...

        @property
        def x_scale(self) -> str: ...

        @property
        def y_scale(self) -> str: ...

    def describe(self) -> dict[str, object]:
        """Return a structured dictionary of chart metadata.

        Useful for AI agents that need to reason about a chart they just
        created. Contains chart type, dimensions, series statistics,
        labels, and layout flags.

        Returns:
            Dict with keys: chart_type, title, dimensions, series,
            labels, label_count, series_count, theme, has_negative_values,
            stacked.
        """
        # Determine the raw data series to compute stats over.
        # PieChart stores its real data in _pie_data; base class gets synthetic data.
        # BarChart stores values in x_data (horizontal bars); detect via x_stacked attr.
        if hasattr(self, "_pie_data"):
            raw_series = [self._pie_data]
        elif getattr(self, "x_stacked", False) or (
            self.data_model.x_data and self.__class__.__name__ == "BarChart"
        ):
            raw_series = self.data_model.x_data
        else:
            raw_series = self.data_model.y_data

        # Build per-series stats
        series_info = []
        for i, series_data in enumerate(raw_series):
            name = None
            if self.series_names and i < len(self.series_names):
                name = self.series_names[i]
            count = len(series_data)
            s_min = float(min(series_data))
            s_max = float(max(series_data))
            s_sum = float(sum(series_data))
            s_mean = s_sum / count if count else 0.0
            series_info.append(
                {
                    "name": name,
                    "count": count,
                    "min": s_min,
                    "max": s_max,
                    "mean": s_mean,
                    "sum": s_sum,
                }
            )

        # Determine labels list: check pie labels, then y_labels (BarChart),
        # then x_labels (most chart types)
        if hasattr(self, "_pie_labels") and self._pie_labels:
            labels = [
                lbl.text if hasattr(lbl, "text") else str(lbl)
                for lbl in self._pie_labels
            ]
        elif self.y_labels:
            labels = [
                lbl.text if hasattr(lbl, "text") else str(lbl) for lbl in self.y_labels
            ]
        elif self.x_labels:
            labels = [
                lbl.text if hasattr(lbl, "text") else str(lbl) for lbl in self.x_labels
            ]
        else:
            labels = None

        label_count = (
            len(labels) if labels else (len(raw_series[0]) if raw_series else 0)
        )

        # Detect negative values across all series
        has_negative = any(val < 0 for series_data in raw_series for val in series_data)

        # Stacked flag: either x_stacked (BarChart) or y_stacked (ColumnChart)
        stacked = bool(
            getattr(self, "x_stacked", False) or getattr(self, "y_stacked", False)
        )

        return {
            "chart_type": self.__class__.__name__,
            "title": self._title.text if self._title else None,
            "dimensions": {"width": self._width, "height": self._height},
            "series": series_info,
            "labels": labels,
            "label_count": label_count,
            "series_count": len(raw_series),
            "theme": "default",
            "has_negative_values": has_negative,
            "stacked": stacked,
            "scales": {"x": self.x_scale, "y": self.y_scale},
        }
