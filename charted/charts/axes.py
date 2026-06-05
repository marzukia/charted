from __future__ import annotations

import math
from typing import TYPE_CHECKING, Protocol, TypedDict, cast

from charted.constants import DEFAULT_PADDING
from charted.html.element import Element, G, Path, Text
from charted.utils.defaults import DEFAULT_FONT, DEFAULT_FONT_SIZE
from charted.utils.exceptions import InvalidDataError
from charted.utils.helpers import (
    calculate_text_dimensions,
    common_denominators,
    round_to_clean_number,
)
from charted.utils.transform import rotate, translate
from charted.utils.types import (
    AxisDimension,
    AxisValues,
    MeasuredText,
    Vector,
    Vector2D,
)
from charted.utils.value_format import format_value

if TYPE_CHECKING:
    from charted.charts.scales import Scale


class _AxisParent(Protocol):
    """Structural type for the chart object an axis renders against.

    The axis only ever reads these layout attributes off its parent chart; the
    Protocol documents that contract without constraining concrete parents.
    """

    plot_width: float
    plot_height: float
    left_padding: float
    top_padding: float
    x_label_rotation: tuple[float, float] | None


class _TickLabeled(Protocol):
    """Structural type for a scale that exposes formatted tick labels."""

    def tick_labels(self) -> list[str]: ...


class _GridMinorParams(TypedDict):
    """Minor-grid parameters peeled off a dict grid config."""

    divisions: int
    stroke: str | None
    stroke_width: float | None
    stroke_dasharray: str


