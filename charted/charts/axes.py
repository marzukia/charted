from typing import List
from charted.fonts.utils import (
    DEFAULT_FONT,
    DEFAULT_FONT_SIZE,
    calculate_rotation_angle,
    calculate_text_dimensions,
)
from charted.html.element import G, Text
from charted.utils.transform import rotate, translate
from charted.utils.types import Labels, Vector


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
        self._labels = [calculate_text_dimensions(x) for x in labels]


class YAxis(Axis):
    class_name = "y-axis"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kwargs["transform"] = translate(
            x=self.parent.padding * self.parent.width,
            y=self.parent.padding * self.parent.height,
        )
        self.labels = self.y_labels
        self.add_child(self.axes_labels)

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
    def axes_labels(self) -> G:
        g = G(font_size=DEFAULT_FONT_SIZE, font_family=DEFAULT_FONT)
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
            )
            g.add_child(text)
        return g


class XAxis(Axis):
    class_name = "x-axis"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.labels = self.parent.labels
        self.kwargs["transform"] = translate(
            x=(self.parent.width * self.parent.padding),
            y="12",
        )
        self.add_child(self.axes_labels)

    @property
    def x_coordinates(self) -> Vector:
        y = self.parent.height * (1 - self.parent.padding)
        x_width = self.parent.plot_width / self.parent.x_count
        if self.parent.x_width == x_width:
            return [(x + x_width, y) for x in self.parent.x_ticks]

        return [(x + (self.parent.x_width / 2), y) for x in self.parent.x_ticks]

    @property
    def axes_labels(self) -> G:
        g = G(font_size=DEFAULT_FONT_SIZE, font_family=DEFAULT_FONT)
        rotation_angle = 0

        for label in self.labels:
            angle = calculate_rotation_angle(label.width, self.parent.x_width)
            if angle and (angle > rotation_angle):
                rotation_angle = angle

        g.add_children(
            *[
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
                )
                for label, (x, y) in zip(self.labels, self.x_coordinates)
            ]
        )

        return g
