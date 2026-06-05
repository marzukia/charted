"""Value-label methods for charts.

Extracted from the :class:`~charted.charts.chart.Chart` base class to reduce
its size. The methods are unchanged; they are mixed back into ``Chart`` via
the class bases, so they continue to operate on the same ``self``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from charted.html.element import G, Text

if TYPE_CHECKING:
    from charted.charts.axes import YAxis
    from charted.themes.core import Theme
    from charted.utils.types import (
        ValueLabelConfig,
        ValueLabelOptions,
        Vector2D,
    )


class ChartValueLabelMixin:
    """Opt-in formatted value-label behavior for :class:`Chart`.

    Normalizes the ``value_labels`` argument, synthesizes formatted label
    strings from the raw data, and renders data labels onto data points. These
    rely on attributes supplied by the concrete chart class; they are declared
    here only for type checking.
    """

    if TYPE_CHECKING:
        _value_label_config: ValueLabelConfig | None
        _data_labels: list[str] | list[list[str]] | None
        theme: Theme
        y_axis: YAxis

        @property
        def x_offset(self) -> float: ...

        @property
        def plot_width(self) -> float: ...

        @property
        def plot_height(self) -> float: ...

        @property
        def y_data(self) -> Vector2D: ...

        @property
        def y_values(self) -> Vector2D: ...

        @property
        def y_offsets(self) -> Vector2D: ...

        @property
        def x_values(self) -> Vector2D: ...

        @property
        def colors(self) -> list[str]: ...

        def _apply_stacking(self, y: float, y_offset: float) -> float: ...

    @staticmethod
    def _normalize_value_labels(
        spec: bool | str | dict[str, object] | None,
    ) -> ValueLabelConfig | None:
        """Coerce the ``value_labels`` argument into a config dict or None.

        Accepted forms:
        - ``None`` / ``False``: feature off (returns None).
        - ``True``: on with the default ``"number"`` format.
        - a format string (``"number"`` / ``"percent"`` / ``"currency"``).
        - a dict, e.g. ``{"format": "currency", "decimals": 2, "prefix": "US"}``.
          A ``"format"`` key chooses the format; all other keys are passed
          straight through to ``format_value`` as keyword options.

        Foot-gun: the ``"percent"`` shorthand (and the dict form without an
        explicit ``percent_scale``) defaults to ``percent_scale=True``, which
        multiplies the raw value by 100 (``0.4`` -> ``"40%"``). That default
        suits fractional data. If your data is *already* expressed in percent
        units (``40`` meaning 40%), pass the dict form
        ``{"format": "percent", "percent_scale": False}`` so the value renders
        as ``"40%"`` rather than ``"4000%"``. The library cannot infer the
        scale of arbitrary numbers, so the caller must say which one applies.
        """
        if spec is None or spec is False:
            return None
        if spec is True:
            return {"format": "number"}
        if isinstance(spec, str):
            return {"format": spec}
        if isinstance(spec, dict):
            cfg: ValueLabelConfig = cast("ValueLabelConfig", dict(spec))
            cfg.setdefault("format", "number")
            return cfg
        raise TypeError(
            "value_labels must be None, a bool, a format string, or a dict; "
            f"got {type(spec).__name__}"
        )

    def _value_label_data(self) -> Vector2D:
        """Return the raw per-series values that value labels annotate.

        Defaults to ``y_data``. Charts whose value axis is X (horizontal bars)
        or whose data lives elsewhere (pie) override this.
        """
        return self.y_data

    def _build_value_labels(self) -> list[list[str]] | None:
        """Synthesize formatted label strings from the chart's raw values.

        Returns a 2D list mirroring the value-data shape, or None when value
        labels are disabled. Used by ``_render_data_labels`` as the label source
        when no explicit ``data_labels`` were supplied.
        """
        cfg = self._value_label_config
        if not cfg:
            return None
        from charted.utils.value_format import format_value

        opts = cast(
            "ValueLabelOptions",
            {k: v for k, v in cfg.items() if k != "format"},
        )
        fmt = cfg["format"]
        data = self._value_label_data()
        return [[format_value(v, fmt, **opts) for v in row] for row in data]

    @property
    def _data_label_x_offset(self) -> float:
        return 0

    @property
    def _data_labels_use_contrast(self) -> bool:
        return False

    def _render_data_labels(self) -> G | None:
        """Render data labels on data points.

        Returns a G element with text labels positioned at each data point.
        Subclasses call this from their representation property.

        When no explicit ``data_labels`` are supplied but ``value_labels`` is
        enabled, the labels are synthesized from the raw data with the requested
        number/percent/currency formatting, and any label whose box would
        collide with an already-placed one is hidden.
        """
        from charted.utils.colors import get_contrast_color

        labels = self._data_labels
        auto_hide = False
        if not labels:
            labels = self._build_value_labels()
            auto_hide = labels is not None
        if not labels:
            return None

        # Normalize to 2D list
        if labels and not isinstance(labels[0], list):
            labels = [labels]

        g = G()
        font_size = max(8, self.theme.title_font_size - 4)
        font_family = self.theme.title_font_family
        font_color = self.theme.resolved_data_label_color

        # Track placed label boxes (in plot coordinates) so value labels can be
        # auto-hidden when they would collide with an already-placed label.
        placed_boxes: list[tuple[float, float, float, float]] = []

        from charted.utils.helpers import calculate_text_dimensions

        for series_idx, label_row in enumerate(labels):
            if series_idx >= len(self.y_values):
                break
            y_vals = self.y_values[series_idx]
            y_offs = self.y_offsets[series_idx]
            x_vals = self.x_values[series_idx]
            series_color = (
                self.colors[series_idx] if series_idx < len(self.colors) else None
            )

            for i, label_text in enumerate(label_row):
                if i >= len(x_vals) or not label_text:
                    continue
                x = x_vals[i] + self.x_offset + self._data_label_x_offset
                y = self._apply_stacking(y_vals[i], y_offs[i])
                label_offset = font_size + 4
                if y_vals[i] < 0:
                    ty = y + label_offset + font_size
                else:
                    ty = y - label_offset
                anchor = "middle"
                # Clamp labels that would go off-chart vertically
                if ty < font_size:
                    ty = y + label_offset + font_size
                if ty > self.plot_height - font_size:
                    ty = y - label_offset
                # Detect if label is inside the bar/column area
                inside = self._data_labels_use_contrast and (
                    (y_vals[i] >= 0 and 0 < ty < y) or (y_vals[i] < 0 and y < ty < 0)
                )
                # Nudge label away from grid lines for breathing room
                grid_margin = font_size * 0.6
                if hasattr(self, "y_axis"):
                    for tick_y in self.y_axis.coordinates:
                        if abs(ty - tick_y) < grid_margin:
                            ty = (
                                tick_y - grid_margin
                                if ty > tick_y
                                else tick_y + grid_margin
                            )
                            break
                # Use contrast-aware color when label is inside a colored area
                fill = font_color
                if inside and series_color:
                    fill = get_contrast_color(series_color)
                # Clamp labels at horizontal edges
                if x > self.plot_width * 0.85:
                    anchor = "end"
                elif x < self.plot_width * 0.15:
                    anchor = "start"
                # Auto-hide synthesized value labels that would overlap an
                # already-placed one. Explicit data_labels are left untouched so
                # historical renders stay byte-for-byte identical.
                if auto_hide:
                    tw = calculate_text_dimensions(
                        str(label_text), font=font_family, font_size=font_size
                    ).width
                    box = (
                        x - tw / 2,
                        ty - font_size / 2,
                        x + tw / 2,
                        ty + font_size / 2,
                    )
                    if any(
                        box[0] < pb[2]
                        and box[2] > pb[0]
                        and box[1] < pb[3]
                        and box[3] > pb[1]
                        for pb in placed_boxes
                    ):
                        continue
                    placed_boxes.append(box)
                g.add_child(
                    Text(
                        text=str(label_text),
                        x=x,
                        y=ty,
                        fill=fill,
                        font_size=font_size,
                        font_family=font_family,
                        text_anchor=anchor,
                        transform=f"translate({x},{ty}) scale(1,-1) translate({-x},{-ty})",
                    )
                )

        return g
