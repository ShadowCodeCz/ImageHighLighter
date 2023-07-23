import argparse
import logging
import logging.config


from . import rectangle
from . import extender
from . import print_screen

def main():
    parser = argparse.ArgumentParser(
        description="Image High Lighter",
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers()

    rect_parser = subparsers.add_parser('rect')
    rect_parser.set_defaults(func=rectangle.run)
    rect_parser.add_argument("-p", "--path", required=True)
    rect_parser.add_argument("-z", "--minimize", action='store_true')

    print_screen_parser = subparsers.add_parser('ps')
    print_screen_parser.set_defaults(func=print_screen.run)
    print_screen_parser.add_argument("-o", "--output", default="./print_screens/%Y.%m.%d_%H-%M-%S.png")
    print_screen_parser.add_argument("-b", "--backup", default=r"C:\Users\sedaj/ihl/backup/full/%Y.%m.%d/%Y.%m.%d_%H-%M-%S.png")
    print_screen_parser.add_argument("--backup_directory", default=r"C:\Users\sedaj/ihl/backup/original/%Y.%m.%d/")
    print_screen_parser.add_argument("-r", "--rect", action='store_true')
    print_screen_parser.add_argument("-z", "--rect_minimize", action='store_true')
    print_screen_parser.add_argument("-m", "--monitor", default=2)
    print_screen_parser.add_argument("-v", "--variables", default=[], nargs='*')

    extender_parser = subparsers.add_parser('ext')
    extender_parser.set_defaults(func=extender.run)
    extender_parser.add_argument("-i", "--image_path")
    extender_parser.add_argument("-o", "--output_path", default=None, help="If it is not set. The original image will overwrite.")
    extender_parser.add_argument("-p", "--position", default="head", help="foot, head")
    extender_parser.add_argument("-t", "--text", required=True)
    extender_parser.add_argument("-a", "--text_align", default="center", help="left, center, right")
    extender_parser.add_argument("-c", "--text_color", default="#FFFFFF", help="#FFFFFF, FFFFFF")
    extender_parser.add_argument("-b", "--background_color", default="#000000", help="#000000")
    extender_parser.add_argument("-f", "--font_path", default="FONTS/arial.ttf", help="FONTS/arial.ttf")
    extender_parser.add_argument("-s", "--font_size", default=34, help="34")
    extender_parser.add_argument("-v", "--vertical_padding", default=10, help="10")
    extender_parser.add_argument("-n", "--horizontal_padding", default=10, help="10")

    extender_parser = subparsers.add_parser('bect')
    extender_parser.set_defaults(func=rectangle.run_for_all)
    extender_parser.add_argument("-z", "--rect_minimize", action='store_true')

    arguments = parser.parse_args()
    arguments.func(arguments)


# TODO: Extender gradient
# TODO: Extender Config
# TODO: Extender Path template