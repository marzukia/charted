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
        has_x_axis_label: bool = False,
        has_y_axis_label: bool = False,
    ):
        self.width = width
        self.height = height
        self.h_padding = h_padding
        self.v_padding = v_padding
        self.x_labels = x_labels or []
        self.y_labels = y_labels or []
        self.title = title
        self.subtitle = subtitle
        self.has_x_axis_label = has_x_axis_label
        self.has_y_axis_label = has_y_axis_label

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
    def right_padding(self) -> float:
        """Calculate right padding.

        Returns:
            Right padding in pixels (base horizontal padding).
        """
        return self.h_padding * self.width

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

        return v_pad + offset

    @property
    def bottom_padding(self) -> float:
        """Calculate bottom padding including rotated label space.

        Returns:
            Total bottom padding in pixels (base padding + rotated label space if any).
        """
        base = self.v_padding * self.height

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
