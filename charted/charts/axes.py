import math

from charted.constants import DEFAULT_PADDING
from charted.html.element import G, Path, Text
from charted.utils.defaults import DEFAULT_FONT, DEFAULT_FONT_SIZE
from charted.utils.helpers import (
    calculate_text_dimensions,
    parse_tick_interval,
    round_to_clean_number,
)
from charted.utils.themes import GridConfig
from charted.utils.transform import rotate, translate
from charted.utils.types import AxisDimension, MeasuredText, Vector, Vector2D


class Axis(G):
    def __init__(
        self,
        parent: object,
        data: Vector2D | None = None,
        labels: list[str] | None = None,
        stacked: bool = False,
        zero_index: bool = True,
        config: GridConfig | None = None,
        axis_tick_interval: float | str | None = None,
    ):
        if not data and not labels:
            raise Exception("Need labels or data.")
        elif not data and labels:
            labels = [" ", *labels, " "]
            data = [[i for i in range(len(labels))]]

        self.stacked = stacked
        self.data = data
        self.parent = parent
        self.axis_tick_interval = axis_tick_interval
        self.values = (data, labels, zero_index)
        self.labels = labels
        self.config = config
        self.add_children(self.grid_lines, self.axis_labels)

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

        # Handle values between -1 and 1
        if abs(min_value) < 1 and abs(max_value) <= 1:
            min_value = math.floor(min_value)
            max_value = math.ceil(max_value)

        # Ensure zero is included if zero_index is True
        # - If all values are positive, set min to 0
        # - If all values are negative, set max to 0
        if zero_index:
            if min_value > 0:
                min_value = 0
            elif max_value < 0:
                max_value = 0

        # Clean up min/max for non-labeled axes
        if not has_labels:
            if min_value < 0:
                min_value = -round_to_clean_number(abs(min_value))
            else:
                min_value = round_to_clean_number(min_value, round_down=True)
            max_value = round_to_clean_number(max_value)

        return AxisDimension(min_value, max_value, count)

    @classmethod
    def _choose_tick_step(cls, value_range: float, max_ticks: int) -> float:
        """Choose a clean step size for ticks based on the range.

        Uses standard "nice" number progression: 1, 2, 5, 10, 20, 50, 100, etc.
        """
        if value_range <= 0:
            return 1.0

        # Calculate ideal step to get close to max_ticks
        ideal_step = value_range / max_ticks

        # Get the order of magnitude
        if ideal_step == 0:
            return 1.0
        magnitude = 10 ** math.floor(math.log10(ideal_step))

        # Normalize to [1, 10)
        normalized = ideal_step / magnitude

        # Choose from nice numbers: 1, 2, 5
        if normalized <= 1:
            step = 1
        elif normalized <= 2:
            step = 2
        elif normalized <= 5:
            step = 5
        else:
            step = 10

        return step * magnitude

    @classmethod
    def generate_tick_values(
        cls,
        min_value: float,
        max_value: float,
        axis_tick_interval: float | str | None = None,
        max_ticks: int = 10,
    ) -> tuple[list[float], list[float]]:
        """Generate tick values for both labels and grid lines.

        Args:
            min_value: Minimum axis value
            max_value: Maximum axis value
            axis_tick_interval: Optional tick interval (numeric or percentage string)
                - int: Show every Nth tick label
                - str with '%': Show percentage of tick labels (e.g., "25%")
                - float < 1: Show proportion of tick labels (e.g., 0.25 = 25%)
            max_ticks: Maximum number of ticks to generate

        Returns:
            Tuple of (label_values, grid_values) where:
            - label_values: Filtered tick values for display (respects tick_interval)
            - grid_values: All tick values for grid line rendering (always includes 0 if spanned)
        """
        value_range = max_value - min_value

        # Handle zero or near-zero range
        if value_range == 0:
            return ([min_value], [min_value])

        # Choose a clean step size
        step = cls._choose_tick_step(value_range, max_ticks)

        # Calculate tick positions aligned to the step
        # Start from a nice round number <= min_value
        start_tick = math.floor(min_value / step) * step
        end_tick = math.ceil(max_value / step) * step

        # Generate all tick positions (uniform spacing)
        num_ticks = int(round((end_tick - start_tick) / step)) + 1
        all_ticks = [round(start_tick + i * step, 6) for i in range(num_ticks)]

        # Ensure we have at least one tick
        if not all_ticks:
            all_ticks = [min_value]

        # Grid values: start with all ticks
        grid_values = all_ticks.copy()

        # Ensure 0 is included when the axis spans across zero (if not already present)
        if min_value < 0 < max_value:
            has_zero = any(abs(t) < 1e-9 for t in grid_values)
            if not has_zero:
                # Insert 0 at the correct position to maintain order
                zero_idx = int(round(abs(min_value) / step))
                grid_values.insert(zero_idx, 0.0)

        # Determine the interval for filtering labels
        if axis_tick_interval is not None:
            parsed_interval = parse_tick_interval(axis_tick_interval, len(grid_values))
            label_interval = (
                parsed_interval if parsed_interval and parsed_interval > 1 else 1
            )
        else:
            # Default: limit to max_ticks by filtering
            if len(grid_values) > max_ticks:
                label_interval = math.ceil(len(grid_values) / max_ticks)
            else:
                label_interval = 1

        # Label values: apply tick interval filtering from grid_values
        # Key insight: when spanning zero, adjust start index so 0 is always selected
        # This ensures 0 is labeled while maintaining uniform intervals
        if min_value < 0 < max_value and label_interval > 1:
            # Find where 0 is in grid_values
            zero_idx_in_grid = next(
                i for i, v in enumerate(grid_values) if abs(v) < 1e-9
            )

            # Calculate the "phase" - what offset would make 0 land on a selected index
            # We want: (zero_idx_in_grid - offset) % label_interval == 0
            # So: offset = zero_idx_in_grid % label_interval
            offset = zero_idx_in_grid % label_interval

            # Filter with the offset adjustment
            label_values = [
                t
                for i, t in enumerate(grid_values)
                if (i - offset) % label_interval == 0
            ]
        else:
            # Standard filtering without zero alignment
            if label_interval > 1:
                label_values = [
                    t for i, t in enumerate(grid_values) if i % label_interval == 0
                ]
            else:
                label_values = grid_values.copy()

        return label_values, grid_values

    @classmethod
    def calculate_axis_values(
        cls,
        data: Vector2D,
        labels: list[str] | None = None,
        zero_index: bool = True,
        stacked: bool | None = None,
        axis_tick_interval: int | None = None,
    ) -> tuple[AxisDimension, list[float], list[float]]:
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

            # Ensure zero is included in values when spanning negative to positive
            if min_val < 0 < max_val and 0 not in values:
                values = sorted(values + [0])

            # Apply tick interval filtering if specified (for numeric X-axes with labels)
            # This handles XY charts where both x_data and x_labels are provided
            if axis_tick_interval is not None and min_val != max_val:
                parsed_interval = parse_tick_interval(axis_tick_interval, len(values))
                if parsed_interval and parsed_interval > 1:
                    # When spanning zero, adjust offset so 0 is always selected
                    if min_val < 0 < max_val:
                        zero_idx_in_values = next(
                            i for i, v in enumerate(values) if abs(v) < 1e-9
                        )
                        offset = zero_idx_in_values % parsed_interval
                        values = [
                            v
                            for i, v in enumerate(values)
                            if (i - offset) % parsed_interval == 0
                        ]
                    else:
                        values = [
                            v for i, v in enumerate(values) if i % parsed_interval == 0
                        ]

            return (axd, values, grid_line_values)

        # Use the new tick generation logic
        label_values, grid_values = cls.generate_tick_values(
            min_value=axd.min_value,
            max_value=axd.max_value,
            axis_tick_interval=axis_tick_interval,
        )

        return (
            AxisDimension(axd.min_value, axd.max_value, axd.count),
            label_values,
            grid_values,
        )

    def reverse(self, value: float) -> float:
        raise Exception("reverse not implemented for instance of Axis.")

    @property
    def zero(self) -> float:
        return self.reproject(0)

    @property
    def grid_lines(self) -> Path:
        raise Exception("grid_lines not implemented for instance of Axis.")

    @property
    def axis_labels(self) -> G:
        raise Exception("axis_labels not implemented for instance of Axis.")

    @property
    def reprojected_values(self):
        return [self.reproject(v) for v in self.values]

    @property
    def values(self) -> Vector:
        return self._values

    @values.setter
    def values(
        self,
        kwargs: tuple[
            Vector2D,
            list[str] | None,
            bool,
        ],
    ) -> None:
        data, labels, zero_index = kwargs
        self.axis_dimension, self._values, self._grid_line_values = (
            self.calculate_axis_values(
                data=data,
                stacked=self.stacked,
                labels=labels,
                zero_index=zero_index,
                axis_tick_interval=self.axis_tick_interval,
            )
        )

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
            # When labels are provided but values have been filtered (via tick_interval),
            # we need to filter the labels to match the filtered values.
            # Map original data values to their corresponding labels, then filter.
            if self.data and len(self.data) > 0:
                original_values = list(self.data[0])
                # Create a mapping from original values to labels
                value_to_label = {}
                for i, val in enumerate(original_values):
                    if i < len(labels):
                        value_to_label[val] = labels[i]

                # Filter labels to match self.values (which may be filtered)
                filtered_labels = []
                for val in self.values:
                    # Find the closest original value (for floating point tolerance)
                    closest_val = min(original_values, key=lambda x: abs(x - val))
                    if closest_val in value_to_label:
                        filtered_labels.append(value_to_label[closest_val])

                labels = (
                    filtered_labels if filtered_labels else labels[: len(self.values)]
                )
            else:
                labels = labels[: len(self.values)]

        self._labels = [calculate_text_dimensions(label) for label in labels]

    @property
    def count(self) -> int:
        return len(self.values)


