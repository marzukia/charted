from __future__ import annotations

import math
from typing import TypedDict, cast

from charted.charts.chart import Chart
from charted.constants import (
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
    QUADRANT_BOTTOM_MARGIN_FACTOR,
    QUADRANT_LABEL_LINE_GAP,
)
from charted.html.element import Circle, Element, G, Path, Rect, Text
from charted.themes.core import Theme
from charted.utils.types import (
    PointStyleConfig,
    SeriesStyleConfig,
    Vector,
    Vector2D,
)


class _PlacedLabel(TypedDict):
    """A data label's placement state during collision avoidance."""

    text: str
    px: float
    py: float
    cx: float
    cy: float
    w: float
    h: float
    marker: float


class ScatterChart(Chart):
    """Scatter plot for displaying relationships between two variables.

    Plots individual data points at (x, y) coordinates to show
    correlations, clusters, or distributions. Supports multi-series
    data with custom marker shapes and sizes.

    Args:
        data: Single series (list of y-values with x=indices) or
              multi-series (list of lists) or list of (x, y) tuples
        x_data: Optional x-coordinates for each point
        labels: Optional series names
        width, height: Chart dimensions in pixels
        zero_index: Whether to include zero in both axes
        title: Optional chart title
        theme: Optional theme configuration
        series_names: Names for each series (shown in legend)
        series_styles: Per-series style overrides (marker_shape, marker_size)
        point_styles: Per-POINT marker overrides, a list of per-series rows
            mirroring the data shape. Each entry is a ``PointStyleConfig``
            (``marker_shape``, ``marker_size``, ``fill``, ``opacity``) or
            ``None``. Any present field wins over the series-level/shape-cycle
            resolution; omitted fields fall through. Defaults to None, leaving
            every point styled by its series (existing behaviour). Data-label
            colour now comes from the theme's ``data_label_color`` token
            (override via ``Theme(data_label_color=...)``); the default token
            reproduces the previous axis-title colour.
        x_range: Optional (min, max) to fix the x-axis domain instead of
            deriving it from the data, removing the need for invisible anchor
            points to control the visible range.
        y_range: Optional (min, max) to fix the y-axis domain.
        domain_padding: Optional fraction (e.g. 0.1) padding the data-derived
            domain by that amount on each side. Ignored on an axis with an
            explicit range. Defaults to None (no padding).
        quadrant_label_inset: Extra padding (px) used to inset the four
            quadrant labels from the plot corners so they clear the axis tick
            numbers instead of sitting flush. Defaults to 12.0; pass 0 to
            restore the original flush-corner placement.
        quadrant_label_backplate: When True, draws a semi-opaque rounded
            background plate behind each quadrant label for contrast. Defaults
            to False.
        shape_cycle: Redundant shape encoding for multi-series scatters so
            series differ by marker SHAPE as well as colour. Defaults to None
            (every series uses circles, preserving existing behaviour). Pass
            True to enable the built-in cycle
            (circle, square, triangle, diamond, star), or a custom list of
            shape names to cycle through. A per-series ``marker_shape`` in
            ``series_styles`` always wins over the cycle.
        legend: Placement for a series legend that maps each ``series_names``
            entry to its marker shape and colour swatch. One of ``'none'``
            (default, no legend), ``'right'``, ``'bottom'``, or ``'top'``.
            When shown, layout space is reserved on that side so the legend
            never overlaps the plot. Requires ``series_names``; with no names
            there is nothing to label and the layout is left unchanged.
        avoid_label_collisions: When True, run a collision-avoidance pass over
            the data labels so they overlap each other (and their markers) as
            little as possible, drawing a thin leader line back to a point
            whenever its label is pushed noticeably away. Defaults to False,
            which keeps the original fixed-offset label placement so existing
            renders are unchanged. See ``_render_data_labels`` for the
            algorithm and its limitations.

    Example:
        >>> from charted import ScatterChart
        >>> # Basic scatter plot
        >>> chart = ScatterChart(data=[5, 8, 12, 15], x_data=[1, 2, 3, 4])
        >>> chart.save('correlation.svg')
        >>>
        >>> # Multi-series with custom markers
        >>> chart = ScatterChart(
        ...     data=[[5, 8, 12], [7, 10, 14]],
        ...     x_data=[1, 2, 3],
        ...     series_styles=[{'marker_shape': 'circle'}, {'marker_shape': 'square'}]
        ... )
    """

    # Default marker shapes cycled for redundant (shape + colour) encoding
    # when ``shape_cycle=True`` and no per-series shape is given.
    DEFAULT_SHAPE_CYCLE = ["circle", "square", "triangle", "diamond", "star"]

    @staticmethod
    def _resolve_shape_cycle(
        shape_cycle: list[str] | bool | None,
    ) -> list[str] | None:
        """Normalise the ``shape_cycle`` argument to a list of shapes or None.

        None/False disable cycling (every series uses circles). True selects
        the built-in cycle. A non-empty list is used verbatim.
        """
        if shape_cycle is None or shape_cycle is False:
            return None
        if shape_cycle is True:
            return list(ScatterChart.DEFAULT_SHAPE_CYCLE)
        if isinstance(shape_cycle, list) and shape_cycle:
            return list(shape_cycle)
        return None

    def __init__(
        self,
        x_data: Vector | Vector2D,
        y_data: Vector | Vector2D,
        width: float = DEFAULT_CHART_WIDTH,
        height: float = DEFAULT_CHART_HEIGHT,
        title: str | None = None,
        subtitle: str | None = None,
        subtitle_leading: float = 8.0,
        theme: Theme | None = None,
        series_names: list[str] | None = None,
        series_styles: list[SeriesStyleConfig] | None = None,
        point_styles: list[list[PointStyleConfig | None]] | None = None,
        data_labels: list[str] | list[list[str]] | None = None,
        x_label: str | None = None,
        y_label: str | None = None,
        h_lines: list[float] | None = None,
        v_lines: list[float] | None = None,
        annotations: list[object] | None = None,
        quadrant_labels: list[str] | None = None,
        quadrant_label_inset: float = 12.0,
        quadrant_label_backplate: bool = False,
        shape_cycle: list[str] | bool | None = None,
        legend: str = "none",
        x_scale: object | None = None,
        y_scale: object | None = None,
        reference_lines: list[dict[str, object]] | None = None,
        colors: list[str] | None = None,
        x_range: tuple[float, float] | None = None,
        y_range: tuple[float, float] | None = None,
        domain_padding: float | None = None,
        avoid_label_collisions: bool = False,
        value_labels: bool | str | dict[str, object] | None = None,
    ):
        self._avoid_label_collisions = avoid_label_collisions
        self._point_styles = point_styles
        self._quadrant_labels = quadrant_labels
        self._quadrant_label_inset = quadrant_label_inset
        self._quadrant_label_backplate = quadrant_label_backplate
        self._shape_cycle = self._resolve_shape_cycle(shape_cycle)
        super().__init__(
            y_data=y_data,
            x_data=x_data,
            width=width,
            height=height,
            title=title,
            subtitle=subtitle,
            subtitle_leading=subtitle_leading,
            theme=theme,
            series_names=series_names,
            chart_type="scatter",
            series_styles=series_styles,
            data_labels=data_labels,
            x_label=x_label,
            y_label=y_label,
            h_lines=h_lines,
            v_lines=v_lines,
            annotations=annotations,
            x_scale=x_scale,
            y_scale=y_scale,
            reference_lines=reference_lines,
            colors=colors,
            x_range=x_range,
            y_range=y_range,
            domain_padding=domain_padding,
            value_labels=value_labels,
            legend=legend,
        )

    # =====================================================================
    # Legend (shape + colour mapping, reserved placement)
    # =====================================================================

    def _legend_entries(self) -> list[tuple[str, str, str]]:
        """Build (name, colour, shape) tuples for each plotted series.

        Returns an empty list when there are no series names to label, which
        is what keeps the legend off by default for unnamed scatters.
        """
        names = self.series_names
        if not names:
            return []
        entries: list[tuple[str, str, str]] = []
        for idx, name in enumerate(names):
            if idx >= len(self.y_values):
                break
            color = self.colors[idx] if idx < len(self.colors) else "#000000"
            shape = self._series_shape(idx)
            entries.append((str(name), color, shape))
        return entries

    def _series_shape(self, series_idx: int) -> str:
        """Resolve the marker shape for a series (mirrors ``representation``)."""
        if self._shape_cycle:
            shape = self._shape_cycle[series_idx % len(self._shape_cycle)]
        else:
            shape = "circle"
        if self.series_styles and series_idx < len(self.series_styles):
            style = self.series_styles[series_idx] or {}
            if style.get("marker_shape"):
                shape = cast(str, style["marker_shape"])
        return shape

    @property
    def representation(self) -> G:
        g = G(
            opacity=0.8,
            transform=[*self.get_base_transform()],
            clip_path="url(#plot-clip)",
        )
        for series_idx, (y_values, y_offsets, x_values, color) in enumerate(
            zip(self.y_values, self.y_offsets, self.x_values, self.colors),
        ):
            # Apply style overrides from series_styles
            fill = color
            # Default marker size is 4px. A theme that explicitly sets
            # marker_size (e.g. high-contrast) raises it for legibility while
            # the standard themes keep the historical 4px.
            marker_size: float = 4
            if self.theme._is_explicit("marker_size"):
                marker_size = self.theme.marker_size
            # Default shape is a circle; with shape_cycle enabled, each series
            # picks a shape from the cycle (redundant shape + colour encoding).
            if self._shape_cycle:
                marker_shape = self._shape_cycle[series_idx % len(self._shape_cycle)]
            else:
                marker_shape = "circle"
            if self.series_styles and series_idx < len(self.series_styles):
                style = self.series_styles[series_idx] or {}
                if style.get("fill"):
                    fill = cast(str, style["fill"])
                if style.get("marker_size"):
                    marker_size = cast(float, style["marker_size"])
                if style.get("marker_shape"):
                    marker_shape = cast(str, style["marker_shape"])

            series = G(fill=fill)
            x_offset = self.x_offset

            for i, (x, y, y_offset) in enumerate(zip(x_values, y_values, y_offsets)):
                x += x_offset
                y = self._apply_stacking(y, y_offset)
                title = self._tooltip_title(series_idx, i)
                # Per-point overrides (point_styles) win over the series-level
                # shape/size/fill resolved above. Each field is independent, so
                # an omitted field keeps the series value.
                p_shape = marker_shape
                p_size = marker_size
                p_fill = fill
                p_opacity: float | None = None
                pstyle = self._point_style(series_idx, i)
                if pstyle:
                    if pstyle.get("marker_shape"):
                        p_shape = cast(str, pstyle["marker_shape"])
                    if pstyle.get("marker_size"):
                        p_size = cast(float, pstyle["marker_size"])
                    if pstyle.get("fill"):
                        p_fill = cast(str, pstyle["fill"])
                    if pstyle.get("opacity") is not None:
                        p_opacity = pstyle["opacity"]
                mark = self._marker_element(p_shape, x, y, p_size, p_fill)
                if mark is not None:
                    # Only set fill on the marker when it differs from the
                    # series group fill, so unstyled points stay byte-identical
                    # (they inherit fill from the enclosing group).
                    if p_fill != fill:
                        mark.kwargs["fill"] = p_fill
                    if p_opacity is not None:
                        mark.kwargs["opacity"] = cast(str, p_opacity)
                    if title is not None:
                        mark.add_child(title)
                    series.add_child(mark)
            g.add_children(series)

        # Data labels and quadrant labels rendered outside the clip group
        # so they don't get clipped at chart edges
        wrapper = G()
        wrapper.add_child(g)

        data_labels_g = self._render_data_labels()
        if data_labels_g:
            unclipped = G(
                transform=[*self.get_base_transform()],
            )
            unclipped.add_child(data_labels_g)
            wrapper.add_child(unclipped)

        quadrant_g = self._render_quadrant_labels()
        if quadrant_g:
            unclipped_q = G(
                transform=[*self.get_base_transform()],
            )
            unclipped_q.add_child(quadrant_g)
            wrapper.add_child(unclipped_q)

        return wrapper

    def _point_style(self, series_idx: int, point_idx: int) -> PointStyleConfig | None:
        """Return the ``PointStyleConfig`` for one point, or None.

        ``point_styles`` is a list of per-series rows mirroring the data shape;
        any missing series, point, or ``None`` entry yields no override.
        """
        styles = self._point_styles
        if not styles or series_idx >= len(styles):
            return None
        row = styles[series_idx]
        if not row or point_idx >= len(row):
            return None
        return row[point_idx] or None

    def _marker_element(
        self, shape: str, x: float, y: float, size: float, fill: str
    ) -> Element | None:
        """Build a marker element centred at (x, y).

        ``size`` is the radius / half-extent, so every shape shares the same
        bounding box for a given size (a square, circle, diamond, triangle and
        star with the same ``size`` all fit the same 2*size box). Returns None
        for shape ``"none"``.
        """
        if shape == "none":
            return None
        if shape == "square":
            return Rect(x=x - size, y=y - size, width=size * 2, height=size * 2)
        if shape == "diamond":
            pts = f"{x},{y - size} {x + size},{y} {x},{y + size} {x - size},{y}"
            return Path(d=f"M{pts} Z", fill=fill)
        if shape == "triangle":
            pts = self._polygon_points(x, y, size, sides=3)
            return Path(d=f"M{pts} Z", fill=fill)
        if shape == "star":
            pts = self._star_points(x, y, size)
            return Path(d=f"M{pts} Z", fill=fill)
        # default: circle
        return Circle(cx=x, cy=y, r=size)

    # The plot group is rendered with a net vertical flip (see
    # LayoutEngine.get_base_transform), so a vertex placed at the bottom in
    # local space appears at the top on screen. The +90 start angle therefore
    # makes the apex/first tip point UP for the viewer.
    @staticmethod
    def _polygon_points(cx: float, cy: float, r: float, sides: int) -> str:
        """Vertices of a regular polygon, apex pointing up on screen."""
        out = []
        for k in range(sides):
            a = math.radians(90 + k * 360 / sides)
            out.append(f"{cx + r * math.cos(a):.3f},{cy + r * math.sin(a):.3f}")
        return " ".join(out)

    @staticmethod
    def _star_points(
        cx: float, cy: float, r: float, points: int = 5, inner_ratio: float = 0.4
    ) -> str:
        """Vertices of a star with ``points`` tips, first tip up on screen."""
        inner = r * inner_ratio
        out = []
        for k in range(points * 2):
            radius = r if k % 2 == 0 else inner
            a = math.radians(90 + k * 180 / points)
            out.append(
                f"{cx + radius * math.cos(a):.3f},{cy + radius * math.sin(a):.3f}"
            )
        return " ".join(out)

    def _render_data_labels(self) -> G | None:
        """Render scatter data labels, optionally de-overlapping them.

        With ``avoid_label_collisions=False`` (the default) this defers to the
        base-class placement so existing renders are byte-for-byte unchanged.

        With it enabled, every label starts at a fixed offset above-right of its
        marker, then a greedy iterative pass nudges labels apart whenever their
        axis-aligned bounding boxes overlap another label or a marker. When a
        label ends up displaced far enough from its point a thin leader line is
        drawn back to the marker so the association stays readable.

        Limitations: the de-overlap is a local greedy relaxation, not a global
        optimiser, so dense clusters can still leave some residual overlap and
        the result depends on point order. Label widths are estimated from the
        font metrics helper (no real text shaping), labels are not clamped to
        the plot rectangle, and rotated/multi-line labels are not handled.
        Markers are approximated by their square bounding box.
        """
        if not getattr(self, "_avoid_label_collisions", False):
            return super()._render_data_labels()
        if not self._data_labels:
            return None

        labels = self._data_labels
        if labels and not isinstance(labels[0], list):
            labels = [labels]

        from charted.utils.helpers import calculate_text_dimensions

        font_size = max(8, self.theme.title_font_size - 4)
        font_family = self.theme.title_font_family
        font_color = self.theme.resolved_data_label_color
        line_color = self.theme.resolved_reference_line_color

        # Gather placed labels and their anchor markers in plot coordinates.
        placed: list[_PlacedLabel] = []
        for series_idx, label_row in enumerate(labels):
            if series_idx >= len(self.y_values):
                break
            y_vals = self.y_values[series_idx]
            y_offs = self.y_offsets[series_idx]
            x_vals = self.x_values[series_idx]
            marker_size = 4.0
            if self.series_styles and series_idx < len(self.series_styles):
                style = self.series_styles[series_idx] or {}
                if style.get("marker_size"):
                    marker_size = float(cast(float, style["marker_size"]))
            for i, label_text in enumerate(label_row):
                if i >= len(x_vals) or not label_text:
                    continue
                px = x_vals[i] + self.x_offset
                py = self._apply_stacking(y_vals[i], y_offs[i])
                text = str(label_text)
                tw = calculate_text_dimensions(text, font_size=font_size).width
                th = font_size
                # Initial offset: up and to the right of the marker.
                off = marker_size + th * 0.5
                cx = px + off + tw / 2
                cy = py + off + th / 2
                placed.append(
                    {
                        "text": text,
                        "px": px,
                        "py": py,
                        "cx": cx,
                        "cy": cy,
                        "w": tw,
                        "h": th,
                        "marker": marker_size,
                    }
                )

        if not placed:
            return None

        self._deoverlap_labels(placed)

        g = G()
        # Leader lines first so labels render on top.
        threshold = font_size * 1.6
        for lab in placed:
            dx = lab["cx"] - lab["px"]
            dy = lab["cy"] - lab["py"]
            if (dx * dx + dy * dy) ** 0.5 > threshold:
                g.add_child(
                    Path(
                        d=f"M{lab['px']:.2f},{lab['py']:.2f} "
                        f"L{lab['cx']:.2f},{lab['cy']:.2f}",
                        stroke=line_color,
                        stroke_width=1,
                        fill="none",
                    )
                )
        for lab in placed:
            tx = lab["cx"]
            ty = lab["cy"]
            g.add_child(
                Text(
                    text=lab["text"],
                    x=tx,
                    y=ty,
                    fill=font_color,
                    font_size=font_size,
                    font_family=font_family,
                    text_anchor="middle",
                    transform=f"translate({tx},{ty}) scale(1,-1) translate({-tx},{-ty})",
                )
            )
        return g

    @staticmethod
    def _deoverlap_labels(placed: list[_PlacedLabel], iterations: int = 60) -> None:
        """Greedily push overlapping label boxes apart, in place.

        Each iteration walks every label pair plus every label/marker pair and,
        for any overlapping axis-aligned boxes, shifts the label along the axis
        of least penetration. A small spring pulls each label back toward its
        own marker so labels do not drift indefinitely. This is a local
        heuristic with no global guarantee (see ``_render_data_labels``).
        """

        def overlap(
            a_cx: float,
            a_cy: float,
            a_w: float,
            a_h: float,
            b_cx: float,
            b_cy: float,
            b_w: float,
            b_h: float,
            pad: float = 2.0,
        ) -> tuple[float, float] | None:
            ox = (a_w + b_w) / 2 + pad - abs(a_cx - b_cx)
            oy = (a_h + b_h) / 2 + pad - abs(a_cy - b_cy)
            if ox > 0 and oy > 0:
                return ox, oy
            return None

        for _ in range(iterations):
            moved = False
            for i, a in enumerate(placed):
                # Label vs every other label.
                for b in placed[i + 1 :]:
                    res = overlap(
                        a["cx"],
                        a["cy"],
                        a["w"],
                        a["h"],
                        b["cx"],
                        b["cy"],
                        b["w"],
                        b["h"],
                    )
                    if res is None:
                        continue
                    ox, oy = res
                    moved = True
                    if ox < oy:
                        shift = ox / 2 + 0.1
                        sign = 1 if a["cx"] >= b["cx"] else -1
                        a["cx"] += sign * shift
                        b["cx"] -= sign * shift
                    else:
                        shift = oy / 2 + 0.1
                        sign = 1 if a["cy"] >= b["cy"] else -1
                        a["cy"] += sign * shift
                        b["cy"] -= sign * shift
                # Label vs markers (approximated by their bounding box).
                for b in placed:
                    m = b["marker"] * 2
                    res = overlap(
                        a["cx"],
                        a["cy"],
                        a["w"],
                        a["h"],
                        b["px"],
                        b["py"],
                        m,
                        m,
                    )
                    if res is None:
                        continue
                    ox, oy = res
                    moved = True
                    if ox < oy:
                        sign = 1 if a["cx"] >= b["px"] else -1
                        a["cx"] += sign * (ox + 0.1)
                    else:
                        sign = 1 if a["cy"] >= b["py"] else -1
                        a["cy"] += sign * (oy + 0.1)
            # Weak spring back toward the marker keeps labels from wandering.
            for a in placed:
                a["cx"] += (a["px"] - a["cx"]) * 0.01
                a["cy"] += (a["py"] - a["cy"]) * 0.01
            if not moved:
                break

    def _render_quadrant_labels(self) -> G | None:
        """Render text labels in each quadrant of the scatter plot.

        Expects a list of 4 strings: [top-left, top-right, bottom-left, bottom-right].
        Each string may contain newlines for multi-line labels.
        """
        if not self._quadrant_labels:
            return None

        labels = self._quadrant_labels
        if len(labels) < 4:
            labels = list(labels) + [""] * (4 - len(labels))

        g = G()
        font_size = max(8, self.theme.title_font_size - 4)
        font_family = self.theme.title_font_family
        font_color = self.theme.resolved_quadrant_label_color
        pw = self.plot_width
        ph = self.plot_height
        # Inset the labels away from the plot edge so they clear the axis
        # tick numbers instead of sitting flush in the corner. The inset is
        # added on top of the base corner pad.
        inset = max(0.0, float(self._quadrant_label_inset))
        padding = 8 + inset

        # In the flipped coordinate system, high Y = top of chart
        # Corner-aligned: top labels hug top edge growing down,
        # bottom labels hug bottom edge growing up
        line_height = font_size + QUADRANT_LABEL_LINE_GAP
        top_margin = padding + font_size
        bottom_margin = padding * QUADRANT_BOTTOM_MARGIN_FACTOR

        for idx, label_text in enumerate(labels):
            if not label_text:
                continue
            lines = str(label_text).split("\n")
            is_left = idx % 2 == 0
            is_top = idx < 2
            anchor = "start" if is_left else "end"
            x = padding if is_left else pw - padding

            if self._quadrant_label_backplate:
                backplate = self._quadrant_backplate(
                    lines,
                    x,
                    anchor,
                    is_top,
                    font_size,
                    line_height,
                    top_margin,
                    bottom_margin,
                    ph,
                )
                if backplate is not None:
                    g.add_child(backplate)

            for line_idx, line in enumerate(lines):
                if is_top:
                    ty = ph - top_margin - line_idx * line_height
                else:
                    ty = (
                        bottom_margin
                        + font_size
                        + (len(lines) - 1 - line_idx) * line_height
                    )
                g.add_child(
                    Text(
                        text=line,
                        x=x,
                        y=ty,
                        fill=font_color,
                        font_size=font_size,
                        font_family=font_family,
                        text_anchor=anchor,
                        opacity=0.8,
                        transform=f"translate({x},{ty}) scale(1,-1) translate({-x},{-ty})",
                    )
                )

        return g

    def _quadrant_backplate(
        self,
        lines: list[str],
        x: float,
        anchor: str,
        is_top: bool,
        font_size: float,
        line_height: float,
        top_margin: float,
        bottom_margin: float,
        ph: float,
    ) -> Rect | None:
        """Build a semi-opaque rounded plate sized to a quadrant label block.

        Drawn in the flipped plot coordinate system (high Y = top), so the
        plate is emitted before the text and renders behind it.
        """
        if not lines:
            return None
        pad_x = font_size * 0.5
        pad_y = font_size * 0.35
        # Width estimate is intentionally font-metric-free to stay stable
        # across environments (matches the pie chart's estimator).
        text_w = max((len(line) for line in lines), default=0) * font_size * 0.55
        if text_w <= 0:
            return None
        block_h = font_size + (len(lines) - 1) * line_height

        rect_w = text_w + pad_x * 2
        rect_h = block_h + pad_y * 2

        if anchor == "start":
            rect_x = x - pad_x
        else:
            rect_x = x - text_w - pad_x

        if is_top:
            top_baseline = ph - top_margin
            rect_y = top_baseline - font_size - pad_y
        else:
            top_baseline = bottom_margin + font_size + (len(lines) - 1) * line_height
            rect_y = top_baseline - font_size - pad_y

        return Rect(
            x=round(rect_x, 2),
            y=round(rect_y, 2),
            width=round(rect_w, 2),
            height=round(rect_h, 2),
            rx=round(font_size * 0.35, 2),
            fill=self.theme.background_color,
            opacity=0.7,
        )
