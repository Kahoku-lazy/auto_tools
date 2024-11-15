from paddleocr import PaddleOCR, draw_ocr

import subprocess
from PIL import Image
import io
import numpy as np

def get_screenshot():
    # 使用ADB命令获取屏幕截图，并使用Pillow处理图像
    result = subprocess.run(['adb', 'exec-out', 'screencap', '-p'], stdout=subprocess.PIPE)
    image_bytes = result.stdout
    image = Image.open(io.BytesIO(image_bytes))
    return image


def calculate_center(x1, y1, x2, y2):
    """
    计算由两个对角点定义的矩形的中心点坐标。

    参数:
    x1, y1 -- 第一个对角点的坐标。
    x2, y2 -- 第二个对角点的坐标。

    返回:
    (x, y) -- 中心点的坐标。
    """
    x_center = (x1 + x2) / 2
    y_center = (y1 + y2) / 2
    return (x_center, y_center)

# 例如ch, en, ru
ocr = PaddleOCR(use_angle_cls=True, lang="ru")  
img_path = r'D:\Kahoku\auto_tools\screenshot.png'
result = ocr.ocr(img_path, cls=True)
for idx in range(len(result)):
    res = result[idx]
    for line in res:
        print(line[0])
