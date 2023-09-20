import argparse
import logging
import logging.config
import os

from . import rectangle
from . import extender
from . import print_screen
from . import app_core

def main():
    ac = app_core.AppCore()

    # ihl ext -i img.jpg -o example.jpg -t TEXT -a center -s 50

    parser = argparse.ArgumentParser(
        description=f"Image High Lighter\n\n{ac.read_extended_help()}",
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers()

    rect_parser = subparsers.add_parser('rect', help="""
    LMB - draw rectangle
    MMB - crop
    RMB - add text
    
    LMB Double click - add number
    
    TAB - change color
    
    CTRL + 7 - add number to left top rectangle corner
    CTRL + 9 - add number to right top rectangle corner
    CTRL + 1 - add number to left bottom rectangle corner
    CTRL + 3 - add number to right bottom rectangle corner
    
    CTRL + 8 - add note above the rectangle
    CTRL + 2 - add note below the rectangle
    
    CTRL + Plus - increase size of rectangle border line
    CTRL + Minus - decrease size of rectangle border line
    
    ALT + Plus - increase alpha of rectangle background color
    ALT + Minus - - decrease alpha of rectangle background color
    
    SHIFT + Plus - increase font size
    SHIFT + Minus - decrease font size
    
    P - increase the number counter
    M - decrease the number counter
    
    ALT + I - increase alpha background color of number rectangle
    ALT + D - decrease alpha background color of number rectangle
    
    CTRL + O - open new instance of application with selected image
    CTRL + C - copy current image
    CTRL + Z - undo
    
    ESC - close the application
    """)
    rect_parser.set_defaults(func=rectangle.run)
    rect_parser.add_argument("-p", "--path", required=True)
    rect_parser.add_argument("-z", "--minimize", action='store_true')
    rect_parser.add_argument("-f", "--frameless", action='store_true')

    print_screen_parser = subparsers.add_parser('ps')
    print_screen_parser.set_defaults(func=print_screen.run)
    print_screen_parser.add_argument("-o", "--output", default="./print_screens/%Y.%m.%d_%H-%M-%S.png")
    print_screen_parser.add_argument("-b", "--backup", default=os.path.join(ac.app_directory(), r"backup/full/%Y.%m.%d/%Y.%m.%d_%H-%M-%S.png"))
    print_screen_parser.add_argument("--backup_directory", default=os.path.join(ac.app_directory(), r"backup/original/%Y.%m.%d/"))
    print_screen_parser.add_argument("-r", "--rect", action='store_true')
    print_screen_parser.add_argument("-z", "--rect_minimize", action='store_true')
    print_screen_parser.add_argument("-f", "--rect_frameless", action='store_true')
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

    batch_rect_parser = subparsers.add_parser('bect')
    batch_rect_parser.set_defaults(func=rectangle.run_for_all)
    batch_rect_parser.add_argument("-z", "--rect_minimize", action='store_true')

    font_test_parser = subparsers.add_parser('font-test')
    font_test_parser.set_defaults(func=extender.run_font_test)
    font_test_parser.add_argument("-i", "--image_path")
    font_test_parser.add_argument("-d", "--fonts_directory")

    arguments = parser.parse_args()
    arguments.func(arguments)

# TODO: Rectangle - CTRL + O

# TODO: Rectangle - Nastaveni tloustky cary
# TODO: Rectangle - Nastaveni alpha pro vypln ctverce
# TODO: Rectangle - Nastaveni fontu a velikosti
# TODO: Rectangle - Hezci okno pro text nebo nazornejsi pridavani textu
# TODO: Rectangle - Funkce prohlizece v adresari sipky
# TODO: Rectangle - Pridani a odstraneni head / foot
# TODO: Rectangle - Frameless ui.setWindowFlags(QtCore.Qt.FramelessWindowHint)
# TODO: Rectangle - Nastrojova a stavova lista
# TODO: Rectangle - Crop mimo aktualni view
# TODO: Rectangle - Hezci scrollbary
# TODO: Rectangle - Hezci background color
# TODO: Rectangle - Vyrezat vlozit
# TODO: Rectangle - Vlozit CTRL + V posunout

# TODO: Aplikace co posloucha Print Screen key press event

# TODO: extender - pridani podle konfigu [] + variables
# TODO: extender - hromadne zpracovani podle konfigu, na jednom radku left, center, right
# TODO: extender - gradient
# TODO: extender - propracovanejsi extended area

# TODO: Idea backup machine - vytvori zip a ulozi na standardni misto

# https://stackoverflow.com/questions/34697559/pil-image-to-qpixmap-conversion-issue
# from PIL.ImageQt import ImageQt
# qim = ImageQt(im)
# pix = QtGui.QPixmap.fromImage(qim)
