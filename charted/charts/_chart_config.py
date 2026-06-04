"""Config serialization methods for charts.

Extracted from the :class:`~charted.charts.chart.Chart` base class to reduce
its size. The methods are unchanged; they are mixed back into ``Chart`` via
the class bases, so they continue to operate on the same ``self``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from charted.charts.chart import Chart, _Annotation
    from charted.utils.data_model import DataModel
    from charted.utils.types import MeasuredText, SeriesStyleConfig


class ChartConfigMixin:
    """Config-serialization behavior for :class:`Chart`.

    Provides ``to_config`` / ``from_config`` and the annotation (de)serialization
    helpers. These rely on attributes supplied by the concrete chart class
    (``_width``, ``_height``, ``_title``, ``data_model``, ``series_styles`` and
    others); they are declared here only for type checking.
    """

    if TYPE_CHECKING:
        _width: float
        _height: float
        _title: MeasuredText | None
        series_names: list[str] | None
        series_styles: list[SeriesStyleConfig] | None
        x_stacked: bool
        zero_index: bool
        data_model: DataModel
        _h_lines: list[float] | None
        _v_lines: list[float] | None
        _annotations: list[_Annotation]

        @property
        def x_labels(self) -> list[MeasuredText] | None: ...

        @property
        def x_scale(self) -> str: ...

        @property
        def y_scale(self) -> str: ...

    def to_config(self) -> dict[str, object]:
        """Serialize chart configuration to a dict.

        Returns a dict with all constructor parameters needed to
        recreate the chart, plus theme info.

        Returns:
            Dict suitable for JSON serialization or agent workflows.
        """
        import dataclasses

        cfg: dict[str, object] = {
            "chart_type": self.__class__.__name__,
            "width": self._width,
            "height": self._height,
            "title": self._title.text if self._title else None,
            "labels": [
                label.text if hasattr(label, "text") else str(label)
                for label in (self.x_labels or [])
            ],
            "series_names": self.series_names,
            "x_stacked": self.x_stacked,
            "zero_index": self.zero_index,
            "x_scale": self.x_scale,
            "y_scale": self.y_scale,
        }
        if self.data_model:
            cfg["x_data"] = self.data_model.x_data
            cfg["y_data"] = self.data_model.y_data
        if self.series_styles:
            cfg["series_styles"] = [
                dataclasses.asdict(s) if dataclasses.is_dataclass(s) else s
                for s in self.series_styles
            ]
        if self._h_lines:
            cfg["h_lines"] = list(self._h_lines)
        if self._v_lines:
            cfg["v_lines"] = list(self._v_lines)
        if self._annotations:
            cfg["annotations"] = [
                self._serialize_annotation(a) for a in self._annotations
            ]
        # Line/area charts carry a curve-interpolation setting.
        if hasattr(self, "curve"):
            cfg["curve"] = self.curve
        return cfg

    @staticmethod
    def _serialize_annotation(a: object) -> object:
        """Serialize one annotation to a JSON-friendly dict.

        Tags the dict with its class name and strips private ``_ref_*`` fields
        (used only for legacy reference-line markup) so they neither leak nor
        break reconstruction in ``from_config``.
        """
        import dataclasses

        if not dataclasses.is_dataclass(a) or isinstance(a, type):
            return a
        data = {k: v for k, v in dataclasses.asdict(a).items() if not k.startswith("_")}
        return {"type": a.__class__.__name__, **data}

    @classmethod
    def from_config(cls, config: dict[str, object], **overrides: object) -> "Chart":
        """Recreate a chart from a config dict.

        Merges ``overrides`` on top of ``config`` so agents can tweak
        individual parameters without rebuilding the whole dict.

        Args:
            config: Dict returned by ``to_config()``.
            **overrides: Override any config key.

        Returns:
            Chart instance of the appropriate subclass.
        """
        import inspect

        from charted.charts import _CHART_CLASSES

        merged = dict(config)
        merged.update(overrides)

        # Reconstruct annotation objects from their serialized dict form.
        # to_config() emits each annotation as {"type": <ClassName>, **asdict(a)}.
        raw_annotations = merged.get("annotations")
        if isinstance(raw_annotations, list):
            merged["annotations"] = cls._rebuild_annotations(raw_annotations)

        chart_type = merged.pop("chart_type", None)
        cls_map = _CHART_CLASSES()
        chart_cls = cls_map.get(chart_type, cls) if isinstance(chart_type, str) else cls
        if chart_cls is None:
            chart_cls = cls

        # Only pass keys the target chart class accepts
        sig = inspect.signature(chart_cls.__init__)
        valid_params = set(sig.parameters.keys()) - {"self"}
        filtered = {k: v for k, v in merged.items() if k in valid_params}

        # Map common aliases: y_data -> data, x_data -> x_data
        if "data" in valid_params and "data" not in filtered:
            if "y_data" in merged:
                filtered["data"] = merged["y_data"]
            elif "x_data" in merged:
                filtered["data"] = merged["x_data"]
        if "y_data" in valid_params and "y_data" not in filtered and "data" in merged:
            filtered["y_data"] = merged["data"]

        # ``filtered`` is a deserialised config whose values are statically
        # ``object``; they are dispatched into the resolved subclass constructor
        # at runtime after being filtered to that constructor's parameters.
        # ``chart_cls`` is resolved from ``_CHART_CLASSES`` (always ``type[Chart]``)
        # or falls back to ``cls``; the cast restores the concrete ``Chart`` type.
        return cast("Chart", chart_cls(**filtered))

    @staticmethod
    def _rebuild_annotations(annotations: list[object]) -> list[object]:
        """Reconstruct annotation objects from their serialized dict form.

        ``to_config()`` serializes each annotation as
        ``{"type": <ClassName>, **dataclasses.asdict(a)}``. This rebuilds the
        concrete annotation object by dispatching on the ``"type"`` field.

        Handles the round-trip quirks:
        - Private ``_ref_*`` fields are stripped so they neither leak into a
          public reconstruction nor break the dataclass constructor.
        - JSON turns tuples into lists, so point/range fields are coerced back
          to tuples.
        """
        from charted.charts.annotations import (
            BoxAnnotation,
            LabelAnnotation,
            LineAnnotation,
        )

        type_map = {
            "LineAnnotation": LineAnnotation,
            "BoxAnnotation": BoxAnnotation,
            "LabelAnnotation": LabelAnnotation,
        }
        # Fields that are (x, y) / (min, max) pairs and must be tuples.
        tuple_fields = {"start", "end", "x_range", "y_range", "point"}

        rebuilt: list[object] = []
        for a in annotations:
            # Already an annotation object (not a serialized dict): keep as-is.
            if not isinstance(a, dict):
                rebuilt.append(a)
                continue

            data: dict[str, object] = {str(k): v for k, v in a.items()}
            type_name = data.pop("type", None)
            ann_cls = type_map.get(type_name) if isinstance(type_name, str) else None
            if ann_cls is None:
                # Unknown type: leave the raw dict untouched rather than guess.
                rebuilt.append(a)
                continue

            # Strip private fields so they don't leak or break reconstruction.
            data = {k: v for k, v in data.items() if not k.startswith("_")}
            # Coerce JSON lists back to tuples for coordinate pairs.
            for key in tuple_fields:
                value = data.get(key)
                if isinstance(value, list):
                    data[key] = tuple(value)

            rebuilt.append(ann_cls(**data))
        return rebuilt
