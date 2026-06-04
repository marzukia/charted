from __future__ import annotations

import math

from charted.charts.pie import PieChart
from charted.config import get_pie_label_font_size
from charted.constants import DEFAULT_CHART_HEIGHT, DEFAULT_CHART_WIDTH
from charted.html.element import Circle, G, Path, Rect, Text
from charted.themes.core import Theme
from charted.utils.colors import get_contrast_color
from charted.utils.types import Labels, SeriesStyleConfig, Vector
from charted.utils.value_format import format_value

# Default number of concentric scale rings drawn behind polar-area slices.
DEFAULT_RADIAL_LEVELS = 5


class PolarAreaChart(PieChart):
    """Polar area chart: a pie where every slice spans an equal angle and
    the slice radius encodes the value.

    Unlike a pie chart (slice angle encodes value), here all slices share the
    same angular width of ``360 / N`` degrees, and each slice's radius is
    scaled by its value so larger values reach further out.

    Args:
        data: Non-negative values, one per slice.
        labels: Optional labels for each slice.
        width, height: Chart dimensions in pixels.
        title: Optional chart title.
        theme: Optional theme configuration.
        start_angle: Starting angle in degrees (0 = top, clockwise).
        series_styles: Optional per-slice styling overrides.
        show_radial_labels: Draw numeric labels on the radial scale rings
            (default True).
        radial_levels: Number of concentric scale rings to draw (default 5).

    Example:
        >>> from charted import PolarAreaChart
        >>> chart = PolarAreaChart(
        ...     data=[10, 20, 30, 15],
        ...     labels=['N', 'E', 'S', 'W'],
        ... )
        >>> chart.save('polar.svg')
    """

    def __init__(
        self,
        data: Vector,
        labels: Labels = None,
        width: float = DEFAULT_CHART_WIDTH,
        height: float = DEFAULT_CHART_HEIGHT,
        title: str | None = None,
        theme: Theme | None = None,
        start_angle: float = 0,
        series_styles: list[SeriesStyleConfig] | None = None,
        show_percentages: bool = False,
        legend: str = "none",
        show_radial_labels: bool = True,
        radial_levels: int = DEFAULT_RADIAL_LEVELS,
        category_patterns: list[str] | bool | None = None,
    ):
        self.show_radial_labels = show_radial_labels
        self.radial_levels = radial_levels
        super().__init__(
            data=data,
            labels=labels,
            width=width,
            height=height,
            title=title,
            theme=theme,
            inner_radius=0,
            explode=0,
            start_angle=start_angle,
            series_styles=series_styles,
            show_percentages=show_percentages,
            legend=legend,
            category_patterns=category_patterns,
        )

    def _plot_rect(self) -> tuple[float, float, float, float]:
        """Plot rectangle (x, y, w, h) inside the padding.

        Uses the layout engine so the circle is centred in the area below the
        title (top_padding includes the title) instead of the full canvas,
        which otherwise leaves the rings sitting top-heavy under the title.
        """
        layout = self.layout
        return (
            layout.left_padding,
            layout.top_padding,
            layout.plot_width,
            layout.plot_height,
        )

    def _center(self) -> tuple[float, float]:
        """Centre of the rings and slice fan.

        Horizontally centred on the canvas (a polar chart has no side-axis
        labels to offset for), vertically centred in the plot rect so it sits
        below the title rather than top-heavy on the full canvas.
        """
        _, y, _, h = self._plot_rect()
        return self.width / 2, y + h / 2

    def _max_radius(self) -> float:
        """Outer radius the largest-valued slice reaches."""
        _, _, w, h = self._plot_rect()
        return min(w, h) / 2 * 0.8

    def slice_angles(self) -> list[tuple[float, float]]:
        """Return (start, end) angle in degrees for each equal-width slice."""
        n = len(self._pie_data)
        step = 360 / n
        return [
            (self.start_angle + i * step, self.start_angle + (i + 1) * step)
            for i in range(n)
        ]

    @staticmethod
    def _nice_step(rough: float, round_to_nearest: bool) -> float:
        """Round a rough step to a 1/2/5 x 10^n 'nice' value (Heckbert)."""
        if rough <= 0:
            return 1.0
        exp = math.floor(math.log10(rough))
        frac = rough / 10**exp
        if round_to_nearest:
            nice = 1 if frac < 1.5 else 2 if frac < 3 else 5 if frac < 7 else 10
        else:
            nice = 1 if frac <= 1 else 2 if frac <= 2 else 5 if frac <= 5 else 10
        return nice * 10**exp

    def _radial_scale(self) -> tuple[float, list[float]]:
        """Return (axis_max, tick_values) snapped to round numbers.

        The outer ring sits on a 'nice' maximum at or above the data max, and
        the tick values are round multiples of a nice step, so slice tips land
        on the labelled rings instead of arbitrary fractions of the data max.
        """
        data = self._pie_data
        vmax = max(data) if data else 0
        if vmax <= 0:
            return 1.0, []
        target = max(2, self.radial_levels)
        step = self._nice_step(vmax / target, True)
        axis_max = math.ceil(vmax / step) * step
        count = int(round(axis_max / step))
        ticks = [round(step * i, 10) for i in range(1, count + 1)]
        return axis_max, ticks

    def slice_radii(self) -> list[float]:
        """Return the rendered radius for each slice, scaled by value.

        Linear from the centre to the nice axis maximum, so a slice of value v
        reaches exactly the ring labelled v.
        """
        data = self._pie_data
        outer = self._max_radius()
        axis_max, _ = self._radial_scale()
        if axis_max <= 0:
            return [outer for _ in data]
        return [(v / axis_max) * outer for v in data]

    @property
    def representation(self) -> G:
        result = G()

        cx, cy = self._center()

        data = self._pie_data
        labels = self._pie_labels or [str(i) for i in range(len(data))]
        total = sum(data)

        angles = self.slice_angles()
        radii = self.slice_radii()

        # Radial scale rings sit behind the slices so values can be read off.
        self._render_radial_grid(result, cx, cy, data)

        for i, (value, label) in enumerate(zip(data, labels)):
            start_angle, end_angle = angles[i]
            radius = radii[i]

            base_color = self.colors[i % len(self.colors)]
            slice_color = base_color
            slice_opacity = 0.8
            if self.series_styles and i < len(self.series_styles):
                style = self.series_styles[i] or {}
                if style.get("fill"):
                    slice_color = style["fill"]
                if style.get("fill_opacity"):
                    slice_opacity = style["fill_opacity"]

            draw_fill = (
                self._category_fill(i, slice_color)
                if slice_color == base_color
                else slice_color
            )
            outline = self._filled_outline_attrs()

            # Full-circle edge case (N == 1): the slice spans the whole circle,
            # so angle_span % 360 == 0 collapses _get_slice_path to a zero-area
            # sliver. Use the full-circle path instead, matching PieChart.
            if (end_angle - start_angle) >= 359.9:
                path_data = self._get_full_circle_path(cx, cy, radius)
            else:
                path_data = self._get_slice_path(cx, cy, radius, start_angle, end_angle)
            result.add_child(
                Path(d=path_data, fill=draw_fill, opacity=slice_opacity, **outline)
            )

            # Label near the slice midpoint. Small slices have a tiny radius, so
            # placing the label at a fraction of their own radius piles every
            # short slice's label on top of the centre. Floor the label distance
            # so short slices push their labels outward (where the wider angular
            # span separates them); when that floor lands the label beyond the
            # slice arc, colour it for the background instead of the fill.
            label_angle = (start_angle + end_angle) / 2
            label_rad = math.radians(label_angle - 90)
            inner_label_radius = radius * 0.6
            min_label_radius = self._max_radius() * 0.42
            if inner_label_radius >= min_label_radius:
                label_radius = inner_label_radius
                text_color = get_contrast_color(slice_color)
            else:
                label_radius = min_label_radius
                text_color = self._ring_label_color()
            label_x = cx + label_radius * math.cos(label_rad)
            label_y = cy + label_radius * math.sin(label_rad)
            label_display = str(label)
            if self.show_percentages and total > 0:
                pct = (value / total) * 100
                label_display = f"{label_display} ({pct:.1f}%)"

            result.add_child(
                Text(
                    x=label_x,
                    y=label_y,
                    text=label_display,
                    fill=text_color,
                    font_size=get_pie_label_font_size(),
                    font_family=self.theme.title_font_family,
                    text_anchor="middle",
                    dominant_baseline="middle",
                )
            )

        # Numeric ring labels are drawn last so the slices cannot cover them.
        self._render_radial_labels(result, cx, cy)

        return result

    def _ring_color(self) -> str:
        """Theme-aware colour for the radial ring lines."""
        theme = self.theme
        resolved = getattr(theme, "resolved_grid_color", None)
        if resolved:
            return resolved
        return getattr(theme, "grid_color", "#cccccc")

    def _ring_label_color(self) -> str:
        """High-contrast colour for the numeric ring labels.

        The faint grid colour reads fine for the ring lines but is nearly
        invisible for text on a dark background. Use the theme's full-opacity
        label colour so the numbers stay legible on every preset.
        """
        theme = self.theme
        resolved = getattr(theme, "resolved_label_color", None)
        if resolved:
            return resolved
        return getattr(theme, "title_color", "#333")

    def _render_radial_grid(
        self, result: G, cx: float, cy: float, data: list[float]
    ) -> None:
        """Draw concentric scale rings behind the slices.

        Rings are spaced so each one sits on a round value of the linear
        ``0..axis_max`` scale, giving the otherwise scale-less polar slices a
        readable magnitude reference. The numeric labels are drawn separately
        (after the slices) so they cannot be hidden under a slice.
        """
        if self.radial_levels <= 0:
            return

        outer = self._max_radius()
        axis_max, ticks = self._radial_scale()
        if not ticks or axis_max <= 0:
            return
        ring_color = self._ring_color()
        grid_width = getattr(self.theme, "grid_width", None) or 1

        for tick in ticks:
            radius = (tick / axis_max) * outer
            result.add_child(
                Circle(
                    cx=cx,
                    cy=cy,
                    r=radius,
                    fill="none",
                    stroke=ring_color,
                    stroke_width=grid_width,
                )
            )

    def _render_radial_labels(self, result: G, cx: float, cy: float) -> None:
        """Draw the numeric ring labels on top of the slices.

        Each number sits just outside its ring at 12 o'clock and carries a
        background-coloured halo (a thick stroke behind the glyphs via
        ``paint-order: stroke``) so it stays readable even where a slice
        covers the ring, in a high-contrast colour so it reads on dark themes.
        """
        if self.radial_levels <= 0 or not self.show_radial_labels:
            return

        outer = self._max_radius()
        axis_max, ticks = self._radial_scale()
        if not ticks or axis_max <= 0:
            return

        # Draw each number as a solid badge: a pill filled with the
        # high-contrast label colour (white on dark themes) carrying the text
        # in the background colour. Dark-on-light (or light-on-dark) badges
        # read unambiguously over both the dark canvas and the slices.
        pill_color = self._ring_label_color()
        text_color = getattr(self.theme, "background_color", "#ffffff")
        font_size = get_pie_label_font_size()
        # Gap (px) between a ring line and its numeric label so they don't touch.
        label_gap = 3

        for tick in ticks:
            radius = (tick / axis_max) * outer
            text = format_value(tick)
            label_x = cx + 3
            label_y = cy - radius - label_gap
            char_w = font_size * 0.62
            pad_x = 3
            pad_y = 2
            box_w = len(text) * char_w + pad_x * 2
            box_h = font_size + pad_y * 2
            result.add_child(
                Rect(
                    x=label_x - pad_x,
                    y=label_y - font_size + pad_y,
                    width=box_w,
                    height=box_h,
                    rx=2,
                    fill=pill_color,
                    fill_opacity=1,
                )
            )
            result.add_child(
                Text(
                    x=label_x,
                    y=label_y,
                    text=text,
                    fill=text_color,
                    font_size=font_size,
                    font_family=self.theme.title_font_family,
                    font_weight="bold",
                    text_anchor="start",
                )
            )

    def to_config(self) -> dict:
        cfg = super().to_config()
        cfg["data"] = list(self._pie_data)
        cfg["labels"] = [
            lbl.text if hasattr(lbl, "text") else str(lbl)
            for lbl in (self._pie_labels or [])
        ] or None
        cfg["start_angle"] = self.start_angle
        return cfg
