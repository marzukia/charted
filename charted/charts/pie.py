"""Pie chart with optional donut mode."""

from __future__ import annotations

import math

from charted.html.element import Path, Svg, Text
from charted.utils.defaults import DEFAULT_COLORS


class PieChart(Svg):
    """Pie chart with optional donut mode.

    Args:
        data: Values for each slice. Single list for one pie.
        labels: Optional labels for each slice.
        width: SVG width in pixels.
        height: SVG height in pixels.
        title: Optional chart title.
        donut: If True, creates a donut chart with a hole in the center.
        donut_radius: Inner radius as fraction of outer radius (0.0-1.0) when donut=True.
        start_angle: Starting angle in degrees (0 = top, increases clockwise).
    """

    def __init__(
        self,
        data: list[float],
        labels: list[str] | None = None,
        width: float = 500,
        height: float = 500,
        title: str | None = None,
        donut: bool = False,
        donut_radius: float = 0.5,
        start_angle: float = 0,
    ):
        super().__init__(
            width=width,
            height=height,
            viewBox=f"0 0 {width} {height}",
        )

        self.data = [max(0, v) for v in data]
        self.labels = labels or [f"Slice {i + 1}" for i in range(len(data))]
        self.width = width
        self.height = height
        self.title = title
        self.donut = donut
        self.donut_radius = max(0.0, min(1.0, donut_radius))
        self.start_angle = start_angle

        colors = self._get_colors(len(data))

        total = sum(self.data)
        if total == 0:
            return

        current_angle = self.start_angle
        outer_r = min(width, height) / 2 * 0.45
        inner_r = outer_r * self.donut_radius if self.donut else 0.0
        cx, cy = width / 2, height / 2

        children = []

        if title:
            title_elem = Text(
                x=cx,
                y=25,
                text=title,
                text_anchor="middle",
                font_size="18",
                font_weight="bold",
            )
            children.append(title_elem)

        for value, color, label in zip(self.data, colors, self.labels):
            if value == 0:
                continue

            slice_angle = (value / total) * 360
            end_angle = current_angle + slice_angle

            path_d = self._slice_path(
                start_angle=current_angle,
                end_angle=end_angle,
                cx=cx,
                cy=cy,
                outer_r=outer_r,
                inner_r=inner_r,
            )

            children.append(Path(d=path_d, fill=color))
            current_angle = end_angle

        for child in children:
            self.add_child(child)

    def _get_colors(self, count: int) -> list[str]:
        """Generate color list for slices."""
        colors = list(DEFAULT_COLORS)
        while len(colors) < count:
            colors.extend(DEFAULT_COLORS)
        return colors[:count]

    def _slice_path(
        self,
        start_angle: float,
        end_angle: float,
        cx: float,
        cy: float,
        outer_r: float,
        inner_r: float,
    ) -> str:
        """Generate SVG path for a pie slice."""
        start_rad = math.radians(start_angle - 90)
        end_rad = math.radians(end_angle - 90)

        x1_outer = cx + outer_r * math.cos(start_rad)
        y1_outer = cy + outer_r * math.sin(start_rad)
        x2_outer = cx + outer_r * math.cos(end_rad)
        y2_outer = cy + outer_r * math.sin(end_rad)

        x1_inner = cx + inner_r * math.cos(start_rad)
        y1_inner = cy + inner_r * math.sin(start_rad)
        x2_inner = cx + inner_r * math.cos(end_rad)
        y2_inner = cy + inner_r * math.sin(end_rad)

        large_arc = 1 if (end_angle - start_angle) % 360 > 180 else 0

        path = []
        path.append(f"M {x1_outer} {y1_outer}")
        path.append(f"A {outer_r} {outer_r} 0 {large_arc} 1 {x2_outer} {y2_outer}")

        if inner_r > 0:
            path.append(f"L {x2_inner} {y2_inner}")
            path.append(f"A {inner_r} {inner_r} 0 {large_arc} 0 {x1_inner} {y1_inner}")
            path.append("Z")
        else:
            path.append(f"L {cx} {cy}")
            path.append("Z")

        return " ".join(path)

    def to_string(self) -> str:
        """Return the SVG as a string."""
        return self.html

    def to_file(self, path: str) -> None:
        """Save the SVG to a file."""
        with open(path, "w") as f:
            f.write(self.html)
