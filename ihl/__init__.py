import argparse
import logging
import logging.config


from . import rectangle
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

    print_screen_parser = subparsers.add_parser('ps')
    print_screen_parser.set_defaults(func=print_screen.run)
    print_screen_parser.add_argument("-o", "--output", default="./print_screens/%Y.%m.%d_%H-%M-%S.png")
    print_screen_parser.add_argument("-b", "--backup", default=r"C:\Users\sedaj/ihl/backup/full/%Y.%m.%d/%Y.%m.%d_%H-%M-%S.png")
    print_screen_parser.add_argument("--backup_directory", default=r"C:\Users\sedaj/ihl/backup/original/%Y.%m.%d/")
    print_screen_parser.add_argument("-r", "--rect", action='store_true')
    print_screen_parser.add_argument("-m", "--monitor", default=2)
    print_screen_parser.add_argument("-v", "--variables", default=[], nargs='*')

    arguments = parser.parse_args()
    arguments.func(arguments)

