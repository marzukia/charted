"""Layout engine for calculating chart dimensions and padding.

Extracted from Chart class to reduce coupling and improve testability.
This module encapsulates all layout calculation logic in a focused component.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import MeasuredText


class LayoutEngine:
    """Calculates chart layout dimensions based on content.

    Replaces scattered layout calculation methods in Chart class with
    a single focused component. All padding and dimension calculations
    are delegated to this class.

    Attributes:
        width: Total chart width in pixels.
        height: Total chart height in pixels.
        h_padding: Horizontal padding as fraction of width.
        v_padding: Vertical padding as fraction of height.
        x_labels: X-axis labels with width information.
        y_labels: Y-axis labels with width information.
        title: Chart title with height information (optional).
    """

    def __init__(
        self,
        width: float,
        height: float,
        h_padding: float,
        v_padding: float,
        x_labels: list["MeasuredText"] | None = None,
        y_labels: list["MeasuredText"] | None = None,
        title: "MeasuredText | None" = None,
        subtitle: "MeasuredText | None" = None,
        subtitle_leading: float = 0.0,
        has_x_axis_label: bool = False,
        has_y_axis_label: bool = False,
        legend_position: str = "none",
        legend_extent: float = 0.0,
    ):
        self.width = width
        self.height = height
        self.h_padding = h_padding
        self.v_padding = v_padding
        self.x_labels = x_labels or []
        self.y_labels = y_labels or []
        self.title = title
        self.subtitle = subtitle
        self.subtitle_leading = max(0.0, float(subtitle_leading))
        self.has_x_axis_label = has_x_axis_label
        self.has_y_axis_label = has_y_axis_label
        # Outside-the-plot legend placement. ``legend_position`` is one of
        # 'right' | 'bottom' | 'top' | 'none' and ``legend_extent`` is the
        # pixel band reserved on that side. 'none'/zero extent leaves all
        # padding untouched, so existing layouts are byte-for-byte preserved.
        self.legend_position = legend_position or "none"
        self.legend_extent = max(0.0, float(legend_extent))

    @property
    def plot_width(self) -> float:
        """Calculate available plot area width.

        Returns:
            Width of the plot area (total width minus left and right padding).
        """
        return self.width - (self.left_padding + self.right_padding)

    @property
    def plot_height(self) -> float:
        """Calculate available plot area height.

        Returns:
            Height of the plot area (total height minus top and bottom padding).
        """
        return self.height - (self.top_padding + self.bottom_padding)

    @property
    def left_padding(self) -> float:
        """Calculate left padding for y-axis labels.

        Returns:
            Total left padding in pixels (base padding + max label width).
        """
        h_pad = self.h_padding * self.width

        # Extra space for y-axis title label (rendered vertically to the left)
        if self.has_y_axis_label:
            h_pad += 16

        if not self.y_labels:
            return h_pad

        max_width = 0.0
        for label in self.y_labels:
            width = label.width if hasattr(label, "width") else 0
            if width > max_width:
                max_width = width

        return h_pad + max_width

    @property
    def _legend_band(self) -> float:
        """Pixel band reserved for an outside-the-plot legend, or 0."""
        if self.legend_position in ("right", "bottom", "top"):
            return self.legend_extent
        return 0.0

    @property
    def right_padding(self) -> float:
        """Calculate right padding.

        Returns:
            Right padding in pixels (base horizontal padding plus any
            right-placed legend band).
        """
        pad = self.h_padding * self.width
        if self.legend_position == "right":
            pad += self._legend_band
        return pad

    @property
    def top_padding(self) -> float:
        """Calculate top padding including title space.

        Returns:
            Total top padding in pixels (base padding + title height if present).
        """
        v_pad = self.v_padding * self.height
        offset = 0

        if self.title:
            offset += self.title.height * 1.5

        # Reserve room for the subtitle plus a gap so it never overlaps the
        # plot grid. The subtitle is rendered below the title.
        if self.subtitle:
            offset += self.subtitle.height * 1.5
            # Reserve the configurable leading gap between title and subtitle
            # so the extra spacing never pushes the subtitle into the plot.
            if self.title:
                offset += self.subtitle_leading

        # Reserve a band above the plot for a top-placed legend.
        if self.legend_position == "top":
            offset += self._legend_band

        return v_pad + offset

    @property
    def bottom_padding(self) -> float:
        """Calculate bottom padding including rotated label space.

        Returns:
            Total bottom padding in pixels (base padding + rotated label space if any).
        """
        base = self.v_padding * self.height

        # Reserve a band below the plot for a bottom-placed legend. The legend
        # is drawn at the chart's bottom edge, so the band must clear the
        # x-axis tick labels. Those labels sit DEFAULT_PADDING below the plot
        # plus their own font height; guarantee the base padding covers that
        # before the legend band is appended, otherwise a thin v_padding lets
        # the labels spill into the legend row.
        if self.legend_position == "bottom":
            if self.x_labels:
                from ..constants import DEFAULT_PADDING
                from .defaults import DEFAULT_FONT_SIZE

                tick_label_band = DEFAULT_PADDING + DEFAULT_FONT_SIZE
                base = max(base, tick_label_band)
            base += self._legend_band

        # Extra space for x-axis title label (rendered below tick labels)
        if self.has_x_axis_label:
            base += 18

        rotation = self.x_label_rotation

        if not rotation:
            return base

        _, width = rotation
        from .helpers import rotate_coordinate

        x, y = (width, 0)
        _, dy = rotate_coordinate(x, y, rotation[0])

        return base + abs((dy - y))

    @property
    def x_label_rotation(self) -> tuple[float, float] | None:
        """Calculate optimal rotation angle for x-axis labels.

        Returns:
            Tuple of (rotation_angle, max_label_width) if rotation needed,
            or None if labels fit without rotation.
        """
        if not self.x_labels:
            return None

        x_width = self.plot_width / len(self.x_labels) if self.x_labels else 0

        from .helpers import calculate_rotation_angle

        rotation_angle = 0
        width = 0

        for label in self.x_labels:
            angle = calculate_rotation_angle(label.width, x_width)
            width = max(width, label.width)
            if angle and angle > rotation_angle:
                rotation_angle = max(angle, rotation_angle)

        return (rotation_angle, width) if rotation_angle else None

    def get_base_transform(self) -> list:
        """Get base transformation matrix for chart coordinates.

        Returns:
            List of transformation operations for SVG coordinate system.
        """
        from .transform import rotate, scale, translate

        h_pad = self.h_padding * self.width

        return [
            translate(-h_pad, -self.bottom_padding),
            rotate(180, self.width / 2, self.height / 2),
            scale(-1, 1),
            translate(-self.plot_width, 0),
        ]

    def calculate_x_offset(self) -> float:
        """Calculate x-offset for ordinal charts.

        For ordinal charts (no explicit x_data), shifts data by one tick width
        so data points sit at the center of their column. For XY charts,
        returns 0 since positions are already correct.

        Returns:
            Offset value (0 for XY charts, tick width for ordinal charts).
        """
        # Note: This requires x_axis reference which is set after initialization
        # Implementation will be updated in Phase 2 when Chart integrates LayoutEngine
        return 0
