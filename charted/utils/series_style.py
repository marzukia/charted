"""Series style configuration for charted charts.

This module provides the SeriesStyle dataclass with builder methods
for configuring per-series appearance.
"""

from __future__ import annotations

import dataclasses
from typing import Optional


@dataclasses.dataclass(frozen=True)
class SeriesStyle:
    """Configuration for a single series' visual appearance.

    Provides builder methods for fluent style configuration:

    ```python
    style = (
        SeriesStyle()
        .with_fill("#ff0000")
        .with_stroke("#cc0000")
        .with_stroke_width(2)
        .with_show_markers(True)
        .with_marker_shape("circle")
        .with_marker_size(5)
    )
    ```

    Args:
        fill: Fill color for bars/areas.
        stroke: Stroke color for lines/borders.
        stroke_width: Width of stroke in pixels.
        stroke_dasharray: Dash pattern (e.g., "2,2").
        show_markers: Whether to show markers on data points.
        marker_shape: Marker shape ('circle', 'square', 'diamond').
        marker_size: Size of markers in pixels.
    """

    _fill: Optional[str] = None
    _stroke: Optional[str] = None
    _stroke_width: Optional[float] = None
    _stroke_dasharray: Optional[str] = None
    _show_markers: Optional[bool] = None
    _marker_shape: Optional[str] = None
    _marker_size: Optional[float] = None

    def with_fill(self, color: str) -> SeriesStyle:
        """Set fill color.

        Args:
            color: Hex color string (e.g., '#ff0000').

        Returns:
            New SeriesStyle with fill set.
        """
        return dataclasses.replace(self, _fill=color)

    def with_stroke(self, color: str) -> SeriesStyle:
        """Set stroke color.

        Args:
            color: Hex color string (e.g., '#cc0000').

        Returns:
            New SeriesStyle with stroke set.
        """
        return dataclasses.replace(self, _stroke=color)

    def with_stroke_width(self, width: float) -> SeriesStyle:
        """Set stroke width.

        Args:
            width: Stroke width in pixels.

        Returns:
            New SeriesStyle with stroke_width set.
        """
        return dataclasses.replace(self, _stroke_width=width)

    def with_stroke_dasharray(self, pattern: str) -> SeriesStyle:
        """Set stroke dash pattern.

        Args:
            pattern: Dash pattern string (e.g., '2,2').

        Returns:
            New SeriesStyle with stroke_dasharray set.
        """
        return dataclasses.replace(self, _stroke_dasharray=pattern)

    def with_show_markers(self, visible: bool) -> SeriesStyle:
        """Set marker visibility.

        Args:
            visible: Whether to show markers.

        Returns:
            New SeriesStyle with show_markers set.
        """
        return dataclasses.replace(self, _show_markers=visible)

    def with_marker_shape(self, shape: str) -> SeriesStyle:
        """Set marker shape.

        Args:
            shape: Marker shape ('circle', 'square', 'diamond').

        Returns:
            New SeriesStyle with marker_shape set.
        """
        return dataclasses.replace(self, _marker_shape=shape)

    def with_marker_size(self, size: float) -> SeriesStyle:
        """Set marker size.

        Args:
            size: Marker size in pixels.

        Returns:
            New SeriesStyle with marker_size set.
        """
        return dataclasses.replace(self, _marker_size=size)

    def __getattr__(self, name: str) -> object:
        """Provide backward-compatible attribute access for dict-style usage.

        Allows code like `style["fill"]` or `style.fill` to work with SeriesStyle.
        """
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")
        # Map public names to internal _prefixed names
        mapping = {
            "fill": "_fill",
            "stroke": "_stroke",
            "stroke_width": "_stroke_width",
            "stroke_dasharray": "_stroke_dasharray",
            "show_markers": "_show_markers",
            "marker_shape": "_marker_shape",
            "marker_size": "_marker_size",
        }
        internal_name = mapping.get(name)
        if internal_name:
            return getattr(self, internal_name)
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")

    def get(self, key: str, default: object = None) -> object:
        """Dict-style get method for backward compatibility."""
        try:
            return getattr(self, key)
        except AttributeError:
            return default

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary for backward compatibility.

        Returns:
            Dictionary with all non-None properties.
        """
        result: dict[str, object] = {}
        if self._fill is not None:
            result["fill"] = self._fill
        if self._stroke is not None:
            result["stroke"] = self._stroke
        if self._stroke_width is not None:
            result["stroke_width"] = self._stroke_width
        if self._stroke_dasharray is not None:
            result["stroke_dasharray"] = self._stroke_dasharray
        if self._show_markers is not None:
            result["show_markers"] = self._show_markers
        if self._marker_shape is not None:
            result["marker_shape"] = self._marker_shape
        if self._marker_size is not None:
            result["marker_size"] = self._marker_size
        return result


# Backward compatibility alias
SeriesStyleConfig = SeriesStyle | dict[str, object]
