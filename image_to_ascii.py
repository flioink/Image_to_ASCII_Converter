import os.path
from PIL import Image, ImageDraw, ImageFont
import cv2


class ImageToAsciiConverter:
    def __init__(self, width=120, charset=None):

        self.width = width
        self.ADJUSTED_RATIO = 0.5
        self.CHAR_ASPECT_RATIO = 1.3
        self.default_font_name = "DejaVuSansMono.ttf"
        self.default_font = self.default_font_name

        self.img = None
        self.ascii_image = None
        self.ascii_image_height = None
        self.ascii_image_width = None

        if charset:
            self.charset = charset

        else:
            self.charset = ["@", "#", "8", "&", "W", "M", "B", "Q", "H", "D",
                            "X", "Y", "O", "C", "I", "*", "!", ";", ":", ".", " "]  # 21 chars

        self.scale_factor = 256 / len(self.charset)  # normalize the value so it doesn't exceed the index of the set


    def open_image(self, img_path):
        if isinstance(img_path, str):  # If it's a file path
            try:
                self.img = Image.open(img_path)
            except FileNotFoundError as e:
                print(f"Error: {e}")
                return False

        else:  # If it's an OpenCV frame (NumPy array)
            self.img = Image.fromarray(cv2.cvtColor(img_path, cv2.COLOR_BGR2RGB))

        return True

    def resize_image(self):
        # Resize
        aspect_ratio = self.img.height / self.img.width
        self.new_height = int(aspect_ratio * self.width * self.ADJUSTED_RATIO)
        self.original_img = self.img.resize((self.width, self.new_height))
        self.img = self.img.resize((self.width, self.new_height)).convert("L")

    def ascii_conversion(self):
        self.pixels = self.img.getdata()
        self.pixels_colors = self.original_img.getdata()
        # print(len(self.pixels_colors), len(self.pixels))

        self.new_pixels = [self.charset[min(int(pixel / self.scale_factor), len(self.charset) - 1)] for pixel in self.pixels]

        self.colored_symbols = list(zip(self.new_pixels, self.pixels_colors))
        # print(self.colored_symbols[0])

        self.ascii_image = []
        for i in range(0, len(self.colored_symbols), self.width):
            row = self.colored_symbols[i:i+self.width]  # Join characters into a row
            self.ascii_image.append(row)  # Store the row

        # self.ascii_image_str = "\n".join(self.ascii_image)

    def load_font(self, font=None):
        font_path = font if font and os.path.exists(font) else self.default_font
        try:
            self.font = ImageFont.truetype(font_path, 11)
            self.font_width, self.font_height = self.font.getbbox("A")[2:4]

        except IOError:
            print(f"Error loading font: {font_path}. Reverting to default.")

            self.font = ImageFont.truetype(self.default_font, 11)
            self.font_width, self.font_height = self.font.getbbox("A")[2:4]

    def get_ascii_image_dimensions(self):
        # Calculate the proper image dimensions
        self.ascii_image_width = self.width * self.font_width
        print(f"ascii_width: {self.ascii_image_width}")
        self.ascii_image_height = int(self.new_height * self.CHAR_ASPECT_RATIO) * self.font_height
        print(f"ascii_height: {self.ascii_image_height}")

    def create_ascii_image(self):
        # Create a blank white image
        self.ascii_image_result = Image.new("RGB", (self.ascii_image_width, self.ascii_image_height), "white")
        self.ascii_drawn = ImageDraw.Draw(self.ascii_image_result)

        # Draw the ASCII text
        #self.ascii_drawn.text((0, 0), self.ascii_image_str, font=self.font, fill=(0, 0, 0))

        for y, row in enumerate(self.ascii_image):
            for x, (char, color) in enumerate(row):  # Extract character and (R, G, B)
                self.ascii_drawn.text(
                    (x * self.font_width, y * self.font_height * self.CHAR_ASPECT_RATIO),
                    char,
                    font=self.font,
                    fill=color
                )


        return self.ascii_image_result

    def convert(self, img_path, font=None):
        if self.open_image(img_path):

            self.resize_image()
            self.ascii_conversion()
            self.load_font(font) if font else self.load_font()
            self.get_ascii_image_dimensions()
            return self.create_ascii_image()



if __name__ == "__main__":

    # test set
    detailed_set = [
    "@", "B", "%", "8", "&", "W", "M", "#", "*", "o", "a", "h", "k", "b", "d", "p", "q", "w", "m",
    "Z", "O", "0", "Q", "L", "C", "J", "U", "Y", "X", "z", "c", "v", "u", "n", "x", "r", "j", "f", "t",
    "/", "|", "(", ")", "1", "{", "}", "[", "]", "?", "-", "_", "+", "~", "<", ">", "i", "!", "l", "I",
    ";", ":", ",", "\"", "^", "`", "'.", " "
]

    # converter = ImageToAsciiConverter(width=150, charset=detailed_set)
    converter = ImageToAsciiConverter()
    ascii_img = converter.convert("test_images/da.jpg")
    ascii_img.show()

# for i, line in enumerate(self.ascii_image):
#     self.ascii_drawn.text((0, i * self.font_height), line, font=self.font, fill=(0, 0, 0))




