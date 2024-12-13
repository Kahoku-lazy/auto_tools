""" 
@ author: Kahoku
@ date: 2024/08
@ description:  windows UI模块 业务功能
@update: 2024/08
@ version: 1.0
"""

import pyautogui
import numpy as np
import cv2

from app.android_tools import AndroidUiAction
from utils.utils import read_yaml_as_dict, LogDriver

class WindowsUiAction:

    def __init__(self, config):

        self._config = config

        device = WindowsDeviceUiTools()  # Android UI 操作方法
        self._drive = device
        self._ocr_language = self._config.get("case", "ocr_language")

        self._action = AndroidUiAction(self._drive, ocr_language=self._ocr_language)
        

        self.action_list = self.get_section_name_values("action")    # 支持的动作列表: 点击/滑动/查找/等待
        self.location_method_list = self.get_section_name_values("location_method") # 支持的定位方式列表: 元素/文本/图片

        self.test_logs = LogDriver(self._config.get("Logs", "test_case_run"), "uiAction")  



class WindowsDeviceUiTools:

    def screenshot(self, format=None):
        # 截取屏幕并保存为文件
        screenshot_pil = pyautogui.screenshot()  # <class 'PIL.Image.Image'>
        screenshot_pil.save("screenshot.png")
        opencv_image = cv2.cvtColor(np.array(screenshot_pil), cv2.COLOR_RGB2BGR)
        return opencv_image
    
    def click(self, x, y):
        pyautogui.click(x, y)

    def send_keys(self, text):
        pyautogui.typewrite(text, interval=0.1)  # interval控制字符之间的间隔

    def press(self, key):
        pyautogui.press(key)
        # pyautogui.hotkey('ctrl', 'c')
    def window_size(self):
        width, height = pyautogui.size()

        return width, height
    
    def swipe(self, start_x, start_y, end_x, end_y, duration=0.5):

        # # 从当前位置拖动到 (200, 250)
        # pyautogui.dragTo(200, 250, duration=1)  # 拖动到指定坐标

        # # 相对当前位置拖动
        # pyautogui.dragRel(50, 50, duration=1)  # 相对当前位置拖动50像素
        # # 向上滚动500个单位
        # pyautogui.scroll(500)

        # # 向下滚动500个单位
        # pyautogui.scroll(-500)
        pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)

    def get_mouse_position():
        # # 获取当前鼠标位置\
        # 移动鼠标到 (100, 150) 坐标
        pyautogui.moveTo(100, 150, duration=1)  # duration参数控制移动时间
        x, y = pyautogui.position()
        return x, y
