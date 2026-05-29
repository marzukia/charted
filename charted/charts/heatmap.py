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
        low_color: Color for the lowest value in the data (default '#1a6b8f').
        high_color: Color for the highest value in the data (default '#f7a55c').
        color_scale: Optional continuous color scale. Pass a ColorScale, a
            named palette string (e.g. 'viridis'), or a list of hex stops to
            color cells along a multi-stop gradient. Overrides low_color and
            high_color. Defaults to None (two-color low/high behavior).
        show_values: If True, display the numeric value in each cell (default True).
        value_format: Format string for displayed values (default '.1f').
        cell_gap: Gap between cells as fraction of cell size (default 0.04).
        label_font_size: Font size for row/column labels (default 11).

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
        low_color: str = "#5fab9e",
        high_color: str = "#f58b51",
        color_scale: "ColorScale | str | list[str] | None" = None,
        show_values: bool = True,
        value_format: str = ".1f",
        cell_gap: float = 0.04,
        label_font_size: int = 11,
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
        self.low_color = low_color
        self.high_color = high_color
        self.show_values = show_values
        self.value_format = value_format
        self.cell_gap = cell_gap
        self._label_font_size = label_font_size

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
                    stroke_width=0.5,
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

        bar_x = self.plot_width + 10
        bar_y = 0
        bar_width = 20
        bar_height = self.plot_height
        bar_label_gap = 6
        n_stops = 20

        for i in range(n_stops):
            t = i / (n_stops - 1) if n_stops > 1 else 0
            if self.color_scale is not None:
                value = self._data_min + t * self._data_range
                color = self._value_to_color(value)
            else:
                color = _lerp_color(self.low_color, self.high_color, t)
            stop_height = bar_height / n_stops
            result.add_child(
                Path(
                    fill=color,
                    d=Path.get_path(
                        bar_x,
                        bar_y + i * stop_height,
                        bar_width,
                        stop_height + 1,
                    ),
                )
            )

        result.add_child(
            Text(
                text=format(self._data_min, self.value_format),
                x=bar_x + bar_width / 2,
                y=bar_y + bar_height + bar_label_gap,
                fill=label_color,
                font_family=font_family,
                font_size=label_font_size,
                text_anchor="middle",
                dominant_baseline="hanging",
            )
        )
        result.add_child(
            Text(
                text=format(self._data_max, self.value_format),
                x=bar_x + bar_width / 2,
                y=bar_y - bar_label_gap,
                fill=label_color,
                font_family=font_family,
                font_size=label_font_size,
                text_anchor="middle",
                dominant_baseline="bottom",
            )
        )

        return result

    @property
    def legend(self) -> None:
        return None
