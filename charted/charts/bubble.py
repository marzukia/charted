from __future__ import annotations

from typing import Any, cast

from charted.charts.scatter import ScatterChart
from charted.constants import DEFAULT_CHART_HEIGHT, DEFAULT_CHART_WIDTH
from charted.html.element import Circle, G, Path, Text
from charted.themes.core import Theme
from charted.utils.types import SeriesStyleConfig, Vector, Vector2D

DEFAULT_BUBBLE_MIN_RADIUS = 4.0
DEFAULT_BUBBLE_MAX_RADIUS = 24.0


def _lerp_color(c1: str, c2: str, t: float) -> str:
    """Linearly interpolate between two hex colours (t in [0, 1])."""
    from charted.utils.colors import hex_to_rgb, rgb_to_hex

    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    t = max(0.0, min(1.0, t))
    return rgb_to_hex(
        (
            int(r1 + (r2 - r1) * t),
            int(g1 + (g2 - g1) * t),
            int(b1 + (b2 - b1) * t),
        )
    )


class BubbleChart(ScatterChart):
    """Bubble chart: a scatter plot where marker radius encodes a third value.

    Each point is drawn as a circle at its (x, y) position, exactly like a
    scatter plot, but the circle radius is scaled from a third data
    dimension (``sizes``) into a configurable ``[min_radius, max_radius]``
    range.

    Sizes map linearly to the circle *radius*, not its area. Because a
    circle's area grows with the square of its radius, large values look
    more than proportionally bigger than their value warrants. This is
    intentional; if you want perceived size to track value, pre-transform
    your data with ``sqrt`` before passing it as ``sizes``.

    For multi-series charts, ``sizes`` applies per point index across every
    series (``sizes[i]`` sets the radius of point ``i`` in all series), and
    its length is validated against the point count of the first series.

    Args:
        x_data: X-coordinates for each point.
        y_data: Y-coordinates for each point.
        sizes: Third dimension; one non-negative value per point. Mapped
            linearly onto ``[min_radius, max_radius]`` (radius, not area).
        min_radius: Smallest rendered marker radius in pixels.
        max_radius: Largest rendered marker radius in pixels.
        size_legend: When truthy, draws a size-scale legend in a reserved
            right-hand band: a few representative bubbles keyed to their
            ``sizes`` value so readers can decode the third dimension.
            Accepts ``True`` (or ``"right"``) to show it, ``False`` (default)
            or ``"none"`` to hide it.
        size_legend_title: Optional heading shown above the size legend.
        hue: Optional fourth dimension; one value per point. When given,
            each bubble's fill is interpolated across ``hue_colors`` by its
            hue value, and a hue colorbar is added beneath the size legend.
            Applies per point index across every series (like ``sizes``).
        hue_colors: ``(low, high)`` hex colours for the hue gradient. When
            omitted, a light-to-dark ramp of the first palette colour is used.
        hue_title: Optional heading shown beside the hue colorbar.
        width, height: Chart dimensions in pixels.
        title: Optional chart title.
        theme: Optional theme configuration.
        series_names: Names for each series (shown in legend).

    Example:
        >>> from charted import BubbleChart
        >>> chart = BubbleChart(
        ...     x_data=[1, 2, 3],
        ...     y_data=[10, 20, 15],
        ...     sizes=[5, 30, 12],
        ... )
        >>> chart.save('bubble.svg')
    """

    def __init__(
        self,
        x_data: Vector | Vector2D,
        y_data: Vector | Vector2D,
        sizes: Vector,
        min_radius: float = DEFAULT_BUBBLE_MIN_RADIUS,
        max_radius: float = DEFAULT_BUBBLE_MAX_RADIUS,
        size_legend: bool | str = False,
        size_legend_title: str | None = None,
        hue: Vector | None = None,
        hue_colors: tuple[str, str] | None = None,
        hue_title: str | None = None,
        width: float = DEFAULT_CHART_WIDTH,
        height: float = DEFAULT_CHART_HEIGHT,
        title: str | None = None,
        theme: Theme | None = None,
        series_names: list[str] | None = None,
        series_styles: list[SeriesStyleConfig] | None = None,
        data_labels: list[str] | list[list[str]] | None = None,
        x_label: str | None = None,
        y_label: str | None = None,
        h_lines: list[float] | None = None,
        v_lines: list[float] | None = None,
        quadrant_labels: list[str] | None = None,
        value_labels: bool | str | dict[str, Any] | None = None,
        legend: str = "none",
        domain_padding: float | None = None,
    ):
        if sizes is None:
            raise ValueError("sizes is required for a bubble chart")
        if any(s < 0 for s in sizes):
            raise ValueError("sizes cannot be negative")
        if min_radius < 0 or max_radius < 0:
            raise ValueError("min_radius and max_radius cannot be negative")
        if max_radius < min_radius:
            raise ValueError("max_radius must be >= min_radius")

        # sizes applies per point index across every series, so validate it
        # against every series length, not just the first.
        is_multi_series = bool(y_data) and isinstance(y_data[0], list)
        if is_multi_series:
            series_lengths = [len(cast("list[float]", series)) for series in y_data]
        else:
            series_lengths = [len(y_data)]
        for series_idx, point_count in enumerate(series_lengths):
            if len(sizes) != point_count:
                raise ValueError(
                    f"sizes length ({len(sizes)}) must match number of points "
                    f"in series {series_idx} ({point_count}); sizes apply per "
                    f"point index across all series"
                )

        # Normalize the size-legend flag: True -> "right", False -> "none".
        if size_legend is True:
            size_legend = "right"
        elif size_legend is False:
            size_legend = "none"
        if size_legend not in ("none", "right"):
            raise ValueError(
                f"size_legend must be one of True, False, 'none', 'right'; "
                f"got {size_legend!r}"
            )

        if hue is not None:
            for point_count in series_lengths:
                if len(hue) != point_count:
                    raise ValueError(
                        f"hue length ({len(hue)}) must match the number of "
                        f"points ({point_count}); hue applies per point index "
                        f"across all series, like sizes"
                    )
            if hue_colors is not None and len(hue_colors) != 2:
                raise ValueError("hue_colors must be a (low, high) pair")

        self.sizes = list(sizes)
        self.min_radius = min_radius
        self.max_radius = max_radius
        self._size_legend = size_legend
        self._size_legend_title = size_legend_title
        self.hue = list(hue) if hue is not None else None
        self._hue_colors = tuple(hue_colors) if hue_colors is not None else None
        self._hue_title = hue_title

        # Bubble markers have a pixel radius, but the data domain is in data
        # units, so a bubble sitting on the data min/max is centred on the plot
        # edge and half of it spills outside the plot rectangle (where it gets
        # clipped). Reserve enough domain headroom that the largest bubble fits
        # inside the plot on every side. A bubble's radius is the same in pixels
        # on both axes, but each axis has its own data-to-pixel scale, so the
        # required padding fraction differs per axis; we compute and apply them
        # separately (see ``_anchor_axis_data``). An explicit ``domain_padding``
        # from the caller disables this and is honoured verbatim on both axes.
        self._bubble_auto_pad: dict[str, float] | None = None
        if domain_padding is None:
            self._bubble_auto_pad = self._radius_aware_domain_padding(
                x_data, y_data, width, height
            )

        super().__init__(
            x_data=x_data,
            y_data=y_data,
            width=width,
            height=height,
            title=title,
            theme=theme,
            series_names=series_names,
            series_styles=series_styles,
            data_labels=data_labels,
            x_label=x_label,
            y_label=y_label,
            h_lines=h_lines,
            v_lines=v_lines,
            quadrant_labels=quadrant_labels,
            value_labels=value_labels,
            legend=legend,
            domain_padding=domain_padding,
        )

    # Pixel geometry for the size / hue legend band.
    _SIZE_LEGEND_GAP = 16
    _SIZE_LEGEND_LABEL_GAP = 12
    _SIZE_LEGEND_PAD = 8
    _HUE_BAR_WIDTH = 14
    _HUE_BAR_HEIGHT = 90
    _HUE_TICK_GAP = 5

    def _legend_font_size(self) -> float:
        return self.theme.legend_font_size

    # ------------------------------------------------------------------
    # Layout reservation for the size / hue legend
    # ------------------------------------------------------------------

    def _legend_layout_position(self) -> str:
        if getattr(self, "_size_legend", "none") == "right":
            return "right"
        return super()._legend_layout_position()

    def _legend_layout_extent(self) -> float:
        if getattr(self, "_size_legend", "none") != "right":
            return super()._legend_layout_extent()
        font_size = self._legend_font_size()
        from charted.utils.helpers import calculate_text_dimensions

        def text_w(s: str) -> float:
            return calculate_text_dimensions(s, font_size=font_size).width

        # The titles ("Population (M)", "Literacy %") sit at the band start, so
        # their width competes with the WHOLE row, not with the swatch column.
        # The value/tick labels sit AFTER the swatch. Sizing the band as
        # swatch + every label (titles included) double-counts a wide title
        # against the swatch and leaves dead space to the right of the legend.
        title_w = 0.0
        if self._size_legend_title:
            title_w = max(title_w, text_w(self._size_legend_title))
        if self._hue_title:
            title_w = max(title_w, text_w(self._hue_title))

        value_labels = [format(v, "g") for v in self._size_legend_values()]
        if self.hue is not None:
            value_labels += [format(min(self.hue), "g"), format(max(self.hue), "g")]
        value_label_w = max((text_w(s) for s in value_labels), default=0.0)

        swatch = max(2 * self.max_radius, self._HUE_BAR_WIDTH)
        row_w = swatch + self._SIZE_LEGEND_LABEL_GAP + value_label_w
        content_w = max(title_w, row_w)
        return self._SIZE_LEGEND_GAP + content_w + self._SIZE_LEGEND_PAD

    def _size_legend_values(self) -> list[float]:
        """Representative size values to key in the legend (min, mid, max)."""
        if not self.sizes:
            return []
        lo = min(self.sizes)
        hi = max(self.sizes)
        if hi == lo:
            return [lo]
        return [lo, (lo + hi) / 2, hi]

    def _radius_aware_domain_padding(
        self,
        x_data: Vector | Vector2D,
        y_data: Vector | Vector2D,
        width: float,
        height: float,
    ) -> dict[str, float]:
        """Per-axis domain-padding fractions that keep edge bubbles in the plot.

        A bubble centred on a data extreme overhangs the plot edge by its
        radius (up to ``max_radius`` px), so without headroom the outermost
        bubbles are clipped by the plot boundary. We want at least
        ``max_radius`` px of empty space between the outermost data point and
        the plot edge on every side.

        ``domain_padding`` inflates an axis by a fraction ``f`` of its *data*
        span (``d_max - d_min``) on each side. The axis actually rendered also
        includes zero (``zero_index``), so the data span can be a small slice of
        the full rendered span, and an ``f`` sized against the data span yields
        far less pixel headroom than ``f`` of the rendered span would. The
        per-edge headroom in pixels is ``f * data_span / rendered_span *
        plot_dim``. Solving ``headroom >= max_radius`` gives
        ``f >= max_radius * rendered_span / (data_span * plot_dim)``.

        A bubble's radius is identical in pixels on both axes, but each axis has
        its own data-to-pixel scale, so we compute a fraction per axis rather
        than forcing one shared value (which would massively over-pad the looser
        axis). Plot dimensions are estimated from the chart size because the
        real layout is not built yet; over-reserving slightly is harmless.
        """
        if self.max_radius <= 0:
            return {"x": 0.0, "y": 0.0}

        def flat(data: Vector | Vector2D) -> list[float]:
            if data and isinstance(data[0], list):
                return [v for row in data for v in row]
            return list(cast("Vector", data)) if data else []

        # Rough plot-area estimates: title/axis chrome eats vertical space and
        # the value-axis gutter plus any reserved legend band eats horizontal
        # space. Deliberately conservative (smaller plot -> larger pad).
        plot_h = max(1.0, height - 110.0)
        plot_w = max(1.0, width - 110.0)
        if self._size_legend == "right" or self.hue is not None:
            # A right-hand legend band steals horizontal space. The exact band
            # width needs the theme (not built yet), so subtract a rough fixed
            # estimate keyed off the legend swatch size.
            plot_w = max(1.0, plot_w - (2.0 * self.max_radius + 90.0))

        def axis_fraction(values: list[float], plot_dim: float) -> float:
            if not values:
                return 0.0
            d_min, d_max = min(values), max(values)
            data_span = d_max - d_min
            if data_span <= 0:
                return 0.0
            # zero_index pulls the rendered domain to include 0 on each axis.
            rendered_span = max(d_max, 0.0) - min(d_min, 0.0)
            rendered_span = max(rendered_span, data_span)
            f = self.max_radius * rendered_span / (data_span * plot_dim)
            # The axis rounds its domain to "nice" tick values after padding,
            # which can snap the padded extreme back toward the data and swallow
            # reserved headroom. A modest safety factor keeps a clear margin so
            # the largest bubble still clears the edge after rounding. Cap each
            # axis so a pathological max_radius cannot blow the domain up.
            return min(f * 1.35, 1.0)

        return {
            "x": axis_fraction(flat(x_data), plot_w),
            "y": axis_fraction(flat(y_data), plot_h),
        }

    def _anchor_axis_data(
        self,
        data: Vector2D,
        fixed_range: tuple[float, float] | None,
        zero_baseline: bool = False,
        stacked: bool = False,
    ) -> Vector2D:
        """Apply the per-axis radius-aware pad before delegating to the base.

        When the caller passed an explicit ``domain_padding`` we leave the base
        behaviour untouched. Otherwise we temporarily install the fraction for
        the axis being anchored (identified by whether ``data`` is the chart's
        x- or y-data) so each axis reserves exactly its own bubble headroom.
        """
        auto = getattr(self, "_bubble_auto_pad", None)
        if auto is None or fixed_range is not None:
            return super()._anchor_axis_data(data, fixed_range, zero_baseline, stacked)
        if data is self.y_data:
            frac = auto.get("y", 0.0)
        elif data is self.x_data:
            frac = auto.get("x", 0.0)
        else:
            frac = 0.0
        if frac <= 0:
            return super()._anchor_axis_data(data, fixed_range, zero_baseline, stacked)
        saved = self._domain_padding
        self._domain_padding = frac
        try:
            # Pad only the side away from zero (like a zero baseline). The
            # bubbles needing headroom sit at the data extreme far from zero;
            # padding the near-zero side too would push the domain below zero on
            # all-positive data, which forces the axis onto a finer tick step
            # and clutters the gridlines. Keeping the zero side pinned preserves
            # the clean tick spacing while still clearing the outer bubbles.
            return super()._anchor_axis_data(
                data, fixed_range, zero_baseline=True, stacked=stacked
            )
        finally:
            self._domain_padding = saved

    def _radius_for_size(self, value: float) -> float:
        """Map a raw size value onto the radius range (matches _scaled_radii)."""
        lo = min(self.sizes)
        hi = max(self.sizes)
        if hi == lo:
            return (self.min_radius + self.max_radius) / 2
        span = self.max_radius - self.min_radius
        return self.min_radius + (value - lo) / (hi - lo) * span

    # ------------------------------------------------------------------
    # Hue (optional fourth dimension)
    # ------------------------------------------------------------------

    def _hue_endpoints(self) -> tuple[str, str]:
        """Resolve the (low, high) hue gradient colours."""
        if self._hue_colors is not None:
            return self._hue_colors[0], self._hue_colors[1]
        base = self.colors[0] if self.colors else "#3366cc"
        # Light-to-saturated ramp of the base palette colour against the
        # chart background, so the gradient reads on either theme.
        bg = self.theme.background_color
        return _lerp_color(base, bg, 0.7), base

    def _hue_color_at(self, value: float) -> str:
        assert self.hue is not None
        lo = min(self.hue)
        hi = max(self.hue)
        t = 0.0 if hi == lo else (value - lo) / (hi - lo)
        low_c, high_c = self._hue_endpoints()
        return _lerp_color(low_c, high_c, t)

    def _scaled_radii(self) -> list[float]:
        """Map each size onto the [min_radius, max_radius] range."""
        if not self.sizes:
            return []
        lo = min(self.sizes)
        hi = max(self.sizes)
        if hi == lo:
            # All equal: use the midpoint of the radius range.
            mid = (self.min_radius + self.max_radius) / 2
            return [mid for _ in self.sizes]
        span = self.max_radius - self.min_radius
        return [self.min_radius + (s - lo) / (hi - lo) * span for s in self.sizes]

    @property
    def representation(self) -> G:
        radii = self._scaled_radii()

        g = G(
            opacity=0.8,
            transform=[*self.get_base_transform()],
            clip_path="url(#plot-clip)",
        )
        for series_idx, (y_values, y_offsets, x_values, color) in enumerate(
            zip(self.y_values, self.y_offsets, self.x_values, self.colors),
        ):
            fill = color
            if self.series_styles and series_idx < len(self.series_styles):
                style = self.series_styles[series_idx] or {}
                if style.get("fill"):
                    fill = cast("str", style["fill"])

            series = G(fill=fill)
            x_offset = self.x_offset
            # Contrasting outline on each bubble in themes that configure one
            # (high-contrast); a no-op dict otherwise.
            outline = self._filled_outline_attrs()

            for i, (x, y, y_offset) in enumerate(zip(x_values, y_values, y_offsets)):
                x += x_offset
                y = self._apply_stacking(y, y_offset)
                r = radii[i] if i < len(radii) else self.min_radius
                circle = Circle(cx=x, cy=y, r=r, **outline)
                # When a hue dimension is supplied, each point's fill is
                # interpolated from its hue value, overriding the series fill.
                if self.hue is not None and i < len(self.hue):
                    point_fill = self._hue_color_at(self.hue[i])
                    if point_fill != fill:
                        circle.kwargs["fill"] = point_fill
                series.add_child(circle)
            g.add_children(series)

        wrapper = G()
        wrapper.add_child(g)

        size_legend_g = self._render_size_legend()
        if size_legend_g is not None:
            wrapper.add_child(size_legend_g)

        data_labels_g = self._render_data_labels()
        if data_labels_g:
            unclipped = G(transform=[*self.get_base_transform()])
            unclipped.add_child(data_labels_g)
            wrapper.add_child(unclipped)

        quadrant_g = self._render_quadrant_labels()
        if quadrant_g:
            unclipped_q = G(transform=[*self.get_base_transform()])
            unclipped_q.add_child(quadrant_g)
            wrapper.add_child(unclipped_q)

        return wrapper

    def _render_size_legend(self) -> G | None:
        """Render the size-scale legend (and hue colorbar) in the right band.

        Drawn in absolute chart coordinates (no plot flip) so text reads the
        right way up, mirroring the shared series legend. Representative
        bubbles are stacked top-down, each aligned with its value label; an
        optional hue colorbar sits beneath them.
        """
        if getattr(self, "_size_legend", "none") != "right":
            return None
        values = self._size_legend_values()
        if not values:
            return None

        font_size = self._legend_font_size()
        font_family = self.theme.legend_font_family
        font_color = self.theme.legend_font_color

        band_x = self.left_padding + self.plot_width + self._SIZE_LEGEND_GAP
        # Centre the bubble column on the largest radius so all bubbles share
        # a vertical centre line.
        bubble_cx = band_x + self.max_radius
        label_x = band_x + 2 * self.max_radius + self._SIZE_LEGEND_LABEL_GAP

        g = G()
        y = self.top_padding + self._SIZE_LEGEND_PAD

        if self._size_legend_title:
            y += font_size
            g.add_child(
                Text(
                    text=self._size_legend_title,
                    x=band_x,
                    y=y,
                    fill=font_color,
                    font_size=font_size,
                    font_family=font_family,
                    text_anchor="start",
                )
            )
            y += self._SIZE_LEGEND_PAD

        # Largest bubble first so the column reads from big to small.
        row_gap = 6
        for value in sorted(values, reverse=True):
            r = self._radius_for_size(value)
            cy = y + r
            # Hollow outline circles, not filled in the data colour: a filled
            # legend bubble in the right margin reads as a data bubble that
            # escaped the plot. An outline reads unambiguously as a scale key.
            g.add_child(
                Circle(
                    cx=bubble_cx,
                    cy=cy,
                    r=r,
                    fill="none",
                    stroke=font_color,
                    stroke_width=1.3,
                )
            )
            g.add_child(
                Text(
                    text=format(value, "g"),
                    x=label_x,
                    y=cy,
                    fill=font_color,
                    font_size=font_size,
                    font_family=font_family,
                    text_anchor="start",
                    dominant_baseline="central",
                )
            )
            y = cy + r + row_gap

        if self.hue is not None:
            # Clear vertical separation between the size-legend block and the
            # hue colorbar so the two legends never crowd or overlap. The gap
            # leaves room for the hue title's ascender below the last bubble.
            y += self._SIZE_LEGEND_GAP + font_size
            self._add_hue_bar(g, band_x, y, font_size, font_family, font_color)

        return g

    def _add_hue_bar(
        self,
        g: G,
        band_x: float,
        bar_top: float,
        font_size: float,
        font_family: str,
        font_color: str,
    ) -> None:
        """Render a vertical hue gradient strip with low/high value labels."""
        if self._hue_title:
            g.add_child(
                Text(
                    text=self._hue_title,
                    x=band_x,
                    y=bar_top,
                    fill=font_color,
                    font_size=font_size,
                    font_family=font_family,
                    text_anchor="start",
                )
            )
            bar_top += self._SIZE_LEGEND_PAD + font_size * 0.3

        bar_w = self._HUE_BAR_WIDTH
        bar_h = self._HUE_BAR_HEIGHT
        assert self.hue is not None
        lo = min(self.hue)
        hi = max(self.hue)

        # Gradient strip: top = high value, bottom = low value.
        n_stops = 48
        stop_h = bar_h / n_stops
        for i in range(n_stops):
            t = 1.0 - (i / (n_stops - 1) if n_stops > 1 else 0.0)
            value = lo + t * (hi - lo)
            g.add_child(
                Path(
                    fill=self._hue_color_at(value),
                    d=Path.get_path(band_x, bar_top + i * stop_h, bar_w, stop_h + 1),
                )
            )
        g.add_child(
            Path(
                fill="none",
                stroke=font_color,
                stroke_width=0.75,
                d=Path.get_path(band_x, bar_top, bar_w, bar_h),
            )
        )

        label_x = band_x + bar_w + self._HUE_TICK_GAP
        for frac, value in ((1.0, hi), (0.0, lo)):
            ty = bar_top + bar_h * (1.0 - frac)
            g.add_child(
                Text(
                    text=format(value, "g"),
                    x=label_x,
                    y=ty,
                    fill=font_color,
                    font_size=font_size,
                    font_family=font_family,
                    text_anchor="start",
                    dominant_baseline="central",
                )
            )

    def to_config(self) -> dict[str, Any]:
        cfg = super().to_config()
        cfg["sizes"] = list(self.sizes)
        cfg["min_radius"] = self.min_radius
        cfg["max_radius"] = self.max_radius
        if self._size_legend != "none":
            cfg["size_legend"] = self._size_legend
        if self._size_legend_title is not None:
            cfg["size_legend_title"] = self._size_legend_title
        if self.hue is not None:
            cfg["hue"] = list(self.hue)
        if self._hue_colors is not None:
            cfg["hue_colors"] = list(self._hue_colors)
        if self._hue_title is not None:
            cfg["hue_title"] = self._hue_title
        return cfg
