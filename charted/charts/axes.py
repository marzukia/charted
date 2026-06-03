import math

from charted.constants import DEFAULT_PADDING
from charted.html.element import G, Path, Text
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


class Axis(G):
    def __init__(
        self,
        parent: object,
        data: Vector2D | None = None,
        labels: list[str] | None = None,
        stacked: bool = False,
        zero_index: bool = True,
        config: str | None = None,
        pad_labels: bool = True,
        scale: object | None = None,
    ):
        if not data and not labels:
            raise InvalidDataError("Need labels or data.")
        elif not data and labels:
            if pad_labels:
                labels = [" ", *labels, " "]
            data = [[i for i in range(len(labels))]]

        self.stacked = stacked
        self.data = data
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

    def _init_with_scale(self, data, labels, zero_index) -> None:
        """Set tick values and labels from a non-linear scale."""
        from charted.utils.types import AxisDimension

        tick_values = self.scale.ticks()
        self.axis_dimension = AxisDimension(
            self.scale.min_value, self.scale.max_value, len(tick_values)
        )
        self._values = list(tick_values)
        self._grid_line_values = list(tick_values)
        # Scale-provided labels (e.g. formatted dates) take priority.
        if hasattr(self.scale, "tick_labels"):
            self._labels = [
                calculate_text_dimensions(text) for text in self.scale.tick_labels()
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
        count = len(data[0])

        if stacked:
            min_values = [0] * count
            max_values = [0] * count
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

        if not has_labels:
            if min_value < 0:
                min_value = -round_to_clean_number(abs(min_value))
            else:
                min_value = round_to_clean_number(min_value, round_down=True)
            max_value = round_to_clean_number(max_value)

        return AxisDimension(min_value, max_value, count)

    @classmethod
    def calculate_axis_values(
        cls,
        data: Vector2D,
        labels: list[str] | None = None,
        zero_index: bool = True,
        stacked: bool | None = None,
    ) -> tuple[AxisDimension, list[float]]:
        axd = cls.calculate_axis_dimensions(
            data=data,
            has_labels=labels is not None,
            zero_index=zero_index,
            stacked=stacked,
        )

        if labels is not None:
            # Use the actual data values as tick positions so that ordinal charts
            # (synthetically created [[0,1,...,n]] in Axis.__init__) and real-data
            # xy charts both land in the correct pixel locations.
            values = list(data[0])
            # Grid lines use full range from min to max for proper rendering
            min_val = min(values)
            max_val = max(values)
            grid_line_values = list(range(int(min_val), int(max_val) + 1))
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

        # Generate all potential grid line positions (full range)
        all_values = []
        for denominator in reversed(denominators):
            count = int(value_range / denominator)
            all_values = [
                min_value + (i * denominator) for i in reversed(range(count + 1))
            ]
            if len(all_values) > 5:
                break

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

    @property
    def zero(self) -> float:
        # Zero has no meaning on a log scale (and may be outside a time
        # domain), so anchor the zero line at the axis origin instead.
        if self.scale is not None and getattr(self.scale, "name", "linear") != "linear":
            return 0.0
        return self.reproject(0)

    @property
    def grid_lines(self) -> Path:
        raise Exception("grid_lines not implemented for instance of Axis.")

    @staticmethod
    def _split_grid_config(config) -> tuple[dict, dict]:
        """Split a grid config into (major_attrs, minor_params).

        A string config becomes the historical single-weight attrs with no
        minor grid. A dict config has its minor_* keys peeled off and returned
        separately so the remaining keys can be splatted onto the major Path.
        """
        if isinstance(config, str):
            return {"stroke": config, "stroke_dasharray": "None"}, {}
        major = dict(config)
        minor = {
            "divisions": major.pop("minor_divisions", 0),
            "stroke": major.pop("minor_stroke", None),
            "stroke_width": major.pop("minor_stroke_width", None),
            "stroke_dasharray": major.pop("minor_stroke_dasharray", "None"),
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
        self.axis_dimension, self._values, self._grid_line_values = (
            self.calculate_axis_values(
                data=axis_values.data,
                stacked=self.stacked,
                labels=axis_values.labels,
                zero_index=axis_values.zero_index,
            )
        )
        # Store grid line values separately (full range, not filtered)
        all_denominators = common_denominators(
            self.axis_dimension.min_value, self.axis_dimension.max_value
        )
        value_range = self.axis_dimension.max_value - self.axis_dimension.min_value
        self._grid_line_values = []
        for denominator in reversed(all_denominators):
            count = int(value_range / denominator)
            self._grid_line_values = [
                self.axis_dimension.min_value + (i * denominator)
                for i in reversed(range(count + 1))
            ]
            if len(self._grid_line_values) > 5:
                break
        # Reduce grid lines if too many
        while len(self._grid_line_values) > 10 and 0 not in self._grid_line_values:
            self._grid_line_values = [
                x for (i, x) in enumerate(self._grid_line_values) if i % 2 == 0
            ]

    @property
    def labels(self) -> list[MeasuredText]:
        return self._labels

    @labels.setter
    def labels(self, labels: Vector | list[str] = None) -> None:
        if not labels:
            labels = []
            precision = 0
            for label in self.values:
                if "." in str(label):
                    decimal_value = str(label).split(".")[-1]
                    if float(decimal_value) > 0:
                        precision = 1
                value = round(label, precision) if precision > 0 else int(label)
                labels.append(value)
        else:
            labels = [*labels]
        self._labels = [calculate_text_dimensions(label) for label in labels]

    @property
    def count(self) -> int:
        return len(self.values)


class XAxis(Axis):
    def reproject(self, value: float) -> float:
        if self.scale is not None and getattr(self.scale, "name", "linear") != "linear":
            return self.scale.reproject(value, self.parent.plot_width)
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

    @property
    def grid_lines(self) -> Path:
        if not self.config:
            return None

        # Split the config into major-line attrs and minor-grid params. A plain
        # string config yields the historical single-weight grid.
        major, minor = self._split_grid_config(self.config)

        # In stacked mode with negative values, the reproject formula is
        # relative to zero (value/range), so tick coordinates need to be
        # shifted right by reproject(abs(min_value)) to land at absolute
        # positions within the plot.
        dx = 0
        min_v = self.axis_dimension.min_value
        if self.stacked and min_v < 0:
            dx = self.reproject(abs(min_v))

        coordinates = list(self.coordinates)
        # Non-linear scales (time/log) own their tick positions, which land on
        # clean calendar/decade boundaries and rarely reach the right edge of
        # the plot. Linear axes always draw a gridline at the max value (the
        # right border), so add one here too when the last tick falls short.
        if self.scale is not None and getattr(self.scale, "name", "linear") != "linear":
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

    @property
    def axis_labels(self) -> G:
        labels = G(
            font_size=DEFAULT_FONT_SIZE,
            font_family=DEFAULT_FONT,
            fill=self.parent.theme.resolved_label_color
            if hasattr(self.parent, "theme")
            else "#444444",
            transform=translate(
                x=self.parent.left_padding,
                y=self.parent.top_padding + DEFAULT_PADDING,
            ),
        )

        rotation_angle = 0
        if self.parent.x_label_rotation:
            rotation_angle, _ = self.parent.x_label_rotation

        # Same absolute-position compensation as grid_lines.
        dx = 0
        min_v = self.axis_dimension.min_value
        if self.stacked and min_v < 0:
            dx = self.reproject(abs(min_v))

        y = self.parent.plot_height
        for x, label in zip(self.coordinates, self.labels):
            x = x + dx
            transformations = [translate(-label.width / 2, 0)]
            if rotation_angle > 0:
                transformations = [
                    translate(label.width / len(label.text) * -1, 0),
                    rotate(rotation_angle, x, y),
                ]
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

        offset = 0
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
    def grid_lines(self) -> Path:
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
        labels = G(
            font_size=DEFAULT_FONT_SIZE,
            font_family=DEFAULT_FONT,
            fill=self.parent.theme.resolved_label_color
            if hasattr(self.parent, "theme")
            else "#444444",
            transform=translate(
                x=(self.parent.left_padding - 6),
                y=self.parent.top_padding,
            ),
        )

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
                    labels.add_child(
                        self._wrapped_label(lines, y, label.height)
                    )
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
