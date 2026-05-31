"""Rendering utilities for charted.

Extracted from Chart class to reduce coupling and improve testability.
"""

from urllib.parse import quote

from charted.html.element import G, Path, Rect, Text
from charted.themes.core import Theme
from charted.utils.exceptions import ValidationError
from charted.utils.helpers import calculate_text_dimensions
from charted.utils.transform import translate
from charted.utils.types import MeasuredText


def _adjust_color(hex_color: str, amount: int) -> str:
    """Shift a hex color lighter (positive) or darker (negative)."""
    bg = hex_color.lstrip("#")
    if len(bg) == 3:
        bg = "".join(c * 2 for c in bg)
    r, g, b = int(bg[0:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
    r = max(0, min(255, r + amount))
    g = max(0, min(255, g + amount))
    b = max(0, min(255, b + amount))
    return f"#{r:02x}{g:02x}{b:02x}"


def _derive_legend_stroke(background_color: str) -> str:
    """Derive a legend border color from the background."""
    bg = background_color.lstrip("#")
    if len(bg) == 3:
        bg = "".join(c * 2 for c in bg)
    r, g, b = int(bg[0:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    if luminance < 0.5:
        return _adjust_color(background_color, 60)
    else:
        return _adjust_color(background_color, -40)


def _derive_legend_background(background_color: str) -> str:
    """Derive a slightly offset legend background from the chart background."""
    bg = background_color.lstrip("#")
    if len(bg) == 3:
        bg = "".join(c * 2 for c in bg)
    r, g, b = int(bg[0:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    if luminance < 0.5:
        return _adjust_color(background_color, 20)
    else:
        return _adjust_color(background_color, -10)


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
    x: float,
    y: float,
    legend_width: float,
    legend_height: float,
    padding: float,
    background_color: str = "#ffffff",
    stroke_color: str = "#CCCCCC",
) -> Rect:
    """Create legend background rectangle.

    Args:
        x: X position of legend.
        y: Y position of legend.
        legend_width: Width of legend content.
        legend_height: Height of legend content.
        padding: Legend padding value.
        background_color: Fill color for legend background.
        stroke_color: Border/stroke color for legend.

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
        fill=background_color,
        fill_opacity=0.85,
        stroke="none",
    )


def calculate_legend_dimensions(
    series_names: list[str], font_size: float, legend_padding: float
) -> tuple[float, float, float, float, float]:
    """Calculate legend dimensions based on series names.

    Args:
        series_names: List of series names for legend entries.
        font_size: Font size for legend text.
        legend_padding: Padding value for legend.

    Returns:
        Tuple of (legend_width, legend_height, icon_height, entry_count, row_gap).
    """
    legend_entries = [
        calculate_text_dimensions(name, font_size=font_size) for name in series_names
    ]
    icon_height = max(entry.height for entry in legend_entries)
    legend_width = max(entry.width for entry in legend_entries) + icon_height + 2
    row_gap = 4  # Vertical gap between legend entries
    legend_height = len(legend_entries) * (icon_height + row_gap)

    return legend_width, legend_height, icon_height, len(legend_entries), row_gap


def calculate_legend_position(
    position: str,
    plot_right: float,
    plot_left: float,
    legend_width: float,
    legend_height: float,
    top_padding: float,
    inset: float = 4,
    padding: float = 0.5,
    plot_height: float = 0,
) -> tuple[float, float]:
    """Calculate legend position coordinates.

    Args:
        position: Legend position ('topright', 'topleft', 'bottomright', 'bottomleft').
        plot_right: Right edge of plot area.
        plot_left: Left edge of plot area.
        legend_width: Width of legend.
        legend_height: Height of legend.
        top_padding: Top padding of chart.
        inset: Small inset from plot border.
        padding: Legend padding value.
        plot_height: Height of the plot area (required for bottom positions).

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
        "bottomright": {
            "x0": plot_right - inset - legend_width * (1 + padding / 2),
            "y0": top_padding + plot_height - inset - legend_height * (1 + padding / 2),
        },
        "bottomleft": {
            "x0": plot_left + inset + legend_width * (padding / 2),
            "y0": top_padding + plot_height - inset - legend_height * (1 + padding / 2),
        },
    }

    result = positions.get(position)
    if not result:
        raise ValidationError(f"Invalid legend position: {position}")

    return result["x0"], result["y0"]


def create_legend_entry(
    rect_x: float,
    entry_top_y: float,
    text: MeasuredText,
    color: str,
    index: int,
    font_family: str,
    entry_height: float,
    font_color: str = "#000000",
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
        font_color: Text color for the legend label.

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
        fill=font_color,
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
    plot_height: float = 0,
) -> G | None:
    """Create complete legend element.

    Args:
        series_names: Names for each series.
        colors: Colors for each series.
        theme_config: Legend configuration from theme.
        plot_left: Left edge of plot area.
        plot_right: Right edge of plot area.
        top_padding: Top padding of chart.
        plot_height: Height of the plot area (required for bottom positions).

    Returns:
        G element containing legend, or None if no legend should be shown.
    """
    if not theme_config or not series_names:
        return None

    # Handle both dict and Theme object
    if isinstance(theme_config, Theme):
        font_size = getattr(theme_config, "legend_font_size", 12)
        legend_padding = 0.15
        font_family = getattr(theme_config, "legend_font_family", "Arial")
        font_color = getattr(theme_config, "legend_font_color", "#444444")
        position = getattr(theme_config, "legend_position", "topright")
        background_color = getattr(theme_config, "background_color", "#ffffff")
    else:
        font_size = theme_config.get("font_size", 12)
        legend_padding = theme_config.get("legend_padding", 0.15)
        font_family = theme_config.get("font_family", "Arial")
        font_color = theme_config.get("font_color", "#444444")
        position = theme_config.get("position", "topright")
        background_color = theme_config.get("background_color", "#ffffff")

    # Derive legend-specific colors from the background
    stroke_color = _derive_legend_stroke(background_color)
    legend_bg = _derive_legend_background(background_color)

    # Calculate dimensions
    legend_width, legend_height, icon_height, entry_count, row_gap = (
        calculate_legend_dimensions(series_names, font_size, legend_padding)
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
        plot_height,
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
            x0,
            y0_center,
            legend_width,
            legend_height,
            legend_padding,
            background_color=legend_bg,
            stroke_color=stroke_color,
        )
    )

    # Add entries (vertically centered in background)
    # Row gap only between entries, not after the last one
    total_entries_height = entry_count * icon_height + (entry_count - 1) * row_gap
    vertical_padding = bg_bottom_actual - bg_top_actual - total_entries_height
    entry_start_y = bg_top_actual + (vertical_padding / 2)

    for i, (name, color) in enumerate(zip(series_names, colors)):
        text = calculate_text_dimensions(name, font_size=font_size)
        entry_top = entry_start_y + i * (icon_height + row_gap)
        entry = create_legend_entry(
            x0,
            entry_top,
            text,
            color,
            i,
            font_family,
            icon_height,
            font_color=font_color,
        )
        legend.add_child(entry)

    return legend


def create_pie_legend(
    series_names: list[str],
    colors: list[str],
    theme_config: dict,
    chart_width: float,
    chart_height: float,
) -> G | None:
    """Create legend for pie/doughnut charts, split across left and right sides.

    Pie charts have significant vertical space on both sides of the circular chart.
    This function splits legend entries between left and right columns to use this
    space efficiently.

    Args:
        series_names: Names for each series.
        colors: Colors for each series.
        theme_config: Legend configuration from theme.
        chart_width: Total chart width.
        chart_height: Total chart height.

    Returns:
        G element containing the legend, or None if no legend should be shown.
    """
    if not theme_config or not series_names:
        return None

    # Handle both dict and Theme object
    if isinstance(theme_config, Theme):
        font_size = getattr(theme_config, "legend_font_size", 12)
        font_family = getattr(theme_config, "legend_font_family", "Arial")
        font_color = getattr(theme_config, "legend_font_color", "#444444")
        background_color = getattr(theme_config, "background_color", "#ffffff")
    else:
        font_size = theme_config.get("font_size", 12)
        font_family = theme_config.get("font_family", "Arial")
        font_color = theme_config.get("font_color", "#444444")
        background_color = theme_config.get("background_color", "#ffffff")

    # Derive legend-specific colors from the background
    legend_bg = _derive_legend_background(background_color)

    # Calculate entry dimensions
    legend_entries = [
        calculate_text_dimensions(name, font_size=font_size) for name in series_names
    ]
    icon_height = max(e.height for e in legend_entries) if legend_entries else font_size
    entry_height = icon_height + 4  # spacing between entries

    # Calculate column width needed
    max_label_width = max(e.width for e in legend_entries) if legend_entries else 0
    col_width = icon_height + 2 + max_label_width + 10  # icon + gap + text + padding

    # Split entries between left and right columns
    n_entries = len(series_names)
    left_count = (n_entries + 1) // 2  # ceil(n/2) for left column
    right_count = n_entries // 2  # floor(n/2) for right column

    # Calculate column heights
    left_height = left_count * entry_height
    right_height = right_count * entry_height

    # Position columns to be vertically centered
    left_bg_top = (chart_height - left_height) / 2 - 4
    right_bg_top = (chart_height - right_height) / 2 - 4

    # X positions: left column at x=10, right column mirrored from right edge
    # Background width is col_width + 12 (including padding)
    left_x = 10
    right_x = chart_width - 10 - (col_width + 12)  # 10px margin from right edge

    # Create legend container
    legend = G()

    # Add background rectangles (no border/stroke)
    if left_count > 0:
        left_bg = Rect(
            x=left_x,
            y=left_bg_top,
            width=col_width + 12,
            height=left_height + 8,
            fill=legend_bg,
            fill_opacity=0.85,
            rx=3,
        )
        legend.add_child(left_bg)

    if right_count > 0:
        right_bg = Rect(
            x=right_x,
            y=right_bg_top,
            width=col_width + 12,
            height=right_height + 8,
            fill=legend_bg,
            fill_opacity=0.85,
            rx=3,
        )
        legend.add_child(right_bg)

    # Add entries to left column
    for i in range(left_count):
        text = legend_entries[i]
        entry_y = left_bg_top + 4 + i * entry_height
        entry = create_legend_entry(
            rect_x=left_x + 6,
            entry_top_y=entry_y,
            text=text,
            color=colors[i],
            index=i,
            font_family=font_family,
            entry_height=entry_height,
            font_color=font_color,
        )
        legend.add_child(entry)

    # Add entries to right column
    for i in range(right_count):
        idx = left_count + i
        text = legend_entries[idx]
        entry_y = right_bg_top + 4 + i * entry_height
        entry = create_legend_entry(
            rect_x=right_x + 6,
            entry_top_y=entry_y,
            text=text,
            color=colors[idx],
            index=idx,
            font_family=font_family,
            entry_height=entry_height,
            font_color=font_color,
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
    stroke_color: str = "black",
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
            stroke=stroke_color,
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
