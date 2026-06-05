"""Output and serialization methods for charts.

Extracted from the :class:`~charted.charts.chart.Chart` base class to reduce
its size. The methods are unchanged; they are mixed back into ``Chart`` via
the class bases, so they continue to operate on the same ``self``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from charted.utils.rendering import (
    generate_html_wrapper,
    generate_markdown_image,
)

if TYPE_CHECKING:
    from charted.utils.types import MeasuredText


class ChartOutputMixin:
    """Output and serialization behavior for :class:`Chart`.

    Provides the public ``to_*`` / ``save`` methods and the notebook ``_repr_*``
    hooks. These rely on attributes supplied by the concrete chart class
    (``svg``, ``html``, ``_title``, ``_tooltips``, ``_build_children``); they
    are declared here only for type checking.
    """

    if TYPE_CHECKING:
        _title: MeasuredText | None
        _tooltips: bool

        @property
        def svg(self) -> str: ...

        @property
        def html(self) -> str: ...

        def _build_children(self) -> None: ...

    def _repr_svg_(self) -> str:
        """Return SVG string for Jupyter notebook display."""
        return self.svg

    def to_svg(self) -> str:
        """Get the SVG string representation of the chart."""
        return self.svg

    def to_markdown(self, alt_text: str | None = None, width: str | None = None) -> str:
        """Generate markdown markup for the chart."""
        title_text = self._title.text if self._title else None
        return generate_markdown_image(self.svg, alt_text, title_text, width)

    def to_html(
        self, style: str = "display: inline-block;", tooltips: bool = False
    ) -> str:
        """Return standalone HTML with embedded SVG.

        Args:
            style: CSS style for the container div.
            tooltips: If True, attach a native SVG ``<title>`` to each data
                mark so browsers show a built-in hover tooltip (no
                JavaScript). File output via ``to_svg()``/``save()`` is never
                affected.

        Returns:
            HTML string with the SVG embedded in a div.
        """
        if not tooltips:
            return generate_html_wrapper(self.svg, style)

        # Regenerate the data-mark representation with <title> children, then
        # restore the inert state so to_svg()/save() stay unchanged.
        self._tooltips = True
        try:
            self._build_children()
            svg = self.html
        finally:
            self._tooltips = False
            self._build_children()
        return generate_html_wrapper(svg, style)

    def _repr_html_(self) -> str:
        """Return HTML wrapper for the chart."""
        return self.to_html()

    def to_base64(self) -> str:
        """Return the SVG as a data URI for inline embedding.

        Returns:
            Data URL string (e.g. 'data:image/svg+xml,<encoded-svg>').
        """
        from urllib.parse import quote

        return f"data:image/svg+xml,{quote(self.svg)}"

    def save(self, path: str, *, scale: int = 2) -> None:
        """Save the chart to a file.

        File format is detected from the extension:
        - .svg: writes raw SVG markup
        - .png: rasterizes to PNG (needs the png extra: pip install "charted[png]")

        Charts export to PNG directly; you do not need to rasterize the SVG
        yourself. Example: ``chart.save("chart.png")``.

        Args:
            path: Destination file path. Use a .svg or .png extension.
            scale: Resolution multiplier for PNG output (default 2x).

        Raises:
            ImportError: If saving as PNG and the png extra is not installed.
            ValueError: If the file extension is not supported.
        """
        import os

        ext = os.path.splitext(path)[1].lower()

        if ext == ".svg":
            with open(path, "w") as f:
                f.write(self.svg)
        elif ext == ".png":
            try:
                import cairosvg  # type: ignore[import-untyped]
            except ImportError:
                raise ImportError(
                    "PNG export requires the optional png extra. "
                    'Install it with: pip install "charted[png]"'
                ) from None
            cairosvg.svg2png(bytestring=self.svg.encode(), write_to=path, scale=scale)
        else:
            raise ValueError(
                f"Unsupported file extension '{ext}'. Supported: .svg, .png"
            )
