from charted.utils.colors import (
    complementary_color,
    generate_complementary_colors,
    hex_to_rgb,
    rgb_to_hex,
)


def test_hex_to_rgb():
    rgb = hex_to_rgb("#ff0000")
    assert rgb == (255, 0, 0)


def test_rgb_to_hex():
    hex = rgb_to_hex((255, 0, 0))
    assert hex == "#ff0000"


def test_complementary_color():
    color = complementary_color("#ff0000")
    assert color is not None
    assert type(color) is str
    assert color[0] == "#"


def test_generate_complementary_colors():
    inputs = ["#ff0000", "#00ff00"]
    colors = []
    for color in generate_complementary_colors(inputs):
        colors.append(color)
    assert len(colors) == 2
    for color in colors:
        assert color is not None
        assert type(color) is str
        assert color[0] == "#"
