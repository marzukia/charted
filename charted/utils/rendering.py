"""Rendering utilities for charted.

Extracted from Chart class to reduce coupling and improve testability.
"""

from urllib.parse import quote

from charted.html.element import G, Path, Rect, Text
from charted.themes.core import Theme
from charted.utils.helpers import calculate_text_dimensions
from charted.utils.transform import translate
from charted.utils.types import MeasuredText


def generate_markdown_image(
    svg_data: str,
    alt_text: str | None,
    title: str | None = None,
    width: str | None = None,
) -> str:
    """Generate markdown markup for an SVG chart.

    Args:
        svg_data: SVG string to embed.
        alt_text: Alternative text for the image.
        title: Chart title (used as fallback for alt_text).
        width: Optional width specification (e.g., '500px' or '100%').

    Returns:
        Markdown image syntax with data URL.
    """
    alt = alt_text or (title if title else "chart")

    # Encode SVG as data URL
    encoded = quote(svg_data)
    data_url = f"data:image/svg+xml,{encoded}"

    if width:
        return f"![{alt}]({data_url}){{width={width}}}"
    return f"![{alt}]({data_url})"


def create_legend_background(
    x: float, y: float, legend_width: float, legend_height: float, padding: float
) -> Rect:
    """Create legend background rectangle.

    Args:
        x: X position of legend.
        y: Y position of legend.
        legend_width: Width of legend content.
        legend_height: Height of legend content.
        padding: Legend padding value.

    Returns:
        Rect element for legend background.
    """
    return Rect(
        transform=translate(
            -(legend_width * padding / 2),
            -(legend_height * padding / 2),
        ),
        x=x,
        y=y,
        width=legend_width * (1 + padding),
        height=legend_height * (1 + padding),
        fill="#ffffff",
        stroke="#CCCCCC",
    )


def calculate_legend_dimensions(
    series_names: list[str], font_size: float, legend_padding: float
) -> tuple[float, float, float, float]:
    """Calculate legend dimensions based on series names.

    Args:
        series_names: List of series names for legend entries.
        font_size: Font size for legend text.
        legend_padding: Padding value for legend.

    Returns:
        Tuple of (legend_width, legend_height, icon_height, entry_count).
    """
    legend_entries = [
        calculate_text_dimensions(name, font_size=font_size) for name in series_names
    ]
    icon_height = max(entry.height for entry in legend_entries)
    legend_width = max(entry.width for entry in legend_entries) + icon_height + 2
    legend_height = len(legend_entries) * (icon_height + 2)

    return legend_width, legend_height, icon_height, len(legend_entries)


def calculate_legend_position(
    position: str,
    plot_right: float,
    plot_left: float,
    legend_width: float,
    legend_height: float,
    top_padding: float,
    inset: float = 4,
    padding: float = 0.5,
) -> tuple[float, float]:
    """Calculate legend position coordinates.

    Args:
        position: Legend position ('topright' or 'topleft').
        plot_right: Right edge of plot area.
        plot_left: Left edge of plot area.
        legend_width: Width of legend.
        legend_height: Height of legend.
        top_padding: Top padding of chart.
        inset: Small inset from plot border.
        padding: Legend padding value.

    Returns:
        Tuple of (x0, y0) coordinates for legend placement.

    Raises:
        Exception: If position is invalid.
    """
    positions = {
        "topright": {
            "x0": plot_right - inset - legend_width * (1 + padding / 2),
            "y0": top_padding + inset + legend_height * (padding / 2),
        },
        "topleft": {
            "x0": plot_left + inset + legend_width * (padding / 2),
            "y0": top_padding + inset + legend_height * (padding / 2),
        },
    }

    result = positions.get(position)
    if not result:
        raise Exception(f"Invalid legend position: {position}")

    return result["x0"], result["y0"]


def create_legend_entry(
    rect_x: float,
    entry_top_y: float,
    text: MeasuredText,
    color: str,
    index: int,
    font_family: str,
    entry_height: float,
) -> G:
    """Create a single legend entry (icon + text).

    Args:
        rect_x: X position for legend icon.
        entry_top_y: Y position of the top of this legend entry.
        text: Legend text measurement.
        color: Color for the legend icon.
        index: Series index.
        font_family: Font family for legend text.
        entry_height: Height for each legend entry.

    Returns:
        G element containing the legend entry.
    """
    h = text.height

    # Icon rectangle - positioned within this entry's vertical space
    rect_y = entry_top_y + (entry_height - h) / 2
    rect = Rect(y=rect_y, x=rect_x, width=h, height=h, fill=color)

    # Legend text - vertically centered with icon
    legend_text = Text(
        y=rect_y + h * 0.75,
        x=rect_x + 2 + h,
        text=text.text,
        font_size=text.height,
        font_family=font_family,
    )

    g = G()
    g.add_children(rect, legend_text)
    return g


