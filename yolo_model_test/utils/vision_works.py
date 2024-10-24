''' @author: Kahoku 
    @date: 2024/10/07
'''
import cv2
import os
from mss import mss, tools
import pyautogui
from screeninfo import get_monitors

def is_single_letter(s):
    """ 判断是否为单个字符串 """
    return len(s) == 1 and s.isalpha()

def open_image_screen(image_path, delay_time=1000):
    """ 副屏中显示图片
    参数:
        image_path: 图片路径
        delay_time: 图片窗口持续时间
    """
    image = cv2.imread(image_path)

    height, width, channels = image.shape
    if image is None:
        exit()

    # 获取主屏幕的分辨率
    screen_width, screen_height = pyautogui.size()
    secondary_screen_x = screen_width
    secondary_screen_y = 0

    # # 创建窗口
    cv2.namedWindow('screen_windows', cv2.WINDOW_NORMAL)
    cv2.moveWindow('screen_windows', secondary_screen_x, secondary_screen_y)
    cv2.setWindowProperty('screen_windows', cv2.WND_PROP_FULLSCREEN ,cv2.WINDOW_FULLSCREEN)

    # 显示图片
    cv2.imshow('screen_windows', image)

    cv2.waitKey(delay_time)
    cv2.destroyAllWindows()
