"""Chart styling module.

Extracts styling and theming responsibilities from the Chart class to improve
maintainability and testability.
"""

from typing import Any

from charted.config import get_chart_theme, load_config
from charted.html.element import Text
from charted.utils.colors import generate_complementary_colors
from charted.utils.defaults import DEFAULT_COLORS
from charted.utils.helpers import calculate_text_dimensions
from charted.utils.types import MeasuredText, SeriesStyleConfig
from charted.utils.themes import Theme


class ChartStyling:
    """Encapsulates chart styling, theming, and legend management.

    This class handles all styling-related responsibilities that were previously
    in the Chart base class, including:
    - Theme loading and application
    - Color palette generation
    - Legend rendering
    - Title styling

    Attributes:
        theme: Applied theme configuration
        colors: Auto-generated color palette for series
        title: Chart title styling
        legend_position: Legend position ('topright' or 'topleft')
    """

    def __init__(
        self,
        theme: Theme | None = None,
        colors: list[str] | None = None,
        title: str | None = None,
        series_names: list[str] | None = None,
        legend: bool = True,
        legend_position: str = "topright",
        chart_type: str | None = None,
    ):
        """Initialize chart styling.

        Args:
            theme: Theme configuration or None for default
            colors: Custom color palette or None for auto-generation
            title: Chart title text
            series_names: Names of data series for legend
            legend: Whether to show legend
            legend_position: Legend position ('topright' or 'topleft')
            chart_type: Chart type for theme overrides
        """
        # Load theme (may be overridden by chart_type)
        self.theme = Theme.load(theme)

        if chart_type:
            self._apply_chart_theme_override(chart_type)

        self.h_padding = self.theme["padding"]["h_padding"]
        self.v_padding = self.theme["padding"]["v_padding"]

        # Initialize colors
        self._colors: list[str] = []
        self.colors = colors or []

        # Title and legend
        self.title = title
        self.series_names = series_names
        self.legend_enabled = legend
        self.legend_position = legend_position

    def _apply_chart_theme_override(self, chart_type: str) -> None:
        """Apply chart-type-specific theme overrides.

        Args:
            chart_type: Chart type name (e.g., 'bar', 'line', 'pie')
        """
        config = load_config()
        chart_override = get_chart_theme(config, chart_type)
        if chart_override:
            chart_theme = Theme.load(chart_override)
            # Merge: chart override takes precedence over base theme
            for key in self.theme:
                if key not in chart_theme:
                    chart_theme[key] = self.theme[key]
                elif isinstance(self.theme[key], dict) and isinstance(
                    chart_theme[key], dict
                ):
                    for subkey in self.theme[key]:
                        if subkey not in chart_theme[key]:
                            chart_theme[key][subkey] = self.theme[key][subkey]
            self.theme = chart_theme

    @property
    def colors(self) -> list[str]:
        """Get color palette for series."""
        return self._colors

    @colors.setter
    def colors(self, colors: list[str] | None = None) -> None:
        """Generate or set color palette based on series count.

        Args:
            colors: Custom colors or None to auto-generate
        """
        if not colors:
            colors = [*DEFAULT_COLORS]
        self._colors = colors

    def update_colors_for_series(self, series_count: int) -> None:
        """Extend color palette if needed for series count.

        Args:
            series_count: Number of data series
        """
        target = series_count
        new_colors = [*self._colors]

        while target > len(new_colors):
            for color in generate_complementary_colors(self._colors):
                if len(new_colors) >= target:
                    break
                new_colors.append(color)

        self._colors = new_colors

    @property
    def title_style(self) -> dict | None:
        """Get title styling configuration from theme."""
        if not self.theme.get("title"):
            return None
        return {
            "font_color": self.theme["title"]["font_color"],
            "font_family": self.theme["title"]["font_family"],
            "font_weight": self.theme["title"]["font_weight"],
            "font_size": self.theme["title"]["font_size"],
        }

    @property
    def legend_config(self) -> dict | None:
        """Get legend configuration from theme."""
        if not self.legend_enabled or not self.theme.get("legend"):
            return None
        return self.theme["legend"]

    def create_legend(
        self,
        series_names: list[str],
        colors: list[str],
        x0: float,
        y0: float,
        plot_width: float,
        plot_left: float,
        plot_right: float,
        top_padding: float,
    ) -> Any | None:
        """Create legend element.

        Args:
            series_names: Names of series to display
            colors: Colors for each series
            x0: Legend anchor x position
            y0: Legend anchor y position
            plot_width: Available plot width
            plot_left: Left edge of plot area
            plot_right: Right edge of plot area
            top_padding: Top padding value

        Returns:
            Legend G element or None if no legend configured
        """
        legend_config = self.legend_config
        if not legend_config or not series_names:
            return None

        from charted.html.element import G, Rect

        legend_entries = [
            calculate_text_dimensions(x, font_size=legend_config["font_size"])
            for x in series_names
        ]
        icon_height = max(x.height for x in legend_entries)
        legend_width = max(x.width for x in legend_entries) + icon_height + 2
        legend_height = len(legend_entries) * (icon_height + 2)

        # Position legend fully inside plot borders
        pad = legend_config["legend_padding"]
        inset = 4
        positions = {
            "topright": {
                "x0": plot_right - inset - legend_width * (1 + pad / 2),
                "y0": top_padding + inset + legend_height * (pad / 2),
            },
            "topleft": {
                "x0": plot_left + inset + legend_width * (pad / 2),
                "y0": top_padding + inset + legend_height * (pad / 2),
            },
        }

        position = positions.get(legend_config["position"], None)
        if not position:
            raise Exception("Invalid legend position.")

        x_pos, y_pos = position["x0"], position["y0"]

        legend = G()
        legend.add_child(
            Rect(
                transform=None,  # Will be set by caller
                x=x_pos,
                y=y_pos,
                width=legend_width * (1 + legend_config["legend_padding"]),
                height=legend_height * (1 + legend_config["legend_padding"]),
                fill="#ffffff",
                stroke="#CCCCCC",
            )
        )

        for i, (legend_text, color) in enumerate(zip(legend_entries, colors)):
            h = legend_text.height
            g = G(transform=None)  # Will be set by caller
            y = y_pos + (i * h)
            rect = Rect(y=y - h, x=x_pos, width=h, height=h, fill=color)
            text = Text(
                y=y - (h / 4),
                x=x_pos + 2 + h,
                text=legend_text.text,
                font_size=legend_config["font_size"],
                font_family=self.theme["title"]["font_family"],
            )
            g.add_children(rect, text)
            legend.add_child(g)

        return legend
