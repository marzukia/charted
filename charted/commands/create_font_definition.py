import argparse

from charted.fonts.utils import create_font_definition


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a font definition for specified font within specified range."
    )

    parser.add_argument("font", type=str, help="The font name.")
    parser.add_argument(
        "min_font_size",
        nargs="?",
        type=int,
        help="The minimum font size.",
        default=8,
    )
    parser.add_argument(
        "max_font_size",
        nargs="?",
        type=int,
        help="The maximum font size.",
        default=21,
    )

    args = parser.parse_args()

    create_font_definition(args.font, args.min_font_size, args.max_font_size)
