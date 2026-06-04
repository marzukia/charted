"""Shared series-legend component used by every multi-series chart.

The scatter chart pioneered a placement-aware legend (right / bottom / top)
whose band is reserved by the LayoutEngine so it never overlaps the plot. This
module lifts that logic into a mixin that any chart can use, so pie, line, bar,
column, boxplot, combo, bubble and polar share one consistent legend box with
the same placement options.

Backward compatibility: the legend is off by default (``legend='none'``). When
off, the mixin reserves no layout space and the chart's historical in-plot
legend (if any) is left untouched, so existing renders are byte-for-byte
identical.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, cast

from charted.html.element import Element, G, Rect, Text

if TYPE_CHECKING:
    from charted.themes.core import Theme


class _LegendHost(Protocol):
    """Structural type for the chart that hosts the :class:`SeriesLegend` mixin.

    Used only by the type checker (via :func:`typing.cast`) so the mixin can
    reference host-provided attributes without coupling to a concrete chart
    class. It introduces no runtime members on the mixin or its hosts.
    """

    @property
    def colors(self) -> list[str]: ...

    @property
    def series_names(self) -> list[str] | None: ...

    @property
    def theme(self) -> Theme: ...

    @property
    def left_padding(self) -> float: ...

    @property
    def top_padding(self) -> float: ...

    @property
    def bottom_padding(self) -> float: ...

    @property
    def plot_width(self) -> float: ...

    @property
    def plot_height(self) -> float: ...

    def _default_legend(self) -> G | None: ...


VALID_LEGEND_PLACEMENTS = ("none", "right", "bottom", "top")


class SeriesLegend:
    """Mixin providing a placement-aware, layout-reserved series legend.

    Charts opt in by passing ``legend='right'|'bottom'|'top'`` to their
    constructor. The host chart must call :meth:`_init_legend` early in
    ``__init__`` (before ``super().__init__`` for the base ``Chart``, which
    reads the layout hooks) and expose ``series_names``, ``colors``,
    ``theme``, ``left_padding``, ``top_padding``, ``plot_width`` and
    ``plot_height``.

    Subclasses may override :meth:`_legend_entries` to control the
    ``(name, colour, shape)`` rows, and provide a ``_marker_element`` method to
    draw shaped swatches (scatter does this). The default swatch is a square,
    which suits filled-area charts (bar, column, pie, line, box, etc.).
    """

    # Default marker swatch for charts that do not draw shaped markers.
    _LEGEND_DEFAULT_SHAPE = "square"

    def _init_legend(self, placement: str) -> None:
        """Validate and store the requested legend placement."""
        if placement not in VALID_LEGEND_PLACEMENTS:
            raise ValueError(
                f"Invalid legend placement {placement!r}. "
                f"Expected one of {', '.join(repr(p) for p in VALID_LEGEND_PLACEMENTS)}."
            )
        self._legend_placement = placement

    # ------------------------------------------------------------------
    # LayoutEngine hooks (override the base Chart no-op defaults)
    # ------------------------------------------------------------------

    def _legend_layout_position(self) -> str:
        """Side reserved for the legend band, or 'none'."""
        placement = getattr(self, "_legend_placement", "none")
        if placement != "none" and self._has_legend_entries():
            return placement
        return "none"

    def _legend_layout_extent(self) -> float:
        """Pixel band to reserve for the legend on its placement side."""
        if self._legend_layout_position() == "none":
            return 0.0
        return self._legend_reserved_extent()

    # ------------------------------------------------------------------
    # Entries
    # ------------------------------------------------------------------

    def _has_legend_entries(self) -> bool:
        """Cheap check (names only) usable before colours/values exist."""
        return bool(getattr(self, "series_names", None))

    def _legend_entries(self) -> list[tuple[str, str, str]]:
        """Build ``(name, fill, shape)`` rows, one per named series.

        Default: a square swatch per ``series_names`` entry. The swatch fill is
        the same fill the chart paints that series with, so when the chart uses
        category hatch patterns (``category_patterns=True``) the legend swatch
        shows the matching pattern instead of a flat colour. Returns an empty
        list when there is nothing to label.
        """
        names = getattr(self, "series_names", None)
        if not names:
            return []
        colors = cast("_LegendHost", self).colors
        category_fill = getattr(self, "_category_fill", None)
        entries: list[tuple[str, str, str]] = []
        for idx, name in enumerate(names):
            color = colors[idx] if idx < len(colors) else "#000000"
            fill = category_fill(idx, color) if callable(category_fill) else color
            entries.append((str(name), fill, self._LEGEND_DEFAULT_SHAPE))
        return entries

    # ------------------------------------------------------------------
    # Geometry
    # ------------------------------------------------------------------

    def _legend_font_size(self) -> float:
        return cast("_LegendHost", self).theme.legend_font_size

    def _legend_reserved_extent(self) -> float:
        """Pixel band to reserve for the legend on its placement side.

        Depends only on the series names and theme font size, so it is safe to
        call from the LayoutEngine hook before colours/values are computed.
        """
        from charted.utils.helpers import calculate_text_dimensions

        names = getattr(self, "series_names", None)
        if not names:
            return 0.0
        font_size = self._legend_font_size()
        row_h = font_size + 6
        swatch = font_size
        gap = 6
        pad = 8
        if self._legend_placement == "right":
            max_w = 0.0
            for name in names:
                w = calculate_text_dimensions(str(name), font_size=font_size).width
                max_w = max(max_w, w)
            return swatch + gap + max_w + pad * 2
        # top / bottom: a single text row plus padding
        return row_h + pad

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    @property
    def legend(self) -> G | None:
        """Render the series legend in the band reserved by the layout.

        When ``legend='none'`` (the default), defers to the host's previous
        legend behaviour via ``_default_legend`` so existing output is
        unchanged. Otherwise draws one swatch + label per series in the chosen
        band.
        """
        host = cast("_LegendHost", self)
        if getattr(self, "_legend_placement", "none") == "none":
            return host._default_legend()

        entries = self._legend_entries()
        if not entries:
            return None

        font_size = self._legend_font_size()
        font_family = host.theme.legend_font_family
        font_color = host.theme.legend_font_color
        swatch = font_size
        gap = 6
        pad = 8
        row_h = font_size + 6

        lp = host.left_padding
        tp = host.top_padding
        pw = host.plot_width
        ph = host.plot_height

        g = G()

        if self._legend_placement == "right":
            x = lp + pw + pad
            total_h = len(entries) * row_h
            y = tp + (ph - total_h) / 2
            for name, color, shape in entries:
                cy = y + row_h / 2
                cx = x + swatch / 2
                self._legend_add_entry(
                    g,
                    name,
                    color,
                    shape,
                    cx,
                    cy,
                    x + swatch + gap,
                    font_size,
                    font_family,
                    font_color,
                )
                y += row_h
            return g

        # top / bottom: lay entries out in a horizontal row, centred on the plot
        from charted.utils.helpers import calculate_text_dimensions

        widths = []
        for name, _, _ in entries:
            tw = calculate_text_dimensions(name, font_size=font_size).width
            widths.append(swatch + gap + tw)
        item_gap = 16
        total_w = sum(widths) + item_gap * (len(entries) - 1)
        x = lp + (pw - total_w) / 2
        band = self._legend_reserved_extent()
        if self._legend_placement == "top":
            # Centre the legend row within the band reserved above the plot,
            # which sits just under the title (top_padding already includes it).
            cy = tp - band + row_h / 2
        else:
            # Centre the legend row within the band reserved at the very bottom
            # of the chart, below the x-axis tick labels. The bottom padding is
            # base label space + this legend band, so anchoring to the chart's
            # bottom edge keeps the legend clear of the axis labels.
            bottom_edge = tp + ph + host.bottom_padding
            cy = bottom_edge - band + row_h / 2
        for (name, color, shape), w in zip(entries, widths):
            cx = x + swatch / 2
            self._legend_add_entry(
                g,
                name,
                color,
                shape,
                cx,
                cy,
                x + swatch + gap,
                font_size,
                font_family,
                font_color,
                text_baseline=cy + font_size * 0.35,
            )
            x += w + item_gap
        return g

    def _legend_swatch(
        self, shape: str, cx: float, cy: float, size: float, color: str
    ) -> Element | None:
        """Build the swatch element for one legend row.

        Charts that draw shaped markers (scatter) provide ``_marker_element``;
        this routes through it so the legend shows the same shape as the plot.
        Everything else gets a square colour chip.
        """
        marker = getattr(self, "_marker_element", None)
        if marker is not None and shape and shape != self._LEGEND_DEFAULT_SHAPE:
            mark = marker(shape, cx, cy, size, color)
            if mark is not None:
                mark.kwargs["fill"] = color
                return cast("Element", mark)
            return None
        # Default square chip.
        return Rect(
            x=cx - size, y=cy - size, width=size * 2, height=size * 2, fill=color
        )

    def _legend_add_entry(
        self,
        g: G,
        name: str,
        color: str,
        shape: str,
        cx: float,
        cy: float,
        text_x: float,
        font_size: float,
        font_family: str,
        font_color: str,
        text_baseline: float | None = None,
    ) -> None:
        """Add one swatch + label to the legend group ``g``."""
        mark = self._legend_swatch(shape, cx, cy, font_size / 2, color)
        if mark is not None:
            g.add_child(mark)
        baseline = text_baseline if text_baseline is not None else cy + font_size * 0.35
        g.add_child(
            Text(
                text=name,
                x=text_x,
                y=baseline,
                fill=font_color,
                font_size=font_size,
                font_family=font_family,
                text_anchor="start",
            )
        )
