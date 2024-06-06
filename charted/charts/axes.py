from typing import List
from charted.html.element import G, Text
from charted.utils.text import TextMeasurer
from charted.utils.transform import rotate, translate
from charted.utils.types import Labels, MeasuredText, Vector


class Axes(G):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_children(self.x_axis, self.y_axis)

    @property
    def x_axis(self) -> "XAxis":
        return XAxis(parent=self.parent)

    @property
    def y_axis(self) -> "YAxis":
        return YAxis(parent=self.parent)


class Axis(G):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def labels(self) -> Labels:
        return self._labels

    @labels.setter
    def labels(self, labels) -> None:
        with TextMeasurer() as tm:
            self._labels = [MeasuredText(x, *tm.measure_text(x)) for x in labels]


class YAxis(Axis):
    class_name = "y-axis"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kwargs["transform"] = translate(
            x=self.parent.padding * self.parent.width,
            y=self.parent.padding * self.parent.height,
        )
        self.labels = self.y_labels
        self.add_children(*self.axes_labels)

    @property
    def y_coordinates(self) -> Vector:
        arr = [*self.parent.plot.y_coordinates]
        arr.sort()
        return arr

    @property
    def y_labels(self) -> List[str]:
        labels = []
        z = self.parent._reproject_y(self.parent.bounds.y2)
        for y in self.y_coordinates:
            v = abs(self.parent._reverse_y(abs(y) - abs(z)))
            if y > z:
                v = -v
            labels.append(str(round(v)))
        return [*labels, "0"]

    @property
    def axes_labels(self) -> List[Text]:
        arr = []
        z = self.parent._reproject_y(self.parent.bounds.y2)
        for y, label in zip(
            [*self.y_coordinates, z],
            self.labels,
        ):
            text = Text(
                text=label.text,
                x=0,
                y=y,
                transform=translate(
                    x=-(label.width + 12),
                    y=label.height / 2,
                ),
                font_size=12,
                font_family="Verdana",
            )
            arr.append(text)
        return arr


class XAxis(Axis):
    class_name = "x-axis"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.labels = self.parent.labels
        self.kwargs["transform"] = translate(
            x=(self.parent.width * self.parent.padding),
            y="12",
        )
        self.add_children(*self.axes_labels)

    @property
    def x_coordinates(self) -> Vector:
        y = self.parent.height * (1 - self.parent.padding)
        return [(x + (self.parent.column_width / 2), y) for x in self.parent.x_ticks]

    @property
    def axes_labels(self) -> List[Text]:
        total_column_width = self.parent.no_columns * self.parent.column_width
        total_label_width = sum([label.width for label in self.labels])
        rotation_angle = TextMeasurer.calculate_rotation_angle(
            total_label_width,
            total_column_width,
        )

        return [
            Text(
                text=label.text,
                x=x,
                y=y,
                transform=[
                    translate(
                        x=(
                            -label.width / 2
                            if not rotation_angle
                            else label.width / len(label.text) * -1
                        ),
                        y=0,
                    ),
                    rotate(rotation_angle or 0, x, y),
                ],
                # TODO: Remove hardcoded font value
                font_size=12,
                font_family="Verdana",
            )
            for label, (x, y) in zip(self.labels, self.x_coordinates)
        ]
