"""Chart layout configuration module.

Extracts layout and dimension calculation responsibilities from the Chart class
to improve maintainability and testability.
"""

from dataclasses import dataclass

from charted.utils.helpers import calculate_rotation_angle, calculate_text_dimensions, rotate_coordinate
from charted.utils.types import MeasuredText


@dataclass
class Dimensions:
    """Chart dimensions as a value object.

    Encapsulates width, height, and related calculations to replace
    repeated parameter pairs across chart constructors.

    Attributes:
        width: Chart width in pixels
        height: Chart height in pixels
        h_padding: Horizontal padding ratio (0.0-1.0)
        v_padding: Vertical padding ratio (0.0-1.0)
    """
    width: float = 500
    height: float = 500
    h_padding: float = 0.08
    v_padding: float = 0.08

    @property
    def h_pad(self) -> float:
        """Calculate horizontal padding in pixels."""
        return self.h_padding * self.width

    @property
    def v_pad(self) -> float:
        """Calculate vertical padding in pixels."""
        return self.v_padding * self.height

    @property
    def plot_width(self) -> float:
        """Calculate available plot width (excluding horizontal padding)."""
        # Note: full left/right padding calculation requires label widths,
        # so this is a simplified version. Use LayoutConfig.plot_width for full calculation.
        return self.width - (self.h_pad * 2)

    @property
    def plot_height(self) -> float:
        """Calculate available plot height (excluding vertical padding)."""
        # Note: full top/bottom padding calculation requires title/label heights,
        # so this is a simplified version. Use LayoutConfig.plot_height for full calculation.
        return self.height - (self.v_pad * 2)


