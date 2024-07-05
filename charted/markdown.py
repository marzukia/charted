"""Markdown utilities for charted.

Provides functions to embed charts in markdown documentation and HTML.
"""

__all__ = ["chart_to_markdown", "inline_svg", "chart_to_data_url"]

from pathlib import Path
from urllib.parse import quote


def chart_to_markdown(
    svg_path: str | Path,
    title: str | None = None,
    width: str | None = None,
    relative_path: str | None = None,
) -> str:
    """Generate markdown markup for a chart image.

    Args:
        svg_path: Path to the SVG file.
        title: Alternative text for the image. Defaults to filename if not provided.
        width: Optional width specification (e.g., '500px' or '100%').
        relative_path: If provided, use this path in the markdown instead of svg_path.
            Useful when generating docs in a different directory.

    Returns:
        Markdown image syntax string.

    Example:
        >>> md = chart_to_markdown("docs/examples/bar.svg", title="Sales Chart")
        >>> print(md)
        ![Sales Chart](docs/examples/bar.svg)

        >>> md = chart_to_markdown("output.svg", width="600px")
        >>> print(md)
        ![output](output.svg){width=600px}
    """
    svg_path = Path(svg_path)

    if not svg_path.exists():
        raise FileNotFoundError(f"SVG file not found: {svg_path}")

    # Use title or derive from filename
    if title is None:
        title = svg_path.stem.replace("_", " ").replace("-", " ").title()

    # Determine the path to use in markdown
    display_path = relative_path if relative_path else str(svg_path)

    if width:
        return f"![{title}]({display_path}){{width={width}}}"
    return f"![{title}]({display_path})"


def inline_svg(svg_path: str | Path) -> str:
    """Read an SVG file and return its contents for inline embedding.

    Useful for embedding SVG directly in HTML or Jupyter notebooks.

    Args:
        svg_path: Path to the SVG file.

    Returns:
        The SVG markup as a string.

    Example:
        >>> svg_html = inline_svg("docs/examples/bar.svg")
        >>> print(svg_html[:100])
        <svg xmlns="http://www.w3.org/2000/svg" ...
    """
    svg_path = Path(svg_path)

    if not svg_path.exists():
        raise FileNotFoundError(f"SVG file not found: {svg_path}")

    with open(svg_path, "r", encoding="utf-8") as f:
        return f.read()


def chart_to_data_url(svg_path: str | Path) -> str:
    """Convert an SVG file to a data URL for embedding in markdown/HTML.

    The SVG is URL-encoded and returned as a data URI that can be
    embedded directly in markdown images or HTML img tags.

    Args:
        svg_path: Path to the SVG file.

    Returns:
        Data URL string (e.g., "data:image/svg+xml,{encoded_svg}").

    Example:
        >>> url = chart_to_data_url("chart.svg")
        >>> md = f"![chart]({url})"
    """
    svg_path = Path(svg_path)

    if not svg_path.exists():
        raise FileNotFoundError(f"SVG file not found: {svg_path}")

    with open(svg_path, "r", encoding="utf-8") as f:
        svg_data = f.read()

    encoded = quote(svg_data)
    return f"data:image/svg+xml,{encoded}"
