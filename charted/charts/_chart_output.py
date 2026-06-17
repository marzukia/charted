"""Output and serialization methods for charts.

Extracted from the :class:`~charted.charts.chart.Chart` base class to reduce
its size. The methods are unchanged; they are mixed back into ``Chart`` via
the class bases, so they continue to operate on the same ``self``.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from charted.utils.rendering import (
    generate_html_wrapper,
    generate_markdown_image,
)

if TYPE_CHECKING:
    from charted.themes.core import Theme
    from charted.utils.types import MeasuredText

# Bundled, redistributable font files available for @font-face embedding.
_FONT_FILES_DIR = Path(__file__).resolve().parent.parent / "fonts" / "files"


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
        theme: Theme

        @property
        def svg(self) -> str: ...

        @property
        def html(self) -> str: ...

        def _build_children(self) -> None: ...

    def _repr_svg_(self) -> str:
        """Return SVG string for Jupyter notebook display."""
        return self.svg

    def to_svg(self, embed_fonts: bool = False) -> str:
        """Get the SVG string representation of the chart.

        Args:
            embed_fonts: If True, inline an @font-face for each bundled font the
                chart uses, so the SVG renders the exact font even where it is
                not installed. Off by default to keep the SVG small.
        """
        svg = self.svg
        return self._embed_font_faces(svg) if embed_fonts else svg

    def _embed_font_faces(self, svg: str) -> str:
        """Inline @font-face declarations for any bundled font the chart uses."""
        import base64

        theme = getattr(self, "theme", None)
        families: list[str] = []
        for attr in ("title_font_family", "legend_font_family"):
            value = getattr(theme, attr, None)
            if isinstance(value, str):
                families.append(value.split(",")[0].strip())

        faces: list[str] = []
        seen: set[str] = set()
        for family in families:
            if family in seen:
                continue
            seen.add(family)
            ttf = _FONT_FILES_DIR / f"{family}.ttf"
            if ttf.exists():
                encoded = base64.b64encode(ttf.read_bytes()).decode("ascii")
                faces.append(
                    f'@font-face{{font-family:"{family}";'
                    f'src:url("data:font/ttf;base64,{encoded}") '
                    f'format("truetype");}}'
                )
        if not faces:
            return svg
        style = "<style>" + "".join(faces) + "</style>"
        idx = svg.find(">")
        return svg if idx < 0 else svg[: idx + 1] + style + svg[idx + 1 :]

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

    def to_png_bytes(self, *, scale: int = 2, embed_fonts: bool = False) -> bytes:
        """Rasterize the chart to PNG and return the raw bytes.

        Args:
            scale: Resolution multiplier for the PNG output (default 2x).
            embed_fonts: If True, inline the chart's bundled font(s) as
                @font-face so the output renders the exact font without it
                installed.

        Returns:
            PNG image data as bytes.

        Raises:
            ImportError: If the png extra (cairosvg) is not installed.
        """
        try:
            import cairosvg  # type: ignore[import-untyped]
        except ImportError:
            raise ImportError(
                "PNG export requires the optional png extra. "
                'Install it with: pip install "charted[png]"'
            ) from None

        svg = self.to_svg(embed_fonts=embed_fonts)
        png: bytes = cairosvg.svg2png(bytestring=svg.encode(), scale=scale)
        return png

    def to_png_base64(self, *, scale: int = 2, embed_fonts: bool = False) -> str:
        """Rasterize the chart to PNG and return base64-encoded bytes.

        The returned string is the raw base64 payload with no data URL
        prefix. Use :meth:`to_png_data_url` for an embeddable data URL.

        Args:
            scale: Resolution multiplier for the PNG output (default 2x).
            embed_fonts: If True, inline the chart's bundled font(s).

        Returns:
            Base64-encoded PNG bytes as an ASCII string.

        Raises:
            ImportError: If the png extra (cairosvg) is not installed.
        """
        import base64

        return base64.b64encode(
            self.to_png_bytes(scale=scale, embed_fonts=embed_fonts)
        ).decode("ascii")

    def to_png_data_url(self, *, scale: int = 2, embed_fonts: bool = False) -> str:
        """Rasterize the chart to a PNG data URL for inline embedding.

        Unlike :meth:`to_base64`, which returns an SVG data URL, this returns
        a base64 PNG data URL that renders in any chat UI or browser without a
        separate SVG renderer.

        Args:
            scale: Resolution multiplier for the PNG output (default 2x).
            embed_fonts: If True, inline the chart's bundled font(s).

        Returns:
            Data URL string ('data:image/png;base64,...').

        Raises:
            ImportError: If the png extra (cairosvg) is not installed.
        """
        b64 = self.to_png_base64(scale=scale, embed_fonts=embed_fonts)
        return f"data:image/png;base64,{b64}"

    def save(self, path: str, *, scale: int = 2, embed_fonts: bool = False) -> None:
        """Save the chart to a file.

        File format is detected from the extension:
        - .svg: writes raw SVG markup
        - .png: rasterizes to PNG (needs the png extra: pip install "charted[png]")

        Charts export to PNG directly; you do not need to rasterize the SVG
        yourself. Example: ``chart.save("chart.png")``.

        Args:
            path: Destination file path. Use a .svg or .png extension.
            scale: Resolution multiplier for PNG output (default 2x).
            embed_fonts: If True, inline the chart's bundled font(s) as @font-face
                so the output renders the exact font without it installed.

        Raises:
            ImportError: If saving as PNG and the png extra is not installed.
            ValueError: If the file extension is not supported.
        """
        import os

        ext = os.path.splitext(path)[1].lower()
        svg = self.to_svg(embed_fonts=embed_fonts)

        if ext == ".svg":
            with open(path, "w") as f:
                f.write(svg)
        elif ext == ".png":
            try:
                import cairosvg
            except ImportError:
                raise ImportError(
                    "PNG export requires the optional png extra. "
                    'Install it with: pip install "charted[png]"'
                ) from None
            cairosvg.svg2png(bytestring=svg.encode(), write_to=path, scale=scale)
        else:
            raise ValueError(
                f"Unsupported file extension '{ext}'. Supported: .svg, .png"
            )