def create_legend(
    series_names: list[str],
    colors: list[str],
    theme_config: dict,
    plot_left: float,
    plot_right: float,
    top_padding: float,
) -> G | None:
    """Create complete legend element.

    Args:
        series_names: Names for each series.
        colors: Colors for each series.
        theme_config: Legend configuration from theme.
        plot_left: Left edge of plot area.
        plot_right: Right edge of plot area.
        top_padding: Top padding of chart.

    Returns:
        G element containing legend, or None if no legend should be shown.
    """
    if not theme_config or not series_names:
        return None

    # Handle both dict and Theme object
    if isinstance(theme_config, Theme):
        font_size = getattr(theme_config, "legend_font_size", 12)
        legend_padding = 0.5  # Default
        font_family = getattr(theme_config, "legend_font_family", "Arial")
        position = getattr(theme_config, "legend_position", "topright")
    else:
        font_size = theme_config.get("font_size", 12)
        legend_padding = theme_config.get("legend_padding", 0.5)
        font_family = theme_config.get("font_family", "Arial")
        position = theme_config.get("position", "topright")

    # Calculate dimensions
    legend_width, legend_height, icon_height, entry_count = calculate_legend_dimensions(
        series_names, font_size, legend_padding
    )

    # Calculate position (y0 is center of legend)
    inset = 4
    x0, y0_center = calculate_legend_position(
        position,
        plot_right,
        plot_left,
        legend_width,
        legend_height,
        top_padding,
        inset,
        legend_padding,
    )

    # Calculate actual top of background after transform
    # Background y attribute is y0_center, but transform shifts it up by -(legend_height * padding / 2)
    transform_offset_y = -(legend_height * legend_padding / 2)
    bg_top_actual = y0_center + transform_offset_y
    bg_bottom_actual = bg_top_actual + legend_height * (1 + legend_padding)

    # Create legend container
    legend = G()

    # Add background (centered at y0)
    legend.add_child(
        create_legend_background(
            x0, y0_center, legend_width, legend_height, legend_padding
        )
    )

    # Add entries (vertically centered in background)
    total_entries_height = entry_count * icon_height
    vertical_padding = bg_bottom_actual - bg_top_actual - total_entries_height
    entry_start_y = bg_top_actual + (vertical_padding / 2)

    for i, (name, color) in enumerate(zip(series_names, colors)):
        text = calculate_text_dimensions(name, font_size=font_size)
        entry_top = entry_start_y + i * icon_height
        entry = create_legend_entry(
            x0, entry_top, text, color, i, font_family, icon_height
        )
        legend.add_child(entry)

    return legend


def create_zero_line_path(
    x_axis_zero: float,
    y_axis_zero: float,
    plot_width: float,
    plot_height: float,
    left_padding: float,
    top_padding: float,
    x_stacked: bool,
    y_stacked: bool,
    x_min: float,
    y_min: float,
    is_bar_chart: bool,
    is_xy_line: bool,
) -> Path | None:
    """Create zero line path for charts with negative values.

    Args:
        x_axis_zero: X-axis zero position.
        y_axis_zero: Y-axis zero position.
        plot_width: Plot area width.
        plot_height: Plot area height.
        left_padding: Left padding.
        top_padding: Top padding.
        x_stacked: Whether x-axis is stacked.
        y_stacked: Whether y-axis is stacked.
        x_min: Minimum x value.
        y_min: Minimum y value.
        is_bar_chart: Whether this is a bar chart.
        is_xy_line: Whether this is an XY line chart.

    Returns:
        Path element for zero lines, or None if no zero lines needed.
    """
    from charted.utils.helpers import round_coordinate

    paths = []

    # X-axis zero line (vertical)
    if x_min < 0 and not is_xy_line:
        x = round_coordinate(x_axis_zero)
        paths.extend(
            [
                f"M{x} {0}",
                f"v{round_coordinate(plot_height)}z",
            ]
        )

    # Y-axis zero line (horizontal)
    if y_min < 0:
        y = round_coordinate(plot_height - y_axis_zero)
        paths.extend(
            [
                f"M{0} {y}",
                f"h{round_coordinate(plot_width)}z",
            ]
        )

    if len(paths) > 0:
        return Path(
            transform=[
                translate(round_coordinate(left_padding), round_coordinate(top_padding))
            ],
            d=paths,
            stroke="black",
        )
    return None


def generate_html_wrapper(
    svg_content: str, style: str = "display: inline-block;"
) -> str:
    """Generate HTML wrapper for SVG chart.

    Args:
        svg_content: SVG string to wrap.
        style: CSS style for container.

    Returns:
        HTML string with embedded SVG.
    """
    return f'<div style="{style}">{svg_content}</div>'
