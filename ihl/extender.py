# https://stackoverflow.com/questions/43295189/extending-a-image-and-adding-text-on-the-extended-area-using-python-pil
# https://stackoverflow.com/questions/72844672/how-would-i-use-pil-to-extend-an-image-and-then-draw-a-black-rectangle-with-t
# https://stackoverflow.com/questions/58806198/python-pil-add-text-before-image-on-top-of-image-not-on-the-image

# Text size
# https://stackoverflow.com/questions/43828955/measuring-width-of-text-python-pil
# https://www.fontspace.com/category/retro

from PIL import Image, ImageFont, ImageDraw


def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


def hex_to_rgb(hexadecimal_color):
    rgb = []
    value = hexadecimal_color.replace("#", "")
    for i in (0, 2, 4):
        decimal = int(value[i:i + 2], 16)
        rgb.append(decimal)

    return tuple(rgb)


def run(arguments):
    extension = Extension()
    extension.image_path = arguments.image_path
    extension.position = arguments.position
    extension.text = arguments.text
    extension.text_align = arguments.text_align
    extension.text_color = hex_to_rgb(arguments.text_color)
    extension.background_color = hex_to_rgb(arguments.background_color)
    extension.font_path = arguments.font_path
    extension.font_size = arguments.font_size
    extension.vertical_padding = arguments.vertical_padding
    extension.horizontal_padding = arguments.horizontal_padding

    extender = ImageExtender()
    extender.add_extension(extension)
    if arguments.output_path == None:
        extender.save(extension.image_path)
    else:
        extender.save(arguments.output_path)


class Extension:
    def __init__(self):
        self.image_path = None
        self.position = None
        self.text = None
        self.text_align = None
        self.text_color = None
        self.background_color = None
        self.font_path = None
        self.font_size = None
        self.vertical_padding = None
        self.horizontal_padding = None

    @property
    def font(self):
        return ImageFont.truetype(self.font_path, self.font_size)


class ImageExtender:
    def __init__(self):
        self.image = None

    def extend(self, x_extension, y_extension, x_paste, y_paste, color=(0, 0, 0)):
        base_size = self.image.size
        new_size = (base_size[0] + x_extension, base_size[1] + y_extension)
        new_img = Image.new("RGB", new_size, color)
        new_img.paste(self.image, (x_paste, y_paste))

        self.image = new_img

    def add_text(self, text, position, font, color):
        draw = ImageDraw.Draw(self.image)
        draw.text(position, text, color, font=font)

    def add_extension(self, extension):
        self.image = Image.open(extension.image_path)
        if extension.position == "head":
            self.add_header(extension)
        if extension.position == "foot":
            self.add_footer(extension)

    def count_x_position(self, extension, text_box):
        if extension.text_align == "left":
            return int(extension.vertical_padding)
        if extension.text_align == "center":
            return int((self.image.size[0] / 2) - (text_box[2] / 2))
        if extension.text_align == "right":
            return int(self.image.size[0] - text_box[2] - extension.vertical_padding)

    def add_header(self, extension):
        draw = ImageDraw.Draw(self.image)
        tb = draw.textbbox((float(0.0), float(0.0)), extension.text, extension.font)
        self.extend(
            0,
            int(tb[3] + extension.vertical_padding * 2),
            0,
            int(tb[3] + extension.vertical_padding * 2),
            extension.background_color
        )
        self.add_text(
            extension.text,
            (self.count_x_position(extension, tb), extension.vertical_padding),
            extension.font,
            extension.text_color
        )

    def add_footer(self, extension):
        base_size = self.image.size
        draw = ImageDraw.Draw(self.image)
        tb = draw.textbbox((float(0.0), float(0.0)), extension.text, extension.font)
        self.extend(
            0,
            int(tb[3] + extension.vertical_padding * 2),
            0,
            0,
            extension.background_color
        )
        self.add_text(
            extension.text,
            (self.count_x_position(extension, tb), base_size[1] + extension.vertical_padding),
            extension.font,
            extension.text_color
        )

    def save(self, path):
        self.image.save(path)