class LayoutConfig:
    """Encapsulates layout calculations and padding management.

    This class handles all layout-related responsibilities that were previously
    in the Chart base class, including:
    - Padding calculations
    - Plot dimension calculations  
    - Label rotation calculations
    - Viewbox calculations

    Attributes:
        dimensions: Dimensions value object with width/height/padding
        x_labels: X-axis labels with measured text
        y_labels: Y-axis labels with measured text
        title: Chart title with measured text
    """

    def __init__(
        self,
        width: float = 500,
        height: float = 500,
        h_padding: float = 0.08,
        v_padding: float = 0.08,
        x_labels: list[str] | None = None,
        y_labels: list[str] | None = None,
        title: str | None = None,
        title_font_family: str = "Arial",
        title_font_size: int = 16,
    ):
        """Initialize layout configuration.

        Args:
            width: Chart width in pixels
            height: Chart height in pixels
            h_padding: Horizontal padding ratio (0.0-1.0)
            v_padding: Vertical padding ratio (0.0-1.0)
            x_labels: X-axis labels
            y_labels: Y-axis labels
            title: Chart title text
            title_font_family: Font family for title
            title_font_size: Font size for title
        """
        self.dimensions = Dimensions(
            width=width,
            height=height,
            h_padding=h_padding,
            v_padding=v_padding,
        )

        # Font settings for title/label measurement (must be set before labels/title)
        self.title_font_family = title_font_family
        self.title_font_size = title_font_size

        self._x_labels: list[MeasuredText] | None = None
        self._y_labels: list[MeasuredText] | None = None
        self._title: MeasuredText | None = None

        # Set labels and title (triggers measurement)
        self.x_labels = x_labels
        self.y_labels = y_labels
        self.title = title

    @property
    def h_padding(self) -> float:
        """Get horizontal padding ratio."""
        return self.dimensions.h_padding

    @h_padding.setter
    def h_padding(self, value: float) -> None:
        """Set horizontal padding ratio."""
        if value > 1:
            raise ValueError("h_padding must be <= 1.0")
        self.dimensions.h_padding = value

    @property
    def v_padding(self) -> float:
        """Get vertical padding ratio."""
        return self.dimensions.v_padding

    @v_padding.setter
    def v_padding(self, value: float) -> None:
        """Set vertical padding ratio."""
        if value > 1:
            raise ValueError("v_padding must be <= 1.0")
        self.dimensions.v_padding = value

    @property
    def width(self) -> float:
        """Get chart width."""
        return self.dimensions.width

    @width.setter
    def width(self, value: float) -> None:
        """Set chart width."""
        if value < 0:
            raise ValueError("width must be >= 0")
        self.dimensions.width = value

    @property
    def height(self) -> float:
        """Get chart height."""
        return self.dimensions.height

    @height.setter
    def height(self, value: float) -> None:
        """Set chart height."""
        if value < 0:
            raise ValueError("height must be >= 0")
        self.dimensions.height = value

    @property
    def h_pad(self) -> float:
        """Get horizontal padding in pixels."""
        return self.dimensions.h_pad

    @property
    def v_pad(self) -> float:
        """Get vertical padding in pixels."""
        return self.dimensions.v_pad

    @property
    def left_padding(self) -> float:
        """Calculate total left padding (h_pad + y_labels width)."""
        labels = self.y_labels

        if not labels:
            # Would need data to calculate - return just h_pad for now
            return self.h_pad

        max_width = 0.0
        for label in labels:
            if hasattr(label, "width"):
                width = label.width
            else:
                width = calculate_text_dimensions(str(label)).width
            if width > max_width:
                max_width = width

        return self.h_pad + max_width

    @property
    def right_padding(self) -> float:
        """Calculate total right padding."""
        return self.h_pad

    @property
    def top_padding(self) -> float:
        """Calculate total top padding (v_pad + title height)."""
        offset = 0
        if self._title:
            offset += self._title.height * 1.5
        return self.v_pad + offset

    @property
    def bottom_padding(self) -> float:
        """Calculate total bottom padding (v_pad + rotated labels)."""
        if not self.x_label_rotation:
            return self.v_pad

        rotation_angle, width = self.x_label_rotation
        x, y = (width, 0)
        _, dy = rotate_coordinate(x, y, rotation_angle)
        return self.v_pad + abs((dy - y))

    @property
    def plot_width(self) -> float:
        """Get available plot width."""
        return self.dimensions.plot_width

    @property
    def plot_height(self) -> float:
        """Get available plot height."""
        return self.dimensions.plot_height

    @property
    def x_labels(self) -> list[MeasuredText] | None:
        """Get measured X-axis labels."""
        return self._x_labels

    @x_labels.setter
    def x_labels(self, labels: list[str] | None) -> None:
        """Set and measure X-axis labels."""
        if labels:
            self._x_labels = [calculate_text_dimensions(label) for label in labels]
        else:
            self._x_labels = None

    @property
    def y_labels(self) -> list[MeasuredText] | None:
        """Get measured Y-axis labels."""
        return self._y_labels

    @y_labels.setter
    def y_labels(self, labels: list[str] | None) -> None:
        """Set and measure Y-axis labels."""
        if labels:
            self._y_labels = [calculate_text_dimensions(label) for label in labels]
        else:
            self._y_labels = None

    @property
    def x_label_rotation(self) -> tuple[float, float] | None:
        """Calculate optimal X-axis label rotation angle.

        Returns:
            Tuple of (rotation_angle, max_width) or None if no labels
        """
        if not self.x_labels:
            return None

        # Note: x_width needs to come from Chart class
        rotation_angle = 0
        width = 0
        for label in self.x_labels:
            # Placeholder - x_width will be provided by Chart
            x_width = 50  # Default placeholder
            angle = calculate_rotation_angle(label.width, x_width)
            width = max(width, label.width)
            if angle and (angle > rotation_angle):
                rotation_angle = max(angle, rotation_angle)

        return rotation_angle, width

    @property
    def title(self) -> MeasuredText | None:
        """Get measured chart title."""
        return self._title

    @title.setter
    def title(self, text: str | None) -> None:
        """Set and measure chart title."""
        if text:
            self._title = calculate_text_dimensions(
                text,
                font=self.title_font_family,
                font_size=self.title_font_size,
            )
        else:
            self._title = None

    def calculate_viewbox(self, width: float, height: float) -> list:
        """Calculate SVG viewbox for the chart.

        Args:
            width: Chart width
            height: Chart height

        Returns:
            Viewbox specification as [min_x, min_y, width, height]
        """
        return [0, 0, width, height]
