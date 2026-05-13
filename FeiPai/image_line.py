from PIL import Image, ImageDraw


class image_line():

    def __init__(self):
        self.image_path = "image/arkimage.jpeg"

    def get_image(self):
        image = Image.open(self.image_path)
        line_width = 2  # 线宽
        x = 15  # 横向起始点
        y = 45  # 纵向起始点
        z = 12  # 线长
        draw = ImageDraw.Draw(image)
        draw.line((x, y, x+z, y), fill=128, width=line_width)
        image.show()

    def output_image(self):
        pass




if __name__ == "__main__":
    iL = image_line()
    iL.get_image()
