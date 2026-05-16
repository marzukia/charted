"""Chart rendering module.

Extracts rendering responsibilities from the Chart class to improve
maintainability and testability.
"""

from typing import Any


class ChartRenderer:
    """Encapsulates chart rendering to SVG, markdown, and file output.

    This class handles all rendering-related responsibilities that were previously
    in the Chart base class, including:
    - SVG string generation
    - Markdown image markup
    - HTML wrapper generation
    - File saving

    Note: The actual SVG construction is still done by the Chart class;
    this module provides the serialization and output methods.
    """

    @staticmethod
    def to_svg(svg_element: Any) -> str:
        """Get SVG string from chart element.

        Args:
            svg_element: Chart's SVG root element with svg property

        Returns:
            Complete SVG markup as string
        """
        return svg_element.svg

    @staticmethod
    def to_markdown(svg_element: Any, alt_text: str | None = None, width: str | None = None) -> str:
        """Generate markdown markup for the chart.

        Args:
            svg_element: Chart's SVG root element with svg property
            alt_text: Alternative text for the image. Defaults to title if available.
            width: Optional width specification (e.g., '500px' or '100%')

        Returns:
            Markdown image syntax with data URL

        Example:
            >>> chart = BarChart(data=[1, 2, 3], labels=['a', 'b', 'c'])
            >>> print(ChartRenderer.to_markdown(chart))
            ![chart](data:image/svg+xml,{encoded_svg})
        """
        from urllib.parse import quote

        svg_data = svg_element.svg
        alt = alt_text or (getattr(svg_element, 'title', None) if hasattr(svg_element, 'title') else "chart")

        # Encode SVG as data URL
        encoded = quote(svg_data)
        data_url = f"data:image/svg+xml,{encoded}"

        if width:
            return f"![{alt}]({data_url}){{width={width}}}"
        return f"![{alt}]({data_url})"

    @staticmethod
    def to_html(svg_element: Any) -> str:
        """Return HTML wrapper for the chart.

        This method is called by IPython/Jupyter when displaying
        objects in HTML format. Wraps the SVG in a container div.

        Args:
            svg_element: Chart's SVG root element with svg property

        Returns:
            HTML string with the embedded SVG
        """
        return f'<div style="display: inline-block;">{svg_element.svg}</div>'

    @staticmethod
    def to_svg_for_jupyter(svg_element: Any) -> str:
        """Return SVG string for Jupyter notebook display.

        This method is automatically called by Jupyter to render
        SVG charts inline in notebooks.

        Args:
            svg_element: Chart's SVG root element with svg property

        Returns:
            The SVG string representation of the chart.
        """
        return svg_element.svg

    @staticmethod
    def save(svg_element: Any, path: str) -> None:
        """Save the chart to a file.

        Args:
            svg_element: Chart's SVG root element with svg property
            path: File path to save the SVG file
        """
        with open(path, "w") as f:
            f.write(svg_element.svg)