class Axis(G):
    parent: _AxisParent

    def __init__(
        self,
        parent: _AxisParent,
        data: Vector2D | None = None,
        labels: list[str] | None = None,
        stacked: bool = False,
        zero_index: bool = True,
        config: str | dict[str, object] | None = None,
        pad_labels: bool = True,
        scale: Scale | None = None,
    ):
        if not data and not labels:
            raise InvalidDataError("Need labels or data.")
        elif not data and labels:
            if pad_labels:
                labels = [" ", *labels, " "]
            data = [[i for i in range(len(labels))]]

        self.stacked = stacked
        self.data: Vector2D | None = data
        self.parent = parent
        # A None scale means the default LinearScale: existing behaviour is
        # preserved byte-for-byte. Non-linear scales (log/time) own their tick
        # positions and labels and override reproject/reverse.
        self.scale = scale
        if scale is not None and getattr(scale, "name", "linear") != "linear":
            self._init_with_scale(data, labels, zero_index)
        else:
            # Use AxisValues dataclass instead of tuple
            self.values = AxisValues(data=data, labels=labels, zero_index=zero_index)
            self.labels = labels
        self.config = config
        self.add_children(self.grid_lines, self.axis_labels)

    def rebuild(self) -> None:
        """Re-render grid lines and tick labels from the current label state.

        ``grid_lines`` and ``axis_labels`` are built eagerly at construction, so
        any later mutation of ``_labels`` (e.g. category-label wrapping or
        truncation) would otherwise leave stale child elements. Call this after
        replacing ``_labels`` to regenerate the rendered children.
        """
        self.children = []
        self.add_children(self.grid_lines, self.axis_labels)

    def _init_with_scale(
        self,
        data: Vector2D | None,
        labels: list[str] | None,
        zero_index: bool,
    ) -> None:
        """Set tick values and labels from a non-linear scale."""
        from charted.utils.types import AxisDimension

        scale = cast("Scale", self.scale)
        tick_values = scale.ticks()
        self.axis_dimension = AxisDimension(
            scale.min_value, scale.max_value, len(tick_values)
        )
        self._values: Vector = list(tick_values)
        self._grid_line_values: Vector = list(tick_values)
        # Scale-provided labels (e.g. formatted dates) take priority.
        if hasattr(scale, "tick_labels"):
            self._labels = [
                calculate_text_dimensions(text)
                for text in cast("_TickLabeled", scale).tick_labels()
            ]
        else:
            self.labels = [str(v) for v in tick_values]

    @classmethod
    def _reproject(
        cls,
        value: float,
        max_value: float,
        min_value: float,
        length: float,
        stacked: bool = False,
    ) -> float:
        value_range = max_value - min_value
        if value_range == 0:
            return 0.0
        normalised_value = (value - min_value) / value_range
        if stacked:
            normalised_value = value / value_range
        return normalised_value * length

    @classmethod
    def _reverse(
        cls,
        value: float,
        max_value: float,
        min_value: float,
        length: float,
    ) -> float:
        value_range = max_value - min_value
        normalised_value = (value + min_value) / length
        if min_value:
            normalised_value = value / length
        return normalised_value * value_range

    @classmethod
    def calculate_axis_dimensions(
        cls,
        data: Vector2D | None = None,
        stacked: bool = False,
        has_labels: bool = False,
        zero_index: bool = True,
    ) -> AxisDimension:
        assert data is not None
        count = len(data[0])

        min_value: float
        max_value: float
        if stacked:
            min_values: list[float] = [0] * count
            max_values: list[float] = [0] * count
            for series in data:
                for n in range(count):
                    if series[n] < 0:
                        min_values[n] -= abs(series[n])
                    else:
                        max_values[n] += series[n]
            min_value = min(min_values)
            max_value = max(max_values)
        else:
            agg = [x for arr in data for x in arr]
            min_value = min(agg)
            max_value = max(agg)

        if abs(min_value) < 1 and abs(max_value) <= 1:
            min_value = math.floor(min_value)
            max_value = math.ceil(max_value)

        if zero_index and min_value > 0:
            min_value = 0
        # Symmetric clamp for an all-negative domain: pull the top of the range
        # up to zero so the rendered domain still contains the zero baseline.
        # Without this the domain is e.g. [-3, -1], and projecting the zero
        # line / bar baseline lands at (0 - -3) / 2 = 1.5x the plot length,
        # pushing gridlines, bars, markers and the line path outside the frame.
        if zero_index and max_value < 0:
            max_value = 0

        if not has_labels:
            if min_value < 0:
                min_value = -round_to_clean_number(abs(min_value))
            else:
                min_value = round_to_clean_number(min_value, round_down=True)
            max_value = round_to_clean_number(max_value)

        return AxisDimension(min_value, max_value, count)

    # The largest number of gridline/tick entries the value axis will build for
    # a denominator before we reject it as too fine and fall back to a
    # nice-number step. The downstream halving loops thin this to <=10, so the
    # cap only needs to stay well clear of the pathological millions-of-ticks
    # region. ~50 is comfortably above any real layout and bounds memory.
    _MAX_RAW_TICKS = 50
    _TARGET_TICKS = 10

    @classmethod
    def _grid_step(
        cls, value_range: float, denominators: Vector
    ) -> float:
        """Pick a tick step that does not explode the gridline list.

        ``calculate_axis_values`` historically walked the common divisors of the
        two endpoint magnitudes (largest first) and used the first step whose
        list had more than 5 entries. For mismatched magnitudes (e.g. domain
        (-1.0, 1e9)) the only common divisor is 1, which forces ~1e9 entries and
        a MemoryError. When the finest available divisor would still produce
        more than ``_MAX_RAW_TICKS`` entries, fall back to a clean ("nice")
        number step computed from ``value_range / _TARGET_TICKS`` instead.
        """
        chosen: float | None = None
        for denominator in reversed(denominators):
            if denominator <= 0:
                continue
            if int(value_range / denominator) + 1 > 5:
                chosen = denominator
                break
            chosen = denominator
        if chosen is None or int(value_range / chosen) > cls._MAX_RAW_TICKS:
            if value_range > 0:
                nice = round_to_clean_number(value_range / cls._TARGET_TICKS)
                if nice > 0:
                    return nice
            # Degenerate domain (no usable divisor and no range): a single tick.
            return chosen if chosen is not None else 1.0
        return chosen

    @classmethod
    def _grid_values(
        cls, min_value: float, value_range: float, denominators: Vector
    ) -> list[float]:
        """Build the descending gridline-value list with a bounded tick step."""
        step = cls._grid_step(value_range, denominators)
        count = int(value_range / step)
        return [min_value + (i * step) for i in reversed(range(count + 1))]

    @classmethod
    def calculate_axis_values(
        cls,
        data: Vector2D,
        labels: list[str] | None = None,
        zero_index: bool = True,
        stacked: bool | None = None,
    ) -> tuple[AxisDimension, list[float], list[float]]:
        axd = cls.calculate_axis_dimensions(
            data=data,
            has_labels=labels is not None,
            zero_index=zero_index,
            stacked=bool(stacked),
        )

        if labels is not None:
            # Use the actual data values as tick positions so that ordinal charts
            # (synthetically created [[0,1,...,n]] in Axis.__init__) and real-data
            # xy charts both land in the correct pixel locations.
            values = list(data[0])
            # Grid lines use full range from min to max for proper rendering
            min_val = min(values)
            max_val = max(values)
            grid_line_values: list[float] = list(range(int(min_val), int(max_val) + 1))
            return (axd, values, grid_line_values)

        denominators = common_denominators(axd.min_value, axd.max_value)
        value_range = axd.value_range
        min_value = axd.min_value
        max_value = axd.max_value

        # Handle values that area -1 to 1.
        # Round these to -1 and 1.
        if axd.value_range < 2:
            value_range = 1

        if min_value > 0 and min_value < 1:
            min_value = 0

        if max_value > 0 and max_value < 1:
            max_value = 1

        # Generate all potential grid line positions (full range), with a tick
        # step bounded so a mismatched-magnitude domain cannot explode the list.
        all_values = cls._grid_values(min_value, value_range, denominators)

        # Preserve original axis range for grid lines
        original_min = all_values[-1]
        original_max = all_values[0]

        # Filter for label display only
        values = all_values.copy()
        while len(values) > 10 and 0 not in values:
            values = [x for (i, x) in enumerate(values) if i % 2 == 0]
            min_value, max_value = values[-1], values[0]

        # Store full range for grid lines, filtered range for labels
        if min_value > original_min:
            min_value = original_min
        if max_value < original_max:
            max_value = original_max

        # Store all grid line positions separately
        grid_line_values = all_values
        while len(grid_line_values) > 10 and 0 not in grid_line_values:
            grid_line_values = [
                x for (i, x) in enumerate(grid_line_values) if i % 2 == 0
            ]

        return AxisDimension(min_value, max_value, axd.count), values, grid_line_values

    def reverse(self, value: float) -> float:
        raise Exception("reverse not implemented for instance of Axis.")

    def reproject(self, value: float) -> float:
        raise Exception("reproject not implemented for instance of Axis.")

    @property
    def zero(self) -> float:
        # Zero has no meaning on a log scale (and may be outside a time
        # domain), so anchor the zero line at the axis origin instead.
        if self.scale is not None and getattr(self.scale, "name", "linear") != "linear":
            return 0.0
        return self.reproject(0)

    @property
    def grid_lines(self) -> Element | None:
        raise Exception("grid_lines not implemented for instance of Axis.")

    @staticmethod
    def _split_grid_config(
        config: str | dict[str, object],
    ) -> tuple[dict[str, object], _GridMinorParams]:
        """Split a grid config into (major_attrs, minor_params).

        A string config becomes the historical single-weight attrs with no
        minor grid. A dict config has its minor_* keys peeled off and returned
        separately so the remaining keys can be splatted onto the major Path.
        """
        if isinstance(config, str):
            empty: _GridMinorParams = {
                "divisions": 0,
                "stroke": None,
                "stroke_width": None,
                "stroke_dasharray": "None",
            }
            return {"stroke": config, "stroke_dasharray": "None"}, empty
        major = dict(config)
        minor: _GridMinorParams = {
            "divisions": cast("int", major.pop("minor_divisions", 0)),
            "stroke": cast("str | None", major.pop("minor_stroke", None)),
            "stroke_width": cast("float | None", major.pop("minor_stroke_width", None)),
            "stroke_dasharray": cast(
                "str", major.pop("minor_stroke_dasharray", "None")
            ),
        }
        return major, minor

    @staticmethod
    def _minor_positions(coordinates: list[float], divisions: int) -> list[float]:
        """Interpolate minor-line positions between adjacent major coordinates.

        ``divisions`` is the number of equal subdivisions between two majors, so
        ``divisions - 1`` minor lines fall strictly between each pair.
        """
        if divisions <= 1 or len(coordinates) < 2:
            return []
        ordered = sorted(coordinates)
        minors: list[float] = []
        for a, b in zip(ordered, ordered[1:]):
            step = (b - a) / divisions
            for k in range(1, divisions):
                minors.append(a + step * k)
        return minors

    @property
    def axis_labels(self) -> G:
        raise Exception("axis_labels not implemented for instance of Axis.")

    @property
    def reprojected_values(self) -> list[float]:
        return [self.reproject(v) for v in self.values]

    @property
    def values(self) -> Vector:
        return self._values

    @values.setter
    def values(self, axis_values: AxisValues) -> None:
        """Set axis values using AxisValues dataclass.

        This replaces the tuple (data, labels, zero_index) which was prone to
        ordering errors. Using AxisValues provides self-documenting field names.
        """
        assert axis_values.data is not None
        self.axis_dimension, self._values, self._grid_line_values = (
            self.calculate_axis_values(
                data=axis_values.data,
                stacked=self.stacked,
                labels=axis_values.labels,
                zero_index=axis_values.zero_index,
            )
        )
        # Store grid line values separately (full range, not filtered). Reuse
        # the same bounded-step helper as calculate_axis_values so a
        # mismatched-magnitude domain cannot explode this list either.
        all_denominators = common_denominators(
            self.axis_dimension.min_value, self.axis_dimension.max_value
        )
        value_range = self.axis_dimension.max_value - self.axis_dimension.min_value
        self._grid_line_values = self._grid_values(
            self.axis_dimension.min_value, value_range, all_denominators
        )
        # Reduce grid lines if too many
        while len(self._grid_line_values) > 10 and 0 not in self._grid_line_values:
            self._grid_line_values = [
                x for (i, x) in enumerate(self._grid_line_values) if i % 2 == 0
            ]

    @property
    def labels(self) -> list[MeasuredText]:
        return self._labels

    @labels.setter
    def labels(self, labels: Vector | list[str] | None = None) -> None:
        resolved: list[str]
        if not labels:
            resolved = []
            precision = 0
            for label in self.values:
                if "." in str(label):
                    decimal_value = str(label).split(".")[-1]
                    if float(decimal_value) > 0:
                        precision = 1
            for label in self.values:
                resolved.append(format_value(label, decimals=precision))
        else:
            resolved = [str(label) for label in labels]
        self._labels = [calculate_text_dimensions(label) for label in resolved]

    @property
    def count(self) -> int:
        return len(self.values)


