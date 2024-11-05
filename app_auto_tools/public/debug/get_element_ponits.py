import uiautomator2 as u2
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

import re

def rectangle_center(x1, y1, x2, y2):
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    return center_x, center_y

def add_text_to_image(draw, text, position, font_size=20, color=(255, 0, 0)):
    font = ImageFont.truetype("arial.ttf", font_size)
    draw.text(position, text, font=font, fill=color)

def draw_elements(elements, draw):
    for element in elements:

        visible = element.attrib['visible-to-user']
        
        outline_color = 'red' if visible == 'true' else 'blue'
        
        bounds = element.attrib['bounds']
        numbers = re.findall(r'\d+', bounds)
        if numbers:
            coords  = [int(num) for num in numbers]
            draw.rectangle(coords, outline=outline_color, width=2)

            add_text_to_image(draw=draw, text=str(rectangle_center(*coords)), position=rectangle_center(*coords))

        if len(element) > 0:
            draw_elements(element, draw)

# 连接设备
device = u2.connect()

# 获取当前页面的 XML 源代码
xml_source = device.dump_hierarchy()

# 解析 XML 源代码以获取所有元素的坐标
root = ET.fromstring(xml_source)

# 获取屏幕截图
screenshot = device.screenshot(format='pillow')

# 在截图上绘制元素边界框
draw = ImageDraw.Draw(screenshot)
draw_elements(root, draw)

# 保存带有标记的截图
screenshot.save('marked_screenshot.png')
