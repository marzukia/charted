from typing import List
from charted.html.element import G, Text
from charted.utils.text import TextMeasurer, calculate_rotation_angle
from charted.utils.transform import rotate, translate
from charted.utils.types import Coordinate, Labels, MeasuredText, Vector


class Axis(G):
    def __init__(self, labels: Labels, coordinates: List[Coordinate], **kwargs):
        super().__init__(**kwargs)
        self.labels = labels
        self.coordinates = coordinates

    @property
    def labels(self) -> Labels:
        return self._labels

    @labels.setter
    def labels(self, labels) -> None:
        with TextMeasurer() as tm:
            self._labels = [MeasuredText(x, tm.measure_text(x)) for x in labels]


class XAxis(Axis):
    class_name = "x-axis"

    def __init__(
        self,
        labels: Labels,
        width: float,
        padding: float,
        no_columns: int,
        column_width: float,
        coordinates: Vector,
        **kwargs
    ):
        kwargs["transform"] = translate(
            x=(width * padding),
            y="12",
        )
        super().__init__(labels=labels, coordinates=coordinates, **kwargs)
        self.column_width = column_width
        self.no_columns = no_columns
        self.add_children(*self.axes_labels)

    @property
    def axes_labels(self) -> List[Text]:
        total_column_width = self.no_columns * self.column_width
        total_label_width = sum([l.width for l in self.labels])
        rotation_angle = calculate_rotation_angle(total_label_width, total_column_width)

        return [
            Text(
                text=l.text,
                x=x,
                y=y,
                transform=[
                    translate(
                        x=(
                            l.width / -2
                            if not rotation_angle
                            else l.width / len(l.text) * -1
                        ),
                        y=0,
                    ),
                    rotate(rotation_angle, x, y),
                ],
                # TODO: Remove hardcoded font value
                font_size=12,
                font_family="Verdana",
            )
            for l, (x, y) in zip(self.labels, self.coordinates)
        ]