class XAxis(Axis):
    def reproject(self, value: float) -> float:
        if self.scale is not None and getattr(self.scale, "name", "linear") != "linear":
            return self.scale.reproject(value, self.parent.plot_width)
        # A single data point collapses the x-domain to a single value
        # (min == max), so the linear projection would pin it at x=0 (the left
        # frame, where it hides under the y-axis). Centre it horizontally
        # instead. Multi-point axes always span a real range and are unaffected.
        if self.axis_dimension.max_value == self.axis_dimension.min_value:
            return self.parent.plot_width / 2
        return self._reproject(
            value,
            self.axis_dimension.max_value,
            self.axis_dimension.min_value,
            self.parent.plot_width,
            self.stacked,
        )

    def reverse(self, value: float) -> float:
        if self.scale is not None and getattr(self.scale, "name", "linear") != "linear":
            return self.scale.reverse(value, self.parent.plot_width)
        return self._reverse(
            value,
            self.axis_dimension.max_value,
            self.axis_dimension.min_value,
            self.parent.plot_width,
        )

    @property
    def coordinates(self) -> list[float]:
        return [self.reproject(i) for i in self.values]

    def _label_stride(self, count: int) -> int:
        """Choose how many categories to skip between drawn labels.

        Dense ordinal axes draw a label for every category, which turns into a
        black smear once there are dozens of them. Mirror the YAxis grid's
        halving behaviour: pick a stride so the number of drawn labels stays in
        a readable range. When the plot width and label widths are available,
        size the stride so labels do not overlap; otherwise fall back to a
        count-based rule. Small axes (<=10 labels) keep every label.
        """
        if count <= 10:
            return 1

        # Cap the drawn-label count to the same target the gridline thinning
        # uses, so labels stay sparse and line up with the thinned grid instead
        # of smearing at a denser stride than the lines they sit under.
        stride = max(1, math.ceil(count / self._GRID_TARGET_LINES))

        # Width-aware path: if the widest label still wouldn't fit at this
        # stride, thin further so nothing overlaps at the tightest point.
        plot_width = getattr(self.parent, "plot_width", None)
        if plot_width:
            widths = [getattr(label, "width", 0) for label in self._labels]
            max_width = max(widths) if widths else 0
            if max_width > 0:
                slot = max_width + 4
                max_fit = max(1, int(plot_width // slot))
                if count > max_fit:
                    stride = max(stride, math.ceil(count / max_fit))

        return stride

    # Past this many per-category vertical gridlines the plot fills with a grey
    # haze. Thin them to roughly this many evenly-spaced lines instead.
    _GRID_DENSITY_CAP = 25
    _GRID_TARGET_LINES = 12

    def _thin_grid_coordinates(self, coordinates: list[float]) -> list[float]:
        """Drop vertical gridlines on dense ordinal axes to avoid a grey haze.

        A category axis draws one gridline per category. With a few hundred
        categories that becomes a solid block of grey. Once the count passes
        ``_GRID_DENSITY_CAP`` keep an evenly-spaced subset (about
        ``_GRID_TARGET_LINES`` lines, always including the first and last) so the
        grid stays legible. Low-cardinality axes are returned unchanged, so
        normal charts keep byte-identical grids.
        """
        n = len(coordinates)
        if n <= self._GRID_DENSITY_CAP:
            return coordinates
        stride = math.ceil(n / self._GRID_TARGET_LINES)
        kept = [c for i, c in enumerate(coordinates) if i % stride == 0]
        if coordinates and coordinates[-1] != kept[-1]:
            kept.append(coordinates[-1])
        return kept

    @property
    def grid_lines(self) -> Element | None:
        if not self.config:
            return None

        # Split the config into major-line attrs and minor-grid params. A plain
        # string config yields the historical single-weight grid.
        major, minor = self._split_grid_config(self.config)

        # In stacked mode with negative values, the reproject formula is
        # relative to zero (value/range), so tick coordinates need to be
        # shifted right by reproject(abs(min_value)) to land at absolute
        # positions within the plot.
        dx: float = 0
        min_v = self.axis_dimension.min_value
        if self.stacked and min_v < 0:
            dx = self.reproject(abs(min_v))

        coordinates = self._thin_grid_coordinates(list(self.coordinates))
        # Close the grid on the right: draw a gridline at the plot boundary when
        # the last tick falls short of it. Category axes already place a tick at
        # the edge, so nothing is added. Value axes with domain padding leave a
        # gap (scatter a little, bubble a lot since it pads for marker radii),
        # and time/log scales land on clean boundaries inside the plot; all of
        # them otherwise leave the right side looking open.
        plot_width = self.parent.plot_width
        if not coordinates or abs((coordinates[-1] + dx) - plot_width) > 0.5:
            coordinates.append(plot_width - dx)

        transform = translate(
            x=self.parent.left_padding,
            y=self.parent.top_padding,
        )

        d = [f"M{x + dx} {0} v{self.parent.plot_height}" for x in coordinates]
        major_path = Path(**major, d=d, transform=transform)

        minor_coords = self._minor_positions(coordinates, minor.get("divisions", 0))
        if not minor_coords:
            return major_path

        minor_attrs = {
            "stroke": minor["stroke"] or major.get("stroke"),
            "stroke_dasharray": minor["stroke_dasharray"],
        }
        if minor["stroke_width"] is not None:
            minor_attrs["stroke_width"] = minor["stroke_width"]
        minor_d = [f"M{x + dx} {0} v{self.parent.plot_height}" for x in minor_coords]
        minor_path = Path(**minor_attrs, d=minor_d, transform=transform)
        # Minor lines first so the heavier major lines render on top.
        return G().add_children(minor_path, major_path)

    @staticmethod
    def _non_overlapping_indices(
        coordinates: list[float],
        labels: list[MeasuredText],
        dx: float,
    ) -> set[int]:
        """Pick label indices whose centred boxes do not overlap their neighbour.

        Walks the labels in left-to-right order and keeps an index only when its
        centred box clears the previously kept label's box. The first and last
        labels are always retained: if the final label collides with the last
        kept middle label, that middle one is dropped instead so the axis range
        stays labelled. Rotated axes are not centred this way, so callers only
        rely on this for the horizontal case; it is a no-op when nothing
        collides, leaving fitting axes byte-for-byte unchanged.
        """
        n = len(labels)
        if n <= 1:
            return set(range(n))
        order = sorted(range(n), key=lambda i: coordinates[i])

        def box(i: int) -> tuple[float, float]:
            centre = coordinates[i] + dx
            half = labels[i].width / 2
            return centre - half, centre + half

        kept: list[int] = [order[0]]
        last_right = box(order[0])[1]
        for i in order[1:-1]:
            left, right = box(i)
            if left >= last_right - 1.0:
                kept.append(i)
                last_right = right
        if len(order) > 1:
            last = order[-1]
            left, right = box(last)
            while len(kept) > 1 and box(kept[-1])[1] > left + 1.0:
                kept.pop()
            kept.append(last)
        return set(kept)

    @property
    def axis_labels(self) -> G:
        theme = getattr(self.parent, "theme", None)
        font_size = DEFAULT_FONT_SIZE
        font_weight = None
        if theme is not None:
            font_size = theme.resolved_axis_label_font_size
            font_weight = theme.axis_label_font_weight
        group_kwargs = {
            "font_size": font_size,
            "font_family": DEFAULT_FONT,
            "fill": theme.resolved_label_color if theme is not None else "#444444",
            "transform": translate(
                x=self.parent.left_padding,
                y=self.parent.top_padding + DEFAULT_PADDING,
            ),
        }
        if font_weight:
            group_kwargs["font_weight"] = font_weight
        labels = G(**group_kwargs)

        rotation_angle: float = 0
        if self.parent.x_label_rotation:
            rotation_angle, _ = self.parent.x_label_rotation

        # Same absolute-position compensation as grid_lines.
        dx: float = 0
        min_v = self.axis_dimension.min_value
        if self.stacked and min_v < 0:
            dx = self.reproject(abs(min_v))

        y = self.parent.plot_height
        coordinates = list(self.coordinates)
        all_labels = list(self.labels)
        # Thin dense ordinal axes: keep first and last, skip every nth in the
        # middle so labels stop overlapping into a smear.
        stride = self._label_stride(len(all_labels))
        last_index = len(all_labels) - 1
        # Width-aware overlap pass. Value-axis numeric labels (e.g. a
        # mismatched-magnitude domain like (-4e8, 1e9)) are not ordinal, so the
        # count-based stride leaves them all in place even when adjacent wide
        # labels collide. Drop the indices whose centred box would overlap the
        # previous kept label; this only ever removes labels, so an axis whose
        # labels already fit keeps every one and renders byte-for-byte the same.
        # The centred-box overlap model only describes horizontal labels; rotated
        # labels pivot off their tick and are handled by the rotation angle, so
        # only drop overlaps when the axis is not rotated.
        keep: set[int] | None = None
        if rotation_angle <= 0:
            keep = self._non_overlapping_indices(coordinates, all_labels, dx)
        left_pad = self.parent.left_padding
        chart_width = getattr(self.parent, "width", None)
        for index, (x, label) in enumerate(zip(coordinates, all_labels)):
            if stride > 1 and index not in (0, last_index) and index % stride != 0:
                continue
            if keep is not None and index not in keep:
                continue
            x = x + dx
            if rotation_angle > 0:
                transformations = [
                    translate(label.width / len(label.text) * -1, 0),
                    rotate(rotation_angle, x, y),
                ]
            else:
                # Centre the label on its tick. Clamp the horizontal shift so an
                # edge label (a wide first/last category) cannot spill off the
                # left or right of the canvas. The label group is already
                # translated right by ``left_padding``; absolute left/right edges
                # are therefore ``left_pad + x + shift`` and ``+ label.width``.
                shift = -label.width / 2
                if chart_width is not None:
                    abs_left = left_pad + x + shift
                    if abs_left < 0:
                        shift -= abs_left
                    abs_right = left_pad + x + shift + label.width
                    overflow = abs_right - chart_width
                    if overflow > 0:
                        shift -= overflow
                transformations = [translate(shift, 0)]
            text = Text(
                x=x,
                y=y,
                text=label.text,
                transform=transformations,
            )
            labels.add_child(text)

        return labels


class YAxis(Axis):
    def reproject(self, value: float) -> float:
        if self.scale is not None and getattr(self.scale, "name", "linear") != "linear":
            return self.scale.reproject(value, self.parent.plot_height)
        return self._reproject(
            value,
            self.axis_dimension.max_value,
            self.axis_dimension.min_value,
            self.parent.plot_height,
            self.stacked,
        )

    def reverse(self, value: float) -> float:
        if self.scale is not None and getattr(self.scale, "name", "linear") != "linear":
            return self.scale.reverse(value, self.parent.plot_height)
        return self._reverse(
            value,
            self.axis_dimension.max_value,
            self.axis_dimension.min_value,
            self.parent.plot_height,
        )

    @property
    def coordinates(self) -> list[float]:
        # For bar/column charts, use values (number of bars) not grid lines
        bar_height = getattr(self.parent, "y_height", None)
        if bar_height is not None:
            values = self.values
        elif hasattr(self, "_grid_line_values") and self._grid_line_values:
            values = self._grid_line_values
        else:
            values = self.values

        offset: float = 0
        if self.stacked and self.axis_dimension.min_value < 0:
            offset = self.axis_dimension.min_value

        if bar_height is not None:
            bar_gap = getattr(self.parent, "bar_gap", 0.5)
            gap = bar_height * bar_gap
            start_y = bar_height * bar_gap
            return [
                start_y + i * (bar_height + gap) + bar_height / 2
                for i in range(len(values))
            ]

        return [self.reproject(i + abs(offset)) for i in reversed(values)]

    @property
    def grid_lines(self) -> Element | None:
        if not self.config:
            return None

        # Split the config into major-line attrs and minor-grid params. A plain
        # string config yields the historical single-weight grid.
        major, minor = self._split_grid_config(self.config)

        transform = translate(
            x=self.parent.left_padding,
            y=self.parent.top_padding,
        )

        coordinates = list(self.coordinates)
        d = [f"M{0} {y} h{self.parent.plot_width}" for y in coordinates]
        major_path = Path(**major, d=d, transform=transform)

        minor_coords = self._minor_positions(coordinates, minor.get("divisions", 0))
        if not minor_coords:
            return major_path

        minor_attrs = {
            "stroke": minor["stroke"] or major.get("stroke"),
            "stroke_dasharray": minor["stroke_dasharray"],
        }
        if minor["stroke_width"] is not None:
            minor_attrs["stroke_width"] = minor["stroke_width"]
        minor_d = [f"M{0} {y} h{self.parent.plot_width}" for y in minor_coords]
        minor_path = Path(**minor_attrs, d=minor_d, transform=transform)
        # Minor lines first so the heavier major lines render on top.
        return G().add_children(minor_path, major_path)

    @property
    def axis_labels(self) -> G:
        theme = getattr(self.parent, "theme", None)
        font_size = DEFAULT_FONT_SIZE
        font_weight = None
        if theme is not None:
            font_size = theme.resolved_axis_label_font_size
            font_weight = theme.axis_label_font_weight
        group_kwargs = {
            "font_size": font_size,
            "font_family": DEFAULT_FONT,
            "fill": theme.resolved_label_color if theme is not None else "#444444",
            "transform": translate(
                x=(self.parent.left_padding - 6),
                y=self.parent.top_padding,
            ),
        }
        if font_weight:
            group_kwargs["font_weight"] = font_weight
        labels = G(**group_kwargs)

        bar_height = getattr(self.parent, "y_height", None)
        if bar_height is not None:
            bar_gap = getattr(self.parent, "bar_gap", 0.5)
            gap = bar_height * bar_gap
            start_y = bar_height * bar_gap
            y_positions = [
                start_y + i * (bar_height + gap) + bar_height / 2
                for i in range(len(self.labels))
            ]
        else:
            y_positions = self.coordinates

        for y, label in zip(y_positions, self.labels):
            lines = getattr(label, "lines", None)
            if bar_height is not None:
                if lines:
                    labels.add_child(self._wrapped_label(lines, y, label.height))
                else:
                    text = Text(
                        x=0,
                        y=y,
                        text=label.text,
                        dominant_baseline="central",
                        transform=translate(
                            x=-label.width,
                            y=0,
                        ),
                    )
                    labels.add_child(text)
            else:
                text = Text(
                    x=0,
                    y=y,
                    text=label.text,
                    transform=translate(
                        x=-label.width,
                        y=label.height / 4,
                    ),
                )
                labels.add_child(text)
        return labels

    @staticmethod
    def _wrapped_label(lines: list[str], y: float, total_height: float) -> Text:
        """Build a right-aligned multi-line label centred on ``y``.

        Each line becomes a ``<tspan>`` (anchored at the gutter's right edge
        via ``text-anchor="end"``) with its own ``dy`` so the stacked block of
        ``len(lines)`` lines is vertically centred on the bar's midpoint ``y``.
        """
        from charted.html.element import TSpan

        n = len(lines)
        line_height = total_height / n if n else total_height
        # Baseline of the first line so the block centres on y. Each subsequent
        # line steps down by one line height.
        first_dy = -(line_height * (n - 1)) / 2 + line_height / 4
        text = Text(
            x=0,
            y=y,
            text_anchor="end",
        )
        for i, line in enumerate(lines):
            text.add_child(
                TSpan(
                    text=line,
                    x=0,
                    dy=first_dy if i == 0 else line_height,
                )
            )
        return text
