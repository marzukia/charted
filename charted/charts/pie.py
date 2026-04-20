from __future__ import annotations

import math
from typing import TYPE_CHECKING

from charted.charts.chart import Chart
from charted.html.element import G, Path, Text, Tspan
from charted.utils.defaults import DEFAULT_FONT


if TYPE_CHECKING:
    from charted.utils.themes import Theme
    from charted.utils.types import Labels


class PieChart(Chart):
    """A pie chart representing categorical data as slices of a circle.

        Unlike other charts that use x/y data, a pie chart operates on a single
    dataset where values represent portions of a whole.
    """

    def __init__(
        self,
        values: list[float],
        labels: Labels = None,
        colors: list[str] | None = None,
        width: float = 500,
        height: float = 500,
        title: str | None = None,
        theme: Theme | None = None,
        inner_radius: float = 0.0,
    ):
        """Initialize a PieChart.

        Args:
            values: List of numeric values representing slice sizes.
            labels: Optional list of category labels.
            colors: Optional list of colors for slices.
            width: SVG width in pixels.
            height: SVG height in pixels.
            title: Optional chart title.
            theme: Optional theme for styling.
            inner_radius: Inner radius for doughnut mode

            (0.0-1.0, 0 = pie, >0 = doughnut).

        Raises:
            ValueError: If values list is empty, contains
            only zeros, or all values are invalid.
            ValueError: If values contain negative numbers or NaN.
        """
        # Validate input is not empty
        if not values:
            raise ValueError("values list cannot be empty")

        # Validate and process each value
        validated_values: list[float] = []
        for v in values:
            if not isinstance(v, (int, float)):
                raise TypeError(
                    f"All values must be numbers, got {type(v).__name__}: {v!r}"
                )
            if math.isnan(v):
                raise ValueError(f"NaN values are not allowed: {v!r}")
            if v < 0:
                raise ValueError(f"Negative values are not allowed: {v!r}")
            validated_values.append(float(v))

        self._raw_values = validated_values

        # Store parameters (use _custom_colors to avoid triggering property setter)
        self._custom_colors = colors if colors is not None else None
        self.labels = labels if labels is not None else []
        self.inner_radius = inner_radius

        # Validate inner_radius range
        if not 0.0 <= inner_radius <= 1.0:
            raise ValueError(
                f"inner_radius must be between 0.0 and 1.0, got {inner_radius!r}"
            )

        # Calculate total and validate at least one positive value
        total = sum(validated_values)
        if total == 0:
            raise ValueError("At least one value must be greater than 0")

        self._total = total

        # Compute angles for each slice
        self._angles: list[tuple[float, float]] = []
        current_angle = 0.0
        for v in validated_values:
            if v > 0:
                angle_span = (v / total) * 360.0
                self._angles.append((current_angle, current_angle + angle_span))
                current_angle += angle_span
            else:
                # Zero values get a zero-span angle
                self._angles.append((current_angle, current_angle))

        self.render_axes = (
            False  # Set BEFORE super().__init__ to prevent axes from being added
        )
        # Call parent Chart constructor with minimal setup
        # Pie chart doesn't use axes, so we pass minimal data
        self.render_axes = (
            False  # Set BEFORE super().__init__ to prevent axes from being added
        )
        # Expand viewBox to accommodate labels outside the pie
        # Labels are positioned at label_radius = outer_radius * 1.15
        # outer_radius = min(width, height) / 2 * 0.85
        # So we need ~15% extra space on each side
        label_margin = 0.20  # 20% extra space
        expanded_width = width * (1 + label_margin)
        expanded_height = height * (1 + label_margin)
        offset_x = -(label_margin / 2) * width
        offset_y = -(label_margin / 2) * height

        # Call parent Chart constructor with minimal setup
        # Pie chart doesn't use axes, so we pass minimal data
        super().__init__(
            width=expanded_width,
            height=expanded_height,
            x_data=[[0]],
            y_data=[[0]],
            title=title,
            theme=theme,
            x_stacked=False,
        )
        # Override viewBox to shift origin and include label space
        self.kwargs["viewBox"] = (
            f"{offset_x} {offset_y} {expanded_width} {expanded_height}"
        )

        # Disable axes - pie charts don't use x/y axes
        self.render_axes = False

    def _slice_path(
        self,
        cx: float,
        cy: float,
        outer_radius: float,
        start_angle: float,
        end_angle: float,
        inner_radius: float = 0.0,
    ) -> str:
        """Generate SVG path data for a pie slice.

        Uses the convention: 0° = top (12 o'clock), clockwise is positive.

        Args:
            cx, cy: Center coordinates of the pie.
            outer_radius: Outer radius of the slice.
            start_angle, end_angle: Start and end angles in
            degrees (0 = top, clockwise).
            inner_radius: Inner radius for doughnut holes (0 = full slice).

        Returns:
            SVG path data string.
        """
        # Special case: single slice covering entire pie (360°)
        angle_diff = (end_angle - start_angle) % 360
        is_full_circle = abs(angle_diff) < 1e-6 or abs(abs(angle_diff) - 360) < 1e-6

        if is_full_circle and inner_radius == 0:
            # Full pie: simple circle
            return (
                f"M {cx + outer_radius} {cy} "
                f"A {outer_radius} {outer_radius} 0 1 1 "
                f"{cx - outer_radius} {cy} "
                f"A {outer_radius} {outer_radius} 0 1 1 "
                f"{cx + outer_radius} {cy} Z"
            )

        # Convert angles to radians (subtract 90° to align: 0°=top, positive=clockwise)
        start_rad = math.radians(start_angle - 90)
        end_rad = math.radians(end_angle - 90)

        # Calculate outer arc points
        ox1 = cx + outer_radius * math.cos(start_rad)
        oy1 = cy + outer_radius * math.sin(start_rad)
        ox2 = cx + outer_radius * math.cos(end_rad)
        oy2 = cy + outer_radius * math.sin(end_rad)

        # Determine large_arc flag
        large_arc = 1 if angle_diff > 180 else 0

        # Build path
        path_cmds: list[str] = []

        if inner_radius > 0:
            # Doughnut slice with inner hole
            inner_rad = inner_radius * outer_radius
            ix1 = cx + inner_rad * math.cos(start_rad)
            iy1 = cy + inner_rad * math.sin(start_rad)
            ix2 = cx + inner_rad * math.cos(end_rad)
            iy2 = cy + inner_rad * math.sin(end_rad)

            # Start at outer start, arc to outer end, line to inner end,
            # arc back to inner start, line to outer start
            path_cmds = [
                f"M {ox1} {oy1}",
                f"A {outer_radius} {outer_radius} 0 {large_arc} 1 {ox2} {oy2}",
                f"L {ix2} {iy2}",
                f"A {inner_rad} {inner_rad} 0 {large_arc} 0 {ix1} {iy1}",
                "Z",
            ]
        else:
            # Full pie slice (triangle-like with curved edge)
            path_cmds = [
                f"M {cx} {cy}",
                f"L {ox1} {oy1}",
                f"A {outer_radius} {outer_radius} 0 {large_arc} 1 {ox2} {oy2}",
                "Z",
            ]

        return " ".join(path_cmds)

    def _render_slices(self) -> G:
        """Render the pie slices and labels."""
        slices_g = G()

        cx = self.width / 2
        cy = self.height / 2
        # Calculate outer radius based on chart dimensions
        outer_radius = min(cx, cy) * 0.85  # Leave room for labels

        # Calculate label positions
        label_radius = outer_radius * 1.15  # Labels just outside pie

        for i, angle_pair in enumerate(self._angles):
            start_angle, end_angle = angle_pair
            mid_angle = (start_angle + end_angle) / 2

            # Skip zero-size slices for rendering
            if start_angle == end_angle:
                continue

            # Create slice path
            slice_path = self._slice_path(
                cx, cy, outer_radius, start_angle, end_angle, self.inner_radius
            )

            # Create path element
            path_elem = Path(
                d=slice_path,
                fill=self.colors[i % len(self.colors)],
                stroke="#ffffff",
                stroke_width=2,
            )
            slices_g.add_child(path_elem)

            # Calculate label position
            label_x = cx + label_radius * math.cos(math.radians(mid_angle - 90))
            label_y = cy + label_radius * math.sin(math.radians(mid_angle - 90))

            # Get label text and value
            label_text = self.labels[i] if i < len(self.labels) else f"Slice {i + 1}"
            value = self._raw_values[i]
            percentage = (value / self._total) * 100

            # Format text: label\n<value>\n<%>
            # Wrap the label text to fit within chart width
            label_lines = [label_text]
            value_line = str(value)
            percent_line = f"{percentage:.1f}%"

            # Create text element with proper font
            text_elem = Text(
                x=label_x,
                y=label_y,
                text_anchor="middle",
                dominant_baseline="middle",
                fill="white",
                font_size=11,
                font_weight="600",
                font_family=DEFAULT_FONT,
            )

            # Combine all lines: wrapped label + value + percentage
            all_lines = label_lines + [value_line, percent_line]

            # Add each line as a tspan for proper line breaks in SVG
            line_height = 14  # Slightly more than font_size for line spacing
            for idx, line in enumerate(all_lines):
                y_offset = (idx - len(all_lines) // 2) * line_height
                tspan = Tspan(
                    text=line,
                    x=label_x,
                    y=label_y + y_offset,
                )
                text_elem.add_child(tspan)

            slices_g.add_child(text_elem)

        return slices_g

    def _split_camel_case(self, text: str) -> list[str]:
        """Split a camelCase or PascalCase string into words.

        Examples:
            "VeryLongCategoryName" -> ["Very", "Long", "Category", "Name"]
            "XMLParser" -> ["XML", "Parser"]

        Args:
            text: A camelCase or PascalCase string.

        Returns:
            List of words extracted from the camelCase string.
        """
        if not text:
            return []

        # Pattern matches:
        # 1. Boundaries before uppercase followed by lowercase (e.g., "Category")
        # 2. Boundaries before uppercase followed by uppercase + lowercase (e.g., "XMLParser" -> "XML", "Parser")
        import re

        # Insert space before uppercase letters that follow lowercase letters
        # or before uppercase letters followed by lowercase (start of new word)
        result = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
        result = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", result)
        return result.split()

    def _break_long_word(self, text: str, max_width: int) -> list[str]:
        """Break a long word into multiple lines by character.

        Uses binary search to find optimal break points that maximize
        utilization of max_width while ensuring each line fits.

        Args:
            text: The text to break.
            max_width: Maximum width in pixels.

        Returns:
            List of lines, each fitting within max_width.
        """
        from charted.utils.helpers import calculate_text_dimensions

        if not text:
            return [""]

        # Check if entire text fits
        text_metrics = calculate_text_dimensions(text)
        if text_metrics.width <= max_width:
            return [text]

        # Binary search for optimal break point
        lines = []
        remaining = text

        while remaining:
            # Binary search for the longest prefix that fits
            lo, hi = 1, len(remaining)
            best = 1

            while lo <= hi:
                mid = (lo + hi) // 2
                substring = remaining[:mid]
                metrics = calculate_text_dimensions(substring)
                if metrics.width <= max_width:
                    best = mid
                    lo = mid + 1
                else:
                    hi = mid - 1

            # Take the best fit
            lines.append(remaining[:best])
            remaining = remaining[best:]

            # Safety check to avoid infinite loop
            if best == 0 or not remaining:
                break

        return lines if lines else [text]

    def _wrap_text(self, text: str, max_width: int = 120) -> list[str]:
        """Wrap text to fit within a maximum width using actual font metrics.

        Uses calculate_text_dimensions for precise width measurement based on
        the actual font being used (Inter, 11pt).

        Breaks text at:
        1. Word boundaries (spaces)
        2. CamelCase boundaries (e.g., "VeryLongName" → "VeryLong\nName")
        3. Character boundaries (last resort)

        Args:
            text: The text to wrap.
            max_width: Maximum width in pixels.

        Returns:
            List of lines, each fitting within max_width.
        """
        if not text:
            return [""]

        from charted.utils.helpers import calculate_text_dimensions

        # Check if entire text fits
        text_metrics = calculate_text_dimensions(text)
        if text_metrics.width <= max_width:
            return [text]

        # First, try to split at word boundaries (spaces)
        words = text.split()
        if len(words) > 1:
            # Multi-word text - wrap at word boundaries
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                line_metrics = calculate_text_dimensions(test_line)
                if line_metrics.width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    # Check if word itself fits
                    word_metrics = calculate_text_dimensions(word)
                    if word_metrics.width <= max_width:
                        current_line = word
                    else:
                        # Word too long - break it (see below)
                        sub_lines = self._break_long_word(word, max_width)
                        lines.extend(sub_lines[:-1])
                        current_line = sub_lines[-1] if sub_lines else ""
            if current_line:
                lines.append(current_line)
            return lines if lines else [text]

        # Single "word" - try camelCase splitting
        camel_words = self._split_camel_case(text)
        if len(camel_words) > 1:
            lines = []
            current_line = ""
            for word in camel_words:
                test_line = current_line + " " + word if current_line else word
                line_metrics = calculate_text_dimensions(test_line)
                if line_metrics.width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    word_metrics = calculate_text_dimensions(word)
                    if word_metrics.width <= max_width:
                        current_line = word
                    else:
                        sub_lines = self._break_long_word(word, max_width)
                        lines.extend(sub_lines[:-1])
                        current_line = sub_lines[-1] if sub_lines else ""
            if current_line:
                lines.append(current_line)
            return lines if lines else [text]

        # Last resort: character-by-character breaking
        return self._break_long_word(text, max_width)

    @property
    def representation(self) -> G:
        """Render the pie chart."""
        return self._render_slices()

    def _get_legend_items(self) -> list[tuple[str, str]]:
        """Return list of (label, color) tuples for legend."""
        items = []
        for i, _ in enumerate(self._angles):
            label = self.labels[i] if i < len(self.labels) else f"Slice {i + 1}"
            items.append((label, self.colors[i % len(self.colors)]))
        return items

    @property
    def x_stacked(self) -> bool:
        """Pie chart doesn't use x_stacked."""
        return False