class XAxis(Axis):
    def reproject(self, value: float) -> float:
        return self._reproject(
            value,
            self.axis_dimension.max_value,
            self.axis_dimension.min_value,
            self.parent.plot_width,
            self.stacked,
        )

    def reverse(self, value: float) -> float:
        return self._reverse(
            value,
            self.axis_dimension.max_value,
            self.axis_dimension.min_value,
            self.parent.plot_width,
        )

    @property
    def coordinates(self):
        return [self.reproject(i) for i in self._grid_line_values]

    @property
    def grid_lines(self) -> Path:
        if not self.config:
            return None

        # In stacked mode with negative values, the reproject formula is
        # relative to zero (value/range), so tick coordinates need to be
        # shifted right by reproject(abs(min_value)) to land at absolute
        # positions within the plot.
        dx = 0
        min_v = self.axis_dimension.min_value
        if self.stacked and min_v < 0:
            dx = self.reproject(abs(min_v))

        d = [f"M{x + dx} {0} v{self.parent.plot_height}" for x in self.coordinates]
        return Path(
            **self.config,
            d=d,
            transform=translate(
                x=self.parent.left_padding,
                y=self.parent.top_padding,
            ),
        )

    @property
    def axis_labels(self) -> G:
        labels = G(
            font_size=DEFAULT_FONT_SIZE,
            font_family=DEFAULT_FONT,
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

        # Use values positions for labels (not all grid line positions)
        # This ensures labels are positioned at the correct filtered tick locations
        label_positions = [self.reproject(v) for v in self.values]

        for x, label in zip(label_positions, self.labels):
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
        return self._reproject(
            value,
            self.axis_dimension.max_value,
            self.axis_dimension.min_value,
            self.parent.plot_height,
            self.stacked,
        )

    def reverse(self, value: float) -> float:
        return self._reverse(
            value,
            self.axis_dimension.max_value,
            self.axis_dimension.min_value,
            self.parent.plot_height,
        )

    @property
    def coordinates(self):
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

        d = [f"M{0} {y} h{self.parent.plot_width}" for y in self.coordinates]
        return Path(
            **self.config,
            d=d,
            transform=translate(
                x=self.parent.left_padding,
                y=self.parent.top_padding,
            ),
        )

    @property
    def axis_labels(self) -> G:
        labels = G(
            font_size=DEFAULT_FONT_SIZE,
            font_family=DEFAULT_FONT,
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
            y_offset = -label.height / 2 if bar_height is not None else label.height / 4
            text = Text(
                x=0,
                y=y,
                text=label.text,
                transform=translate(
                    x=-label.width,
                    y=y_offset,
                ),
            )
            labels.add_child(text)
        return labels
