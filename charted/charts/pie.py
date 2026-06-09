from __future__ import annotations

import math
from typing import TypedDict, cast

from charted.charts.chart import Chart
from charted.config import get_pie_label_font_size
from charted.constants import PIE_CHART_HEIGHT, PIE_CHART_WIDTH
from charted.html.element import G, Path, Text
from charted.themes.core import Theme
from charted.utils.colors import complementary_color, get_contrast_color
from charted.utils.defaults import DEFAULT_COLORS
from charted.utils.types import (
    Labels,
    SeriesStyleConfig,
    ValueLabelOptions,
    Vector,
    Vector2D,
)


class _PieSlice(TypedDict):
    """Per-slice geometry computed in the pie chart's first render pass."""

    i: int
    value: float
    angle: float
    start_angle: float
    end_angle: float
    mid_angle: float
    mid_rad: float
    label_display: str
    text_width_est: float
    fits_inside: bool
    inside_label_r: float
    slice_pct: float


class PieChart(Chart):
    """Pie chart for displaying categorical data as proportional slices.

    Renders data as a circular chart divided into slices where each
    slice's arc length (and area) is proportional to its value.
    Supports doughnut mode, slice explosion, and custom labeling.

    Args:
        data: Values for each slice (must be non-negative, sum > 0)
        labels: Optional labels for each slice
        width, height: Chart dimensions in pixels (default 700x500 for better legend layout)
        title: Optional chart title
        theme: Optional theme configuration
        inner_radius: Ratio (0.0-1.0) for doughnut hole; 0 = regular pie
        explode: Single value or list to offset slices from center (pixels)
        start_angle: Starting angle in degrees (0 = top, clockwise)
        series_styles: Optional per-slice styling overrides
        show_percentages: If True, show percentage values on each slice

    Example:
        >>> from charted import PieChart
        >>> # Basic pie chart
        >>> chart = PieChart(
        ...     data=[25, 35, 40],
        ...     labels=['Product A', 'Product B', 'Product C']
        ... )
        >>> chart.save('market_share.svg')
    """

    render_axes = False  # Pie charts don't need axes or grid lines

    def __init__(
        self,
        data: Vector,
        labels: Labels | None = None,
        width: float = PIE_CHART_WIDTH,
        height: float = PIE_CHART_HEIGHT,
        title: str | None = None,
        theme: Theme | None = None,
        inner_radius: float = 0,
        explode: float | Vector = 0,
        start_angle: float = 0,
        series_styles: list[SeriesStyleConfig] | None = None,
        show_percentages: bool = False,
        value_labels: bool | str | dict[str, object] | None = None,
        legend: str = "none",
        category_patterns: list[str] | bool | None = None,
    ):
        """Initialize pie chart.

        Args:
            data: Values for each slice (must be non-negative, sum > 0)
            labels: Optional labels for each slice
            width, height: Chart dimensions in pixels (default 700x500)
            title: Optional chart title
            theme: Optional theme configuration
            inner_radius: Ratio (0.0-1.0) for doughnut hole; 0 = regular pie
            explode: Single value or list to offset slices from center (pixels)
            start_angle: Starting angle in degrees (0 = top, clockwise)
            series_styles: Optional per-slice styling overrides
            show_percentages: If True, show percentage values on each slice
        """
        # Validate inputs
        if not data or len(data) == 0:
            raise ValueError("Data cannot be empty")
        if any(
            not isinstance(v, (int, float)) or math.isnan(v) or math.isinf(v)
            for v in data
        ):
            raise ValueError("Data must contain only valid numbers")

        if any(v < 0 for v in data):
            raise ValueError("Data values cannot be negative")

        total = sum(data)
        if total == 0:
            raise ValueError("Total of all values must be greater than 0")

        self.inner_radius = inner_radius
        self.explode = explode if isinstance(explode, list) else [explode] * len(data)
        self.start_angle = start_angle
        self.show_percentages = show_percentages
        self._pie_value_labels = Chart._normalize_value_labels(value_labels)
        self._pie_data = list(data)  # Store original data for rendering
        self._pie_labels = labels
        self.series_styles = series_styles

        # Initialize colors before super().__init__() - Chart.__init__ accesses
        # self.colors (and renders slices) during _build_children. Resolve the
        # theme palette up front so presets (e.g. high-contrast) and custom
        # palettes drive slice colours. The default theme palette equals
        # DEFAULT_COLORS, so default renders are byte-for-byte unchanged.
        from charted.utils.theme_manager import ThemeManager

        resolved_theme = ThemeManager.load_theme(theme, "pie")
        self._generate_colors_from_data(data, base=resolved_theme.colors)

        # Create synthetic x_data and y_data for Chart base class compatibility
        x_data = cast(Vector2D, [[i for i in range(len(data))]])
        y_data = cast(Vector2D, [[0, 1]])  # Minimal y range

        super().__init__(
            width=width,
            height=height,
            x_data=x_data,
            y_data=y_data,
            y_labels=labels,
            title=title,
            zero_index=True,
            theme=theme,
            chart_type="pie",
            legend=legend,
            category_patterns=category_patterns,
        )

    def _has_legend_entries(self) -> bool:
        """Pie labels its slices, so any data drives the shared legend."""
        return bool(self._pie_data)

    def _legend_entries(self) -> list[tuple[str, str, str]]:
        """One square swatch per slice, coloured to match the slice."""
        data = self._pie_data
        if not data:
            return []
        labels = self._pie_labels or [str(i) for i in range(len(data))]
        colors = self.colors
        entries: list[tuple[str, str, str]] = []
        for idx, label in enumerate(labels):
            text = label.text if hasattr(label, "text") else str(label)
            color = colors[idx % len(colors)] if colors else "#000000"
            entries.append((text, color, self._LEGEND_DEFAULT_SHAPE))
        return entries

    def _legend_reserved_extent(self) -> float:
        """Reserve a band sized to the slice labels (not ``series_names``)."""
        from charted.utils.helpers import calculate_text_dimensions

        entries = self._legend_entries()
        if not entries:
            return 0.0
        font_size = self._legend_font_size()
        swatch = font_size
        gap = 6
        pad = 8
        if self._legend_placement == "right":
            max_w = max(
                calculate_text_dimensions(name, font_size=font_size).width
                for name, _, _ in entries
            )
            return swatch + gap + max_w + pad * 2
        return font_size + 6 + pad

    # ------------------------------------------------------------------
    # Default (legend='none') band legend, drawn below the pie circle
    # ------------------------------------------------------------------

    # Layout constants for the band legend below the pie.
    _DEFAULT_LEGEND_MARGIN = 10.0  # left/right margin inside the band
    _DEFAULT_LEGEND_ITEM_GAP = 16.0  # gap between entries on a row
    _DEFAULT_LEGEND_SWATCH_GAP = 6.0  # gap between a swatch and its text
    _DEFAULT_LEGEND_ROW_PAD = 6.0  # vertical padding between rows
    _DEFAULT_LEGEND_BAND_PAD = 10.0  # padding above/below the whole band

    def _default_legend_font_size(self) -> float:
        legend_cfg = getattr(self.theme, "legend_font_size", None)
        return float(legend_cfg) if legend_cfg else 12.0

    def _default_legend_entry_width(self, label: str, font_size: float) -> float:
        """Pixel width of one ``swatch + gap + text`` legend entry."""
        from charted.utils.helpers import calculate_text_dimensions

        text_w = calculate_text_dimensions(label, font_size=font_size).width
        return font_size + self._DEFAULT_LEGEND_SWATCH_GAP + text_w

    def _default_legend_label(self, label: object, value: float, total: float) -> str:
        """The display string for a slice (label plus any percentage/value)."""
        base = label.text if hasattr(label, "text") else str(label)
        if self.show_percentages:
            pct = (value / total) * 100
            return f"{base} ({pct:.1f}%)"
        if self._pie_value_labels:
            from charted.utils.value_format import format_value

            cfg = self._pie_value_labels
            opts = cast(
                "ValueLabelOptions", {k: v for k, v in cfg.items() if k != "format"}
            )
            fmt = cfg["format"]
            raw = (value / total) if fmt == "percent" else value
            return f"{base} ({format_value(raw, fmt, **opts)})"
        return base

    def _default_legend_rows(self, labels: Labels) -> list[list[int]] | None:
        """Pack legend entries into rows for the band below the pie.

        Returns a list of rows (each a list of slice indices) or ``None`` when
        the default legend should not be drawn. The legend is drawn only when a
        slice cannot carry its label inside the circle; otherwise every slice is
        already labelled directly and a legend would just repeat it.
        """
        data = self._pie_data
        if not data:
            return None

        # Mirror the inside-fit test from the geometry pass so the legend appears
        # exactly when at least one slice overspills. The no-band radius is used
        # as an upper bound: reserving the band only shrinks the circle, so a
        # slice that overspills the larger radius also overspills the smaller
        # one. This keeps the "legend shown?" decision stable.
        font_size = get_pie_label_font_size()
        radius = min(self.width, self.height) / 2 * 0.8
        inside_label_r = (
            radius * (1 + self.inner_radius) / 2
            if self.inner_radius > 0
            else radius * 0.6
        )
        total = sum(data)
        any_overspill = False
        for value, label in zip(data, labels):
            slice_pct = (value / total) * 100
            arc_length = inside_label_r * math.radians((value / total) * 360)
            display = self._default_legend_label(label, value, total)
            text_width_est = len(display) * font_size * 0.55
            if not self._label_fits_inside(slice_pct, text_width_est, arc_length):
                any_overspill = True
                break
        if not any_overspill:
            return None

        # Pack entries into rows that fit the available width.
        legend_font = self._default_legend_font_size()
        names = [
            label.text if hasattr(label, "text") else str(label) for label in labels
        ]
        avail = self.width - 2 * self._DEFAULT_LEGEND_MARGIN
        rows: list[list[int]] = []
        row: list[int] = []
        row_w = 0.0
        for idx, name in enumerate(names):
            w = self._default_legend_entry_width(name, legend_font)
            add = w if not row else self._DEFAULT_LEGEND_ITEM_GAP + w
            if row and row_w + add > avail:
                rows.append(row)
                row, row_w = [idx], w
            else:
                row.append(idx)
                row_w += add
        if row:
            rows.append(row)
        return rows

    def _default_legend_band_height(self, rows: list[list[int]]) -> float:
        """Total vertical band reserved below the pie for ``rows`` legend rows."""
        font_size = self._default_legend_font_size()
        row_h = font_size + self._DEFAULT_LEGEND_ROW_PAD
        return len(rows) * row_h + 2 * self._DEFAULT_LEGEND_BAND_PAD

    def _render_default_legend(
        self, rows: list[list[int]], labels: Labels, band: float
    ) -> G:
        """Render the band legend in the reserved strip at the bottom edge.

        The strip spans the full chart width below the pie circle, so swatches
        and text never overlap the wedges. Entries are centred on each row.
        """
        from charted.html.element import Rect
        from charted.utils.helpers import calculate_text_dimensions

        font_size = self._default_legend_font_size()
        font_family = getattr(self.theme, "legend_font_family", "DejaVu Sans")
        font_color = getattr(self.theme, "legend_font_color", "#444444")
        swatch = font_size
        gap = self._DEFAULT_LEGEND_SWATCH_GAP
        item_gap = self._DEFAULT_LEGEND_ITEM_GAP
        row_h = font_size + self._DEFAULT_LEGEND_ROW_PAD
        colors = self.colors

        names = [
            label.text if hasattr(label, "text") else str(label) for label in labels
        ]

        g = G()
        # First row's vertical centre sits inside the reserved band.
        band_top = self.height - band
        for r, row in enumerate(rows):
            widths = [
                swatch
                + gap
                + calculate_text_dimensions(names[i], font_size=font_size).width
                for i in row
            ]
            total_w = sum(widths) + item_gap * (len(row) - 1)
            x = (self.width - total_w) / 2
            cy = band_top + self._DEFAULT_LEGEND_BAND_PAD + r * row_h + row_h / 2
            for i, w in zip(row, widths):
                color = colors[i % len(colors)] if colors else "#000000"
                g.add_child(
                    Rect(
                        x=x,
                        y=cy - swatch / 2,
                        width=swatch,
                        height=swatch,
                        fill=color,
                    )
                )
                g.add_child(
                    Text(
                        x=x + swatch + gap,
                        y=cy + font_size * 0.35,
                        text=names[i],
                        fill=font_color,
                        font_size=font_size,
                        font_family=font_family,
                        text_anchor="start",
                    )
                )
                x += w + item_gap
        return g

    def _generate_colors_from_data(
        self, data: Vector, base: list[str] | None = None
    ) -> None:
        """Generate color palette based on data length.

        Internal helper to generate colors. For dense data (>10 slices), uses
        evenly-spaced HSL hues for maximum visual distinctness.

        Args:
            data: Data values - length determines number of colors needed.
            base: Base palette to cycle through for <=10 slices. Defaults to
                DEFAULT_COLORS (used during the pre-super() call when the theme
                palette is not yet resolved).
        """
        base_palette = list(base) if base else list(DEFAULT_COLORS)
        if not base_palette:
            base_palette = list(DEFAULT_COLORS)
        if not data:
            self._colors = list(base_palette)
            return

        n = len(data)
        if n <= 10:
            # Cycle the base palette and generate complementary colors past it.
            base_colors = base_palette
            self._colors = []
            for i in range(n):
                color_idx = i % len(base_colors)
                if i < len(base_colors):
                    self._colors.append(base_colors[color_idx])
                else:
                    self._colors.append(complementary_color(base_colors[color_idx]))
        else:
            # For dense data, generate evenly-spaced HSL hues with varied saturation/value
            import colorsys

            self._colors = []
            for i in range(n):
                hue = (i * 0.618034) % 1.0  # golden ratio spacing for max distinctness
                sat = 0.65 + (i % 3) * 0.1  # vary saturation slightly
                val = 0.75 + (i % 2) * 0.1  # vary value slightly
                r, g, b = colorsys.hsv_to_rgb(hue, min(sat, 0.9), min(val, 0.9))
                # Convert to hex
                self._colors.append(
                    f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
                )

    @property
    def colors(self) -> list[str]:
        """Get generated color palette (read-only).

        Colors are generated from data length in __init__ and cannot be modified.
        Use series_styles for per-slice color overrides.
        """
        return self._colors

    def _get_slice_path(
        self, cx: float, cy: float, radius: float, start_angle: float, end_angle: float
    ) -> str:
        """Generate SVG path data for a pie slice.

        Args:
            cx, cy: center coordinates
            radius: radius of the pie
            start_angle, end_angle: in degrees (0 = top, clockwise)
        """
        # Convert angles to radians (subtract 90deg to shift: 0deg->top, positive=clockwise)
        start_rad = math.radians(start_angle - 90)
        end_rad = math.radians(end_angle - 90)

        # Calculate start and end points on circumference
        x1 = cx + radius * math.cos(start_rad)
        y1 = cy + radius * math.sin(start_rad)
        x2 = cx + radius * math.cos(end_rad)
        y2 = cy + radius * math.sin(end_rad)

        # Determine large_arc flag (1 if arc > 180deg, else 0)
        angle_span = (end_angle - start_angle) % 360
        large_arc = 1 if angle_span > 180 else 0

        # Build path: move to center, line to start, arc to end, close

        if self.inner_radius > 0:
            # Doughnut mode: need inner path too
            # inner_radius is a ratio (0.0-1.0) of the outer radius
            actual_inner_radius = radius * self.inner_radius
            inner_x1 = cx + actual_inner_radius * math.cos(start_rad)
            inner_y1 = cy + actual_inner_radius * math.sin(start_rad)
            inner_x2 = cx + actual_inner_radius * math.cos(end_rad)
            inner_y2 = cy + actual_inner_radius * math.sin(end_rad)

            path = [
                f"M {x1} {y1}",  # Start at outer edge
                f"A {radius} {radius} 0 {large_arc} 1 {x2} {y2}",  # Arc to end
                f"L {inner_x2} {inner_y2}",  # Line to inner edge
                f"A {actual_inner_radius} {actual_inner_radius} 0 {large_arc} 0 {inner_x1} {inner_y1}",
                # Inner arc
                "Z",  # Close
            ]
        else:
            # Standard pie: move to center, line to start, arc to end, close
            path = [
                f"M {cx} {cy}",  # Move to center
                f"L {x1} {y1}",  # Line to start point
                f"A {radius} {radius} 0 {large_arc} 1 {x2} {y2}",  # Arc to end
                "Z",  # Close (back to center)
            ]

        return " ".join(path)

    def _get_full_circle_path(self, cx: float, cy: float, radius: float) -> list[str]:
        """Generate SVG path for a full circle (100% slice case)."""
        if self.inner_radius > 0:
            # Doughnut: use two circles with different fill rules
            actual_inner_radius = radius * self.inner_radius
            return [
                f"M {cx} {cy - radius}",
                f"A {radius} {radius} 0 1 1 {cx} {cy + radius}",
                f"A {radius} {radius} 0 1 1 {cx} {cy - radius}",
                "Z",
                f"M {cx} {cy - actual_inner_radius}",
                f"A {actual_inner_radius} {actual_inner_radius} 0 1 0 {cx} {cy + actual_inner_radius}",
                f"A {actual_inner_radius} {actual_inner_radius} 0 1 0 {cx} {cy - actual_inner_radius}",
                "Z",
            ]

        else:
            return [
                f"M {cx} {cy - radius}",
                f"A {radius} {radius} 0 1 1 {cx} {cy + radius}",
                f"A {radius} {radius} 0 1 1 {cx} {cy - radius}",
                "Z",
            ]

    def _label_fits_inside(
        self, slice_pct: float, text_width_est: float, arc_length: float
    ) -> bool:
        """Check if a label fits inside its slice."""
        return slice_pct >= 2.0 and text_width_est <= arc_length * 0.7

    @property
    def representation(self) -> G:
        """Render the pie chart."""
        result = G()

        # Get data and labels (use stored values, not x_data which is synthetic)
        data = self._pie_data
        labels = self._pie_labels or [str(i) for i in range(len(data))]

        total = sum(data)
        font_size = get_pie_label_font_size()
        current_angle = self.start_angle

        # When the chart uses the default (legend='none') labelling, a legend is
        # drawn only when some slice cannot carry its label inside the pie. That
        # legend sits in a band reserved *below* the circle so it never overlaps
        # the wedges, so the band height must be known before the geometry is
        # laid out. ``legend_rows`` is None when no legend is needed.
        legend_band = 0.0
        legend_rows: list[list[int]] | None = None
        if getattr(self, "_legend_placement", "none") == "none":
            legend_rows = self._default_legend_rows(labels)
            if legend_rows is not None:
                legend_band = self._default_legend_band_height(legend_rows)

        # Calculate center and radius. The circle is centred in the space left
        # above any reserved legend band so its bounding box never intrudes on
        # the band (and the band never overlaps the pie).
        cx = self.width / 2
        cy = (self.height - legend_band) / 2
        radius = min(self.width, self.height - legend_band) / 2 * 0.8
        radius = max(radius, 1.0)

        # --- First pass: compute slice geometry and classify labels ---
        slices: list[_PieSlice] = []  # geometry for each slice
        for i, (value, label) in enumerate(zip(data, labels)):
            angle = (value / total) * 360
            start_angle = current_angle
            end_angle = current_angle + angle
            mid_angle = (start_angle + end_angle) / 2
            mid_rad = math.radians(mid_angle - 90)

            # Determine label text
            label_display = str(label)
            if self.show_percentages:
                pct = (value / total) * 100
                label_display = f"{label_display} ({pct:.1f}%)"
            elif self._pie_value_labels:
                from charted.utils.value_format import format_value

                cfg = self._pie_value_labels
                opts = cast(
                    "ValueLabelOptions",
                    {k: v for k, v in cfg.items() if k != "format"},
                )
                fmt = cfg["format"]
                # For percent format, label the slice's share of the whole.
                raw = (value / total) if fmt == "percent" else value
                formatted = format_value(raw, fmt, **opts)
                label_display = f"{label_display} ({formatted})"

            text_width_est = len(label_display) * font_size * 0.55

            # Inside label radius
            if self.inner_radius > 0:
                actual_inner = radius * self.inner_radius
                inside_label_r = (actual_inner + radius) / 2
            else:
                inside_label_r = radius * 0.6

            slice_angle_rad = math.radians(angle)
            arc_length = inside_label_r * slice_angle_rad
            slice_pct = (value / total) * 100

            fits_inside = self._label_fits_inside(slice_pct, text_width_est, arc_length)

            slices.append(
                {
                    "i": i,
                    "value": value,
                    "angle": angle,
                    "start_angle": start_angle,
                    "end_angle": end_angle,
                    "mid_angle": mid_angle,
                    "mid_rad": mid_rad,
                    "label_display": label_display,
                    "text_width_est": text_width_est,
                    "fits_inside": fits_inside,
                    "inside_label_r": inside_label_r,
                    "slice_pct": slice_pct,
                }
            )
            current_angle = end_angle

        # --- Second pass: legend ---
        # When the shared placement legend is active (legend='right'|'bottom'
        # |'top'), the base class renders a single consistent box in a reserved
        # band, so skip the default legend here. With legend='none' (the
        # default) draw a legend in the reserved band below the pie only when at
        # least one slice is too small to carry its label inside the circle. If
        # every slice is labelled directly the legend would just repeat what is
        # already on the chart, so it is skipped.
        if legend_rows is not None:
            result.add_child(
                self._render_default_legend(legend_rows, labels, legend_band)
            )

        # --- Render slices ---
        for s in slices:
            i = s["i"]
            value = s["value"]
            angle = s["angle"]
            start_angle = s["start_angle"]
            end_angle = s["end_angle"]

            # Calculate explode offset
            explode_offset = self.explode[i] if i < len(self.explode) else 0
            transform = ""
            if explode_offset > 0:
                slice_rad = math.radians(s["mid_angle"] - 90)
                offset_x = explode_offset * math.cos(slice_rad)
                offset_y = explode_offset * math.sin(slice_rad)
                transform = f"translate({offset_x}, {offset_y})"

            # Get slice-specific style
            base_color = self.colors[i % len(self.colors)]
            slice_color = base_color
            slice_opacity = 0.8
            if self.series_styles and i < len(self.series_styles):
                style = self.series_styles[i] or {}
                if style.get("fill"):
                    slice_color = cast(str, style["fill"])
                if style.get("fill_opacity"):
                    slice_opacity = cast(float, style["fill_opacity"])

            # Pattern fill (only when the colour wasn't overridden) and the
            # high-contrast wedge outline. Both are no-ops by default.
            draw_fill = (
                self._category_fill(i, slice_color)
                if slice_color == base_color
                else slice_color
            )
            outline = self._filled_outline_attrs()

            # Render slice path
            path_data: str | list[str]
            if angle >= 359.9:
                path_data = self._get_full_circle_path(cx, cy, radius)
                slice_path = Path(
                    d=path_data,
                    fill=draw_fill,
                    fill_rule="evenodd" if self.inner_radius > 0 else "nonzero",
                    opacity=slice_opacity,
                    **outline,
                )
            else:
                path_data = self._get_slice_path(cx, cy, radius, start_angle, end_angle)
                slice_path = Path(
                    d=path_data,
                    fill=draw_fill,
                    opacity=slice_opacity,
                    **outline,
                )

            if transform:
                slice_g = G(transform=transform)
                slice_g.add_child(slice_path)
                result.add_child(slice_g)
            else:
                result.add_child(slice_path)

        # --- Render labels ---
        # Labels that fit inside their slice are drawn at the slice centroid.
        # Labels that don't fit (small or thin slices) are placed outside the
        # pie with a leader line so every slice keeps its value label instead
        # of being silently dropped.
        #
        # Only do this when a placement legend ('right'/'bottom') is active.
        # With legend='none' (the default) the band legend below the pie already
        # names every slice, so outside leader labels are redundant.
        if getattr(self, "_legend_placement", "none") != "none":
            outside = [s for s in slices if not s["fits_inside"]]
            self._render_outside_labels(result, outside, cx, cy, radius, font_size)

        # When the default band legend is drawn it names every slice already, so
        # the in-slice centroid labels would duplicate those entries (and only
        # the slices that happen to fit would get the extra label, which reads as
        # an inconsistent double-label). Render the legend OR the in-slice labels,
        # never both.
        if legend_rows is not None:
            return result

        for s in slices:
            if not s["fits_inside"]:
                continue
            i = s["i"]
            mid_rad = s["mid_rad"]
            label_display = s["label_display"]
            slice_color = self.colors[i % len(self.colors)]
            text_color = get_contrast_color(slice_color)

            # Label inside the slice
            label_x = cx + s["inside_label_r"] * math.cos(mid_rad)
            label_y = cy + s["inside_label_r"] * math.sin(mid_rad)
            label_text = Text(
                x=label_x,
                y=label_y,
                text=label_display,
                fill=text_color,
                font_size=font_size,
                font_family=self.theme.title_font_family,
                text_anchor="middle",
                dominant_baseline="middle",
            )
            result.add_child(label_text)

        return result

    def _render_outside_labels(
        self,
        result: G,
        outside: list[_PieSlice],
        cx: float,
        cy: float,
        radius: float,
        font_size: float,
    ) -> None:
        """Place labels for slices too small to hold an inside label.

        Each label is drawn just beyond the pie edge with a short leader line
        connecting it to its slice. Labels are split into left/right columns by
        their slice mid-angle and stacked vertically so they do not overlap.
        """
        if not outside:
            return

        text_color = self.theme.resolved_label_color
        line_color = self.theme.resolved_grid_color
        leader_r = radius * 1.02  # where the leader line starts (slice edge)
        line_h = font_size * 1.35

        # Split into left/right by horizontal direction of the slice midpoint.
        right = []
        left = []
        for s in outside:
            if math.cos(s["mid_rad"]) >= 0:
                right.append(s)
            else:
                left.append(s)

        for side in (right, left):
            if not side:
                continue
            is_right = side is right
            # Order top-to-bottom by vertical position so leaders don't cross.
            side.sort(key=lambda s: math.sin(s["mid_rad"]))

            # Vertically distribute labels around the side, centred on the pie.
            # A shared elbow x-column keeps the horizontal runs parallel so the
            # leader lines for adjacent labels don't cross.
            n = len(side)
            start_y = cy - (n - 1) * line_h / 2
            elbow_x = cx + (radius * 1.12 if is_right else -radius * 1.12)
            text_x = cx + (radius * 1.18 if is_right else -radius * 1.18)
            for k, s in enumerate(side):
                mid_rad = s["mid_rad"]
                # Point on the slice edge where the leader starts.
                x0 = cx + leader_r * math.cos(mid_rad)
                y0 = cy + leader_r * math.sin(mid_rad)
                # Horizontal target row for the text.
                text_y = start_y + k * line_h
                # Leader line: slice edge -> elbow (at row height) -> text.
                d = (
                    f"M {x0:.2f} {y0:.2f} "
                    f"L {elbow_x:.2f} {text_y:.2f} "
                    f"L {text_x:.2f} {text_y:.2f}"
                )
                result.add_child(
                    Path(
                        d=d,
                        stroke=line_color,
                        stroke_width=1,
                        fill="none",
                        opacity=0.7,
                    )
                )
                anchor = "start" if is_right else "end"
                gap = 4 if is_right else -4
                result.add_child(
                    Text(
                        x=text_x + gap,
                        y=text_y,
                        text=s["label_display"],
                        fill=text_color,
                        font_size=font_size,
                        font_family=self.theme.title_font_family,
                        text_anchor=anchor,
                        dominant_baseline="middle",
                    )
                )
