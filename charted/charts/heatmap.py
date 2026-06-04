"""Heatmap chart for visualizing matrix data as colored cells.

Displays a 2D grid where each cell is colored according to its value,
using a configurable color scale from low (cool) to high (warm) values.
Supports row and column labels, value annotations, and auto color scaling.
"""

from __future__ import annotations

from charted.charts.chart import Chart
from charted.constants import DEFAULT_CHART_HEIGHT, DEFAULT_CHART_WIDTH
from charted.html.element import G, Path, Text
from charted.themes.core import ColorScale, Theme
from charted.utils.types import Labels, SeriesStyleConfig


def _lerp_color(c1: str, c2: str, t: float) -> str:
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


class HeatmapChart(Chart):
    """Heatmap chart for visualizing matrix data as colored cells.

    Renders a 2D grid where each cell's color represents its value.
    Supports row and column labels, value annotations inside cells,
    and automatic color scaling based on data range.

    Args:
        data: 2D matrix (list of lists) where each inner list is a row.
        x_labels: Labels for each column (optional, auto-generated if omitted).
        y_labels: Labels for each row (optional, auto-generated if omitted).
        width, height: Chart dimensions in pixels.
        title: Optional chart title.
        theme: Optional theme configuration.
        series_names: Names for each series (shown in legend).
        series_styles: Per-series style overrides.
        low_color: Color for the lowest value in the data. Defaults to None,
            which derives the low endpoint from the first theme palette colour.
        high_color: Color for the highest value in the data. Defaults to None,
            which derives the high endpoint from the last theme palette colour.
        color_scale: Optional continuous color scale. Pass a ColorScale, a
            named palette string (e.g. 'viridis'), or a list of hex stops to
            color cells along a multi-stop gradient. Overrides low_color and
            high_color. Defaults to None (two-color low/high behavior).
        show_values: If True, display the numeric value in each cell (default True).
        value_format: Format string for displayed values (default '.1f').
        cell_gap: Gap between cells as fraction of cell size (default 0.04).
        label_font_size: Font size for row/column labels (default 11).
        cell_border_width: Stroke width of the thin border around each cell,
            in pixels (default 0.25).
        colorbar_ticks: Number of evenly spaced tick labels on the colorbar,
            including the min and max endpoints (default 5, minimum 2).
        colorbar_title: Optional title rendered vertically beside the colorbar,
            e.g. a unit or measure name. Defaults to None (no title).
        colorbar_width: Width of the gradient strip in pixels (default 16).

    Example:
        >>> from charted import HeatmapChart
        >>> chart = HeatmapChart(
        ...     data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        ...     x_labels=['A', 'B', 'C'],
        ...     y_labels=['X', 'Y', 'Z'],
        ... )
        >>> chart.save('matrix.svg')
    """

    render_axes = False

    def __init__(
        self,
        data: list[list[float]],
        x_labels: Labels = None,
        y_labels: Labels = None,
        width: float = DEFAULT_CHART_WIDTH,
        height: float = DEFAULT_CHART_HEIGHT,
        title: str | None = None,
        theme: Theme | None = None,
        series_names: list[str] | None = None,
        series_styles: list[SeriesStyleConfig] | None = None,
        low_color: str | None = None,
        high_color: str | None = None,
        color_scale: "ColorScale | str | list[str] | None" = None,
        show_values: bool = True,
        value_format: str = ".1f",
        cell_gap: float = 0.04,
        label_font_size: int = 11,
        cell_border_width: float = 0.25,
        colorbar_ticks: int = 5,
        colorbar_title: str | None = None,
        colorbar_width: float = 16,
    ):
        if not data or not isinstance(data, list) or len(data) == 0:
            raise ValueError("Data must be a non-empty 2D list")

        if not isinstance(data[0], list):
            raise ValueError("Data must be a 2D matrix (list of lists)")

        n_rows = len(data)
        n_cols = len(data[0]) if n_rows > 0 else 0

        if n_cols == 0:
            raise ValueError("Each row must have at least one column")

        for i, row in enumerate(data):
            if len(row) != n_cols:
                raise ValueError(f"Row {i} has {len(row)} columns, expected {n_cols}")

        self._matrix = data
        self._n_rows = n_rows
        self._n_cols = n_cols
        # Defer resolving low/high colours until after super().__init__ has
        # loaded the theme. None means "derive the gradient endpoints from the
        # theme palette" (so presets like high-contrast and custom palettes
        # drive the heatmap); explicit hex strings are honoured as-is.
        self._low_color_override = low_color
        self._high_color_override = high_color
        self.show_values = show_values
        self.value_format = value_format
        self.cell_gap = cell_gap
        self._label_font_size = label_font_size
        self.cell_border_width = max(0.0, float(cell_border_width))
        self.colorbar_ticks = max(2, int(colorbar_ticks))
        self.colorbar_title = colorbar_title
        self.colorbar_width = max(1.0, float(colorbar_width))

        if x_labels is None:
            x_labels = [str(i + 1) for i in range(n_cols)]
        if y_labels is None:
            y_labels = [str(i + 1) for i in range(n_rows)]

        if len(x_labels) != n_cols:
            raise ValueError(
                f"x_labels count ({len(x_labels)}) must match columns ({n_cols})"
            )
        if len(y_labels) != n_rows:
            raise ValueError(
                f"y_labels count ({len(y_labels)}) must match rows ({n_rows})"
            )

        self._x_labels = list(x_labels)
        self._y_labels = list(y_labels)

        all_values = [v for row in data for v in row]
        self._data_min = min(all_values)
        self._data_max = max(all_values)
        self._data_range = self._data_max - self._data_min
        self.color_scale = self._resolve_color_scale(color_scale)

        # Resolve the theme palette up front (super().__init__ triggers
        # _build_children, which renders cells before super returns) so the
        # gradient endpoints can derive from the theme when the caller did not
        # override them. The default theme palette equals the historical
        # low/high defaults' source, keeping default renders unchanged.
        from charted.utils.theme_manager import ThemeManager

        resolved_theme = ThemeManager.load_theme(theme, "heatmap")
        palette = list(resolved_theme.colors) if resolved_theme.colors else []
        # low = first palette colour, high = second. With the default palette
        # (#5fab9e, #f58b51, ...) this reproduces the historical low/high
        # defaults exactly, so default renders are byte-for-byte unchanged,
        # while presets like high-contrast pick up their own two endpoints.
        self.low_color = self._low_color_override or (
            palette[0] if palette else "#5fab9e"
        )
        self.high_color = self._high_color_override or (
            palette[1] if len(palette) > 1 else "#f58b51"
        )

        x_data = [[float(i) for i in range(n_cols)] for _ in range(n_rows)]
        y_data = [[float(i) for i in range(n_rows)] for _ in range(n_cols)]

        super().__init__(
            width=width,
            height=height,
            x_data=x_data,
            y_data=y_data,
            x_labels=x_labels,
            y_labels=y_labels,
            title=title,
            zero_index=True,
            theme=theme,
            chart_type="heatmap",
            series_styles=series_styles,
            series_names=series_names,
        )

        self.layout.h_padding = 0.07
        self.children.clear()
        children = [self.container, self.title, self.representation, self.legend]
        self.add_children(*children)

    # Colorbar geometry. The gap between the plot and the gradient strip,
    # the gap between the strip and its tick marks, and the tick mark length.
    _COLORBAR_GAP = 14
    _COLORBAR_TICK_GAP = 5
    _COLORBAR_TICK_LEN = 4

    def _colorbar_label_width(self) -> float:
        """Estimate the pixel width of the widest colorbar tick label.

        Used to reserve enough right padding so the colorbar, its tick
        labels and (optional) title stay inside the SVG bounds.
        """
        labels = [
            format(
                self._data_min + (self._data_max - self._data_min) * (i / (self.colorbar_ticks - 1)),
                self.value_format,
            )
            for i in range(self.colorbar_ticks)
        ]
        longest = max((len(s) for s in labels), default=1)
        # ~0.6em per character at the label font size.
        return longest * self._label_font_size * 0.6

    def _legend_layout_position(self) -> str:
        # Always reserve a right-hand band for the colorbar.
        return "right"

    def _legend_layout_extent(self) -> float:
        band = (
            self._COLORBAR_GAP
            + self.colorbar_width
            + self._COLORBAR_TICK_GAP
            + self._COLORBAR_TICK_LEN
            + self._colorbar_label_width()
        )
        if self.colorbar_title:
            band += self._label_font_size + 6
        return band

    @property
    def cell_width(self) -> float:
        return self.plot_width / self._n_cols

    @property
    def cell_height(self) -> float:
        return self.plot_height / self._n_rows

    @property
    def cell_gap_x(self) -> float:
        return self.cell_width * self.cell_gap

    @property
    def cell_gap_y(self) -> float:
        return self.cell_height * self.cell_gap

    @property
    def draw_cell_width(self) -> float:
        return self.cell_width - self.cell_gap_x

    @property
    def draw_cell_height(self) -> float:
        return self.cell_height - self.cell_gap_y

    def _resolve_color_scale(
        self, color_scale: "ColorScale | str | list[str] | None"
    ) -> ColorScale | None:
        """Normalize the color_scale argument into a ColorScale or None.

        A None argument keeps the two-color low/high behavior. A string or
        list is wrapped into a ColorScale spanning the data range.

        Note: the heatmap always pins the color-scale domain to the data
        range (min, max). When a ColorScale is passed in, only its palette
        is reused; its own ``domain`` is discarded so cell colors stay
        aligned with the displayed value range and legend bar.
        """
        if color_scale is None:
            return None
        domain = (self._data_min, self._data_max)
        if isinstance(color_scale, ColorScale):
            return ColorScale(palette=color_scale.palette, domain=domain)
        return ColorScale(palette=color_scale, domain=domain)

    def _value_to_color(self, value: float) -> str:
        if self.color_scale is not None:
            return self.color_scale(value)
        if self._data_range == 0:
            return self.low_color
        t = (value - self._data_min) / self._data_range
        return _lerp_color(self.low_color, self.high_color, t)

    @property
    def representation(self) -> G:
        result = G(
            transform=f"translate({self.left_padding}, {self.top_padding})",
        )

        grid_color = self.theme.grid_color
        label_color = self.theme.title_color
        font_family = self.theme.title_font_family

        label_font_size = self._label_font_size
        for row_idx in range(self._n_rows):
            for col_idx in range(self._n_cols):
                value = self._matrix[row_idx][col_idx]
                fill = self._value_to_color(value)

                x = col_idx * self.cell_width + self.cell_gap_x / 2
                y = row_idx * self.cell_height + self.cell_gap_y / 2

                cell = Path(
                    fill=fill,
                    stroke=grid_color,
                    stroke_width=self.cell_border_width,
                    d=Path.get_path(
                        x,
                        y,
                        self.draw_cell_width,
                        self.draw_cell_height,
                    ),
                )
                result.add_child(cell)

                if self.show_values:
                    text_x = x + self.draw_cell_width / 2
                    text_y = y + self.draw_cell_height / 2
                    formatted = format(value, self.value_format)

                    from charted.utils.colors import get_contrast_color

                    text_color = get_contrast_color(fill)

                    result.add_child(
                        Text(
                            text=formatted,
                            x=text_x,
                            y=text_y,
                            fill=text_color,
                            font_family=font_family,
                            font_size=label_font_size,
                            text_anchor="middle",
                            dominant_baseline="central",
                        )
                    )

        for col_idx in range(self._n_cols):
            label_x = col_idx * self.cell_width + self.cell_width / 2
            result.add_child(
                Text(
                    text=self._x_labels[col_idx],
                    x=label_x,
                    y=-self.cell_gap_y,
                    fill=label_color,
                    font_family=font_family,
                    font_size=label_font_size,
                    text_anchor="middle",
                    dominant_baseline="bottom",
                )
            )

        for row_idx in range(self._n_rows):
            label_y = row_idx * self.cell_height + self.cell_height / 2
            result.add_child(
                Text(
                    text=self._y_labels[row_idx],
                    x=-self.cell_gap_x,
                    y=label_y,
                    fill=label_color,
                    font_family=font_family,
                    font_size=label_font_size,
                    text_anchor="end",
                    dominant_baseline="central",
                )
            )

        self._add_colorbar(result, label_color, font_family)

        return result

    def _colorbar_color_at(self, t: float) -> str:
        """Colour at fraction ``t`` (0 = data min, 1 = data max)."""
        if self.color_scale is not None:
            return self._value_to_color(self._data_min + t * self._data_range)
        return _lerp_color(self.low_color, self.high_color, t)

    def _add_colorbar(self, result: G, label_color: str, font_family: str) -> None:
        """Render a gradient colorbar with tick marks, labels and a title.

        Drawn in the right-hand band reserved by ``_legend_layout_extent``.
        The strip runs from the data max at the top to the data min at the
        bottom. ``colorbar_ticks`` evenly spaced labels (including both
        endpoints) annotate the scale, each with a short tick mark.
        """
        bar_x = self.plot_width + self._COLORBAR_GAP
        bar_y = 0
        bar_width = self.colorbar_width
        bar_height = self.plot_height
        font_size = self._label_font_size

        # Gradient strip: many thin bands so the transition reads as smooth.
        n_stops = 64
        stop_height = bar_height / n_stops
        for i in range(n_stops):
            # i = 0 is the top band -> data max; i = n_stops-1 -> data min.
            t = 1.0 - (i / (n_stops - 1) if n_stops > 1 else 0)
            result.add_child(
                Path(
                    fill=self._colorbar_color_at(t),
                    d=Path.get_path(
                        bar_x,
                        bar_y + i * stop_height,
                        bar_width,
                        # Overlap by 1px to avoid hairline seams between bands.
                        stop_height + 1,
                    ),
                )
            )

        # Outline around the strip for a crisp edge.
        result.add_child(
            Path(
                fill="none",
                stroke=label_color,
                stroke_width=0.75,
                d=Path.get_path(bar_x, bar_y, bar_width, bar_height),
            )
        )

        # Tick marks + labels.
        tick_x_end = bar_x + bar_width
        for i in range(self.colorbar_ticks):
            frac = i / (self.colorbar_ticks - 1)
            value = self._data_min + frac * self._data_range
            # frac = 0 is data min -> bottom of the strip.
            ty = bar_y + bar_height * (1.0 - frac)
            result.add_child(
                Path(
                    stroke=label_color,
                    stroke_width=0.75,
                    d=" ".join(
                        [
                            f"M{tick_x_end} {ty}",
                            f"h{self._COLORBAR_TICK_LEN}",
                        ]
                    ),
                )
            )
            result.add_child(
                Text(
                    text=format(value, self.value_format),
                    x=tick_x_end + self._COLORBAR_TICK_LEN + self._COLORBAR_TICK_GAP,
                    y=ty,
                    fill=label_color,
                    font_family=font_family,
                    font_size=font_size,
                    text_anchor="start",
                    dominant_baseline="central",
                )
            )

        # Optional vertical title to the right of the tick labels.
        if self.colorbar_title:
            title_x = (
                tick_x_end
                + self._COLORBAR_TICK_LEN
                + self._COLORBAR_TICK_GAP
                + self._colorbar_label_width()
                + font_size
            )
            title_y = bar_y + bar_height / 2
            result.add_child(
                Text(
                    text=self.colorbar_title,
                    x=title_x,
                    y=title_y,
                    fill=label_color,
                    font_family=font_family,
                    font_size=font_size,
                    text_anchor="middle",
                    dominant_baseline="central",
                    transform=f"rotate(-90 {title_x} {title_y})",
                )
            )

    @property
    def legend(self) -> None:
        return None
