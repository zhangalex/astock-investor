from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import sys

class CaptchaGenerate(object):
    def __init__(self, size=(100, 38), font_size=20, font_path = 'simsun.ttf'):
        self.size = size
        self.image = Image.new('RGBA', self.size, (255,) * 4)
        self.texts = self.rnd_code()
        self.font = ImageFont.truetype(font_path, font_size)
        

    @staticmethod
    def rnd_code(bits=4):
        code_list = []
        code_list.extend([i for i in range(49, 57)])  # numbers, 0 除外，以免和O混淆
        code_list.extend([i for i in range(65, 90)])  # A-Z
        code_list.extend([i for i in range(97, 123)])  # a-z
        code = ""
        for i in range(bits):
            code += chr(random.choice(code_list))
        return code

    def rnd_color(self, a=64, b=255):
        self.font_color = (random.randint(a, b), random.randint(a, b), random.randint(a, b))

    def rotate(self):
        rot = self.image.rotate(random.randint(-6, 6), expand=0)
        fff = Image.new('RGBA', rot.size, (255,) * 4)
        self.image = Image.composite(rot, fff, rot)
        # If a mask is given, this method updates only the regions indicated by the mask.

    def draw_single(self, text, x):
        draw = ImageDraw.Draw(self.image)
        draw.text((x, 2), text, fill=self.font_color, font=self.font)

    def create_points(self): 
        '''''绘制干扰点''' 
        draw = ImageDraw.Draw(self.image)
        point_chance = 1
        width, height = self.size 
        chance = min(50, max(0, int(point_chance))) # 大小限制在[0, 50] 
 
        for w in range(width): 
          for h in range(height): 
            tmp = random.randint(0, 50) 
            if tmp > 50 - chance: 
              draw.point((w, h), fill=(0, 0, 0)) 

    def draw_code(self, x=2, xp=25):
        for text in self.texts:
            self.rnd_color()
            self.draw_single(text, x)
            self.rotate()
            x += xp
        self.create_points()

        return self.texts, self.image

    def save(self, name="v_code.jpg"):
        self.image.save(name)