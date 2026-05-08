import random
import string
import io
import base64
from PIL import Image, ImageDraw, ImageFont
from flask import session

class Captcha:
    def __init__(self, width=120, height=40, font_size=28):
        self.width = width
        self.height = height
        self.font_size = font_size
        self.code = self._generate_code(4)

    def _generate_code(self, length=4):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    def _get_font(self):
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
            '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf',
            '/home/qianqianjie/procurement/app/static/fonts/LiberationSans-Bold.ttf',
        ]
        for path in font_paths:
            try:
                return ImageFont.truetype(path, self.font_size)
            except:
                continue
        return ImageFont.load_default()

    def _create_image(self):
        image = Image.new('RGB', (self.width, self.height), color='#f0f0f0')
        draw = ImageDraw.Draw(image)

        font = self._get_font()

        x_start = 15
        y_start = (self.height - self.font_size) // 2 - 2

        for i, char in enumerate(self.code):
            x = x_start + i * (self.width - 30) // len(self.code)
            y = y_start + random.randint(-3, 3)

            shadow_color = '#cccccc'
            draw.text((x + 1, y + 1), char, font=font, fill=shadow_color)

            text_color = '#2c3e50'
            draw.text((x, y), char, font=font, fill=text_color)

        for _ in range(3):
            line_color = '#d0d0d0'
            x1 = random.randint(0, self.width // 3)
            y1 = random.randint(0, self.height)
            x2 = random.randint(self.width * 2 // 3, self.width)
            y2 = random.randint(0, self.height)
            draw.line([(x1, y1), (x2, y2)], fill=line_color, width=1)

        for _ in range(20):
            dot_color = '#c0c0c0'
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            draw.point((x, y), fill=dot_color)

        return image

    def get_image(self):
        image = self._create_image()
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer.getvalue()

    def get_base64(self):
        image = self._create_image()
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f'data:image/png;base64,{img_base64}'


def generate_captcha():
    captcha = Captcha()
    session['captcha_code'] = captcha.code
    return captcha.get_base64(), captcha.code


def validate_captcha(user_input):
    stored_code = session.get('captcha_code', '')
    if stored_code and stored_code.lower() == user_input.lower():
        session.pop('captcha_code', None)
        return True
    return False