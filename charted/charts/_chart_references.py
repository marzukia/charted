"""Reference-line and axis-title rendering methods for charts.

Extracted from the :class:`~charted.charts.chart.Chart` base class to reduce
its size. The methods are unchanged; they are mixed back into ``Chart`` via
the class bases, so they continue to operate on the same ``self``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from charted.html.element import G, Text

if TYPE_CHECKING:
    from charted.charts.chart import Chart, _Annotation
    from charted.themes.core import Theme
    from charted.utils.types import ReferenceLineDict


class ChartReferenceLayerMixin:
    """Reference-line and axis-title rendering for :class:`Chart`.

    Builds the legacy ``h_lines`` / ``v_lines`` reference layer, the combined
    annotation list, the rendered reference-line group (including label
    callouts), and the x/y axis title labels. These rely on attributes and
    layout properties supplied by the concrete chart class; they are declared
    here only for type checking.
    """

    if TYPE_CHECKING:
        _h_lines: list[float] | None
        _v_lines: list[float] | None
        _annotations: list[_Annotation]
        _reference_line_labels: list[ReferenceLineDict]
        _x_label: str | None
        _y_label: str | None
        _height: float
        theme: Theme

        @property
        def left_padding(self) -> float: ...

        @property
        def top_padding(self) -> float: ...

        @property
        def plot_width(self) -> float: ...

        @property
        def plot_height(self) -> float: ...

    def _collect_legacy_reference_lines(self) -> list[_Annotation]:
        """Build the legacy ``h_lines`` / ``v_lines`` reference-line layer.

        These are expressed as dashed full-span ``LineAnnotation`` objects so
        there is a single rendering path. They are kept separate from
        user-supplied annotations because reference lines span the full plot
        and are intentionally not clipped, and their markup must stay
        byte-for-byte identical to historical output.
        """
        from charted.charts.annotations import LineAnnotation

        annotations: list[_Annotation] = []
        if self._h_lines:
            annotations.extend(LineAnnotation._h_line(v) for v in self._h_lines)
        if self._v_lines:
            annotations.extend(LineAnnotation._v_line(v) for v in self._v_lines)
        return annotations

    def _collect_annotations(self) -> list[_Annotation]:
        """Build the full annotation list for this chart.

        Legacy reference lines (``h_lines`` / ``v_lines``) come first, in their
        historical order, followed by any user-supplied annotations.
        """
        return self._collect_legacy_reference_lines() + list(self._annotations)

    def _render_reference_lines(self) -> G | None:
        """Render the annotation layer (reference lines, boxes, labels).

        Annotations are positioned in data coordinates and reprojected through
        the axes, drawn inside the plot-area group. Legacy full-span reference
        lines are drawn directly in the group; user annotations are drawn in a
        nested group clipped to the plot area so out-of-domain boxes/labels
        cannot bleed over the axes or off-canvas.
        """
        legacy = self._collect_legacy_reference_lines()
        user_annotations = list(self._annotations)
        if (
            not legacy
            and not user_annotations
            and not getattr(self, "_reference_line_labels", [])
        ):
            return None

        g = G(
            transform=f"translate({self.left_padding}, {self.top_padding})",
        )
        # Full-span legacy h/v reference lines are drawn directly (unclipped),
        # preserving byte-for-byte historical output.
        chart = cast("Chart", self)
        for annotation in legacy:
            g.add_child(annotation.render(chart))

        # User annotations (boxes, lines, labels) are clipped to the plot area
        # using the same clip path as the scatter point group.
        if user_annotations:
            clipped = G(clip_path="url(#plot-clip)")
            for annotation in user_annotations:
                clipped.add_child(annotation.render(chart))
            g.add_child(clipped)

        # Render any reference-line labels supplied via the reference_lines API.
        # The lines themselves are already drawn above (as LineAnnotations); this
        # adds the text callouts next to them.
        ref_labels = {}
        for entry in getattr(self, "_reference_line_labels", []):
            ref_labels[(entry["axis"], entry["value"])] = entry.get("label")

        if ref_labels:
            from charted.utils.helpers import calculate_text_dimensions

            ref_color = self.theme.resolved_reference_line_color
            label_font_size = max(8, self.theme.title_font_size - 4)
            label_font_family = self.theme.title_font_family

            for (axis, value), label in ref_labels.items():
                if not label:
                    continue
                text_w = calculate_text_dimensions(
                    str(label), font=label_font_family, font_size=label_font_size
                ).width
                if axis == "y":
                    # The dashed line spans the full plot width. Anchor the label
                    # to the line's right end, inside the plot, so it reads as a
                    # callout on a continuous line rather than a floating tag next
                    # to a clipped one. Sit it just below the line by default
                    # (there is usually more clear space below a target line than
                    # above it) and nudge it off any gridline it would touch.
                    y = self.plot_height - chart.y_axis.reproject(value)
                    label_x = self.plot_width - 4
                    gap = label_font_size * 0.5
                    # Candidate baseline below the line; flip above if that pushes
                    # the text off the bottom of the plot.
                    label_y = y + label_font_size + gap
                    if label_y > self.plot_height - 2:
                        label_y = y - gap
                    # Keep the text band clear of horizontal gridlines.
                    gridlines = [self.plot_height - c for c in chart.y_axis.coordinates]
                    text_top = label_y - label_font_size
                    for tick_y in gridlines:
                        if text_top - 2 <= tick_y <= label_y + 2:
                            # Gridline cuts through the text: shift the whole label
                            # below that gridline (or above the line if no room).
                            shifted = tick_y + label_font_size + gap
                            label_y = (
                                shifted if shifted < self.plot_height - 2 else y - gap
                            )
                            break
                    g.add_child(
                        Text(
                            text=label,
                            x=label_x,
                            y=label_y,
                            fill=ref_color,
                            font_size=label_font_size,
                            font_family=label_font_family,
                            text_anchor="end",
                        )
                    )
                else:
                    x = chart.x_axis.reproject(value)
                    # Keep the label fully on-canvas: anchor it to the left of the
                    # line when it would otherwise overflow the right edge.
                    if x + 4 + text_w > self.plot_width:
                        label_x = x - 4
                        anchor = "end"
                    else:
                        label_x = x + 4
                        anchor = "start"
                    g.add_child(
                        Text(
                            text=label,
                            x=label_x,
                            y=label_font_size,
                            fill=ref_color,
                            font_size=label_font_size,
                            font_family=label_font_family,
                            text_anchor=anchor,
                        )
                    )

        return g

    def _render_axis_labels(self) -> list[Text]:
        """Render x-axis and y-axis title labels."""
        elements: list[Text] = []
        font_size = self.theme.title_font_size - 2
        font_family = self.theme.title_font_family
        font_color = self.theme.resolved_axis_title_color

        if self._x_label:
            # Centered below the x-axis, below the tick labels
            x = self.left_padding + self.plot_width / 2
            y = self._height - 2
            elements.append(
                Text(
                    text=self._x_label,
                    x=x,
                    y=y,
                    fill=font_color,
                    font_size=font_size,
                    font_family=font_family,
                    text_anchor="middle",
                )
            )

        if self._y_label:
            # Centered along the y-axis, rotated -90 degrees
            # Position outside (to the left of) the tick labels
            x = font_size
            y = self.top_padding + self.plot_height / 2
            elements.append(
                Text(
                    text=self._y_label,
                    x=x,
                    y=y,
                    fill=font_color,
                    font_size=font_size,
                    font_family=font_family,
                    text_anchor="middle",
                    transform=f"rotate(-90, {x}, {y})",
                )
            )

        return elements
