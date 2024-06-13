from charted.html.element import G, Path, Text
from charted.utils.defaults import DEFAULT_FONT, DEFAULT_FONT_SIZE
from charted.utils.helpers import (
    calculate_rotation_angle,
    calculate_text_dimensions,
    common_denominators,
    round_to_clean_number,
)
from charted.utils.transform import rotate, translate
from charted.utils.types import AxisDimension, MeasuredText, Vector, Vector2D


class Axis(G):
    def __init__(
        self,
        parent: object,
        data: Vector2D | None = None,
        labels: list[str] | None = None,
        stacked: bool = False,
    ):
        if not data and not labels:
            raise Exception("Need labels or data.")
        elif not data and labels:
            labels = [" ", *labels, " "]
            data = [[i for i in range(len(labels))]]

        self.stacked = stacked
        self.data = data
        self.parent = parent
        self.values = data
        self.labels = labels
        self.add_children(self.grid_lines, self.axis_labels)

    @classmethod
    def _reproject(
        cls,
        value: float,
        max_value: float,
        min_value: float,
        length: float,
    ) -> float:
        value_range = max_value - min_value
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
        normalised_value = value / length
        return normalised_value * value_range

    @classmethod
    def calculate_axis_dimensions(
        cls,
        data: Vector2D | None = None,
        stacked: bool = False,
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
            min_values = min(min_values)
            max_values = max(max_values)
        else:
            agg = [x for arr in data for x in arr]
            min_values = min(agg)
            max_values = max(agg)

        if min_values >= 1:
            min_values = 0

        return AxisDimension(
            round_to_clean_number(min_values),
            round_to_clean_number(max_values),
            min_values,
            max_values,
            count,
        )

    @classmethod
    def calculate_axis_values(cls, data: Vector2D, **kwargs) -> float:
        axd = cls.calculate_axis_dimensions(data, **kwargs)
        denominators = common_denominators(axd.min_value, axd.max_value)

        values = []
        for denominator in reversed(denominators):
            count = int(axd.value_range / denominator)
            values = [axd.min_value + (i * denominator) for i in reversed(range(count))]
            if len(values) > 5 or len(values) == axd.count:
                break

        return values

    def reproject(self, value: float) -> float:
        raise Exception("reproject not implemented for instance of Axis.")

    def reverse(self, value: float) -> float:
        raise Exception("reverse not implemented for instance of Axis.")

    @property
    def axis_dimension(self) -> AxisDimension:
        return self.calculate_axis_dimensions(
            data=self.data,
            stacked=self.stacked,
        )

    @property
    def zero(self) -> float:
        return self.reproject(abs(self.axis_dimension.min_value))

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
    def values(self, data: Vector2D) -> None:
        self._values = self.calculate_axis_values(data=data, stacked=self.stacked)

    @property
    def labels(self) -> list[MeasuredText]:
        return self._labels

    @labels.setter
    def labels(self, labels: Vector | list[str] = None) -> None:
        if not labels:
            labels = []
            precision = 0
            for label in [self.axis_dimension.max_value, *self.values]:
                if "." in str(label):
                    decimal_value = str(label).split(".")[-1]
                    if float(decimal_value) > 0:
                        precision = 1
                value = round(label, precision) if precision > 0 else int(label)
                labels.append(value)
        else:
            labels = list(reversed(labels))
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
        )

    def reverse(self, value: float) -> float:
        return self._reverse(
            value,
            self.axis_dimension.max_value,
            self.axis_dimension.min_value,
            self.plot_width,
        )

    @property
    def coordinates(self):
        count = len(self.values)
        spacing = self.axis_dimension.value_range / count
        reprojected_spacing = self.reproject(spacing)
        return list(reversed([i * reprojected_spacing for i in range(count + 1)]))

    @property
    def grid_lines(self) -> Path:
        d = [f"M{x} {0} v{self.parent.plot_height}" for x in self.coordinates]
        return Path(
            d=d,
            stroke="#CCCCCC",
            transform=translate(
                x=self.parent.h_pad,
                y=self.parent.v_pad,
            ),
        )

    @property
    def axis_labels(self) -> G:
        labels = G(
            font_size=DEFAULT_FONT_SIZE,
            font_family=DEFAULT_FONT,
            transform=translate(
                x=self.parent.h_pad,
                y=self.parent.v_pad + 18,
            ),
        )

        rotation_angle = 0
        for label in self.labels:
            angle = calculate_rotation_angle(label.width, self.parent.x_width)
            if angle and (angle > rotation_angle):
                rotation_angle = max(angle, rotation_angle)
        cum_width = sum([label.width for label in self.labels])
        rotation_angle = calculate_rotation_angle(cum_width, self.parent.plot_width)

        y = self.parent.plot_height
        for x, label in zip(self.coordinates, self.labels):
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
        )

    def reverse(self, value: float) -> float:
        return self._reverse(
            value,
            self.axis_dimension.max_value,
            self.axis_dimension.min_value,
            self.plot_height,
        )

    @property
    def coordinates(self):
        count = len(self.values)
        spacing = self.axis_dimension.value_range / count
        reprojected_spacing = self.reproject(spacing)
        return [i * reprojected_spacing for i in range(count + 1)]

    @property
    def grid_lines(self) -> Path:
        d = [f"M{0} {y} h{self.parent.plot_width}" for y in self.coordinates]
        return Path(
            d=d,
            stroke="#CCCCCC",
            transform=translate(
                x=self.parent.h_pad,
                y=self.parent.v_pad,
            ),
        )

    @property
    def axis_labels(self) -> G:
        labels = G(
            font_size=DEFAULT_FONT_SIZE,
            font_family=DEFAULT_FONT,
            transform=translate(
                x=(self.parent.h_pad - 6),
                y=self.parent.v_pad,
            ),
        )

        for y, label in zip(self.coordinates, self.labels):
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
