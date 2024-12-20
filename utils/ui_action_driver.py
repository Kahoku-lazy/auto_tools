""" 
@ author: Kahoku
@ date: 2024/08
@ description: UI 操作方法
@update: 2024/12
@ version: 2.1
    1. airtest 测试框架 更换为 图像识别算法
    2. 默认使用的 Uiautomator2 框架方法，针对Android 端测试
    3. 识别算法优化，针对不同分辨率手机
    4. pyautogui: windows 模拟键盘、鼠标等操作
    5. uiatumator2: android 模拟键盘、鼠标等操作
    5. 优化代码结构，减少重复代码
    
"""
import cv2
from time import sleep
import numpy as np

import pyautogui
import uiautomator2 as u2

from utils.ui_detection_system import UIDetectionSystem

def rectangle_center(points: list):
    """ 计算由两个对角点定义的矩形的中心点坐标 """
    x1, y1, x2, y2 = [int(coordinate) for point in points for coordinate in point]
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    return (center_x, center_y)

class WindowsDriver:

    def get_screenshot(self, format=None):
        # 截取屏幕并保存为文件
        screenshot_pil = pyautogui.screenshot()  # <class 'PIL.Image.Image'>
        screenshot_pil.save("screenshot.png")
        opencv_image = cv2.cvtColor(np.array(screenshot_pil), cv2.COLOR_RGB2BGR)
        return opencv_image
    
    def click_point(self, x, y):
        pyautogui.click(x, y)

    def input_text(self, text):
        pyautogui.typewrite(text, interval=0.1)  # interval控制字符之间的间隔

    def keyboard(self, key_event):
        pyautogui.press(key)
        # pyautogui.hotkey('ctrl', 'c')
    
    def get_window_midpoint(self):
        width, height = pyautogui.size()
        center_x = width / 2
        center_y = height / 2
        return center_x, center_y
    
    def swipe_point(self, start_x, start_y, end_x, end_y, duration=0.5):

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

class AndroidDriver:

    def __init__(self):
        
        self._driver = u2.connect()
    
    def get_window_midpoint(self):
        """ 获取设备屏幕中间位置的坐标 """
        width, height = self._driver.window_size()
        center_x = width / 2
        center_y = height / 2
        return center_x, center_y
    
    def get_screenshot(self):
        """ 获取手机当前屏幕截图并将其转化为numpy数组 """
        image = self._driver.screenshot(format='opencv')
        return image
    
    def click_point(self, coordinates: tuple):
        """ 坐标点击 """
        x, y = coordinates
        self._driver.click(x,y)

    def swipe_point(self, start_x, start_y, end_x, end_y):
        """ 坐标滑动 """
        self._driver.swipe(start_x, start_y, end_x, end_y)

    def input_text(self, text):
        """ 输入文本 """
        self.wait_seconds(0.5)
        self._driver.send_keys(text)
    
    def keyboard(self, key_event):
        """ 返回键 """
        self._driver.press("BACK")

class UiActionDriver:
    def __init__(self, driver, ocr_language='ch') -> None:

        self._ui = UIDetectionSystem(ocr_language)  # UI识别工具

        self._driver = driver

    def _get_target_value(self, value, value_type):
        if value_type == "text":
            v = value
            return value
        elif value_type == "image":
            v = cv2.imread(value)

        return v

    def get_detection_result(self, value, value_type):
        """ 获取元素中心点的坐标位置 """
        value = self._get_target_value(value, value_type)

        method = getattr(self._ui, f"find_{value_type}_coordinates", lambda x, y: "None")
        points = method(self._driver.get_screenshot(), value)
        try:
            midpoint = self.rectangle_center(points)
        except:
            midpoint = None
        finally:
            return midpoint

    def click_action(self,  element=None, element_type=None):
        """ 目标元素点击 """
        midpoint = self.get_detection_result(element, element_type)
        if midpoint:
            self._driver.click_point(midpoint)
        else:
            return False
        
    def click_relative_location_action(self,  element=None, element_type=None, x_axial:int = 0, y_axial:int = 0):
        """ 以元素为参考点位，点击相对位置"""
        midpoint = self.get_detection_result(element, element_type)
        if midpoint:
            x, y = midpoint
            self._driver.click_points((x + x_axial, y + y_axial))

    def swipe_action(self, element=None, element_type=None, direction: str = "up", pixel: float = 100.0):
        """ 滑动元素 """
        if element and element_type:
            midpoint = self.get_detection_result(element, element_type)
            if midpoint:
                x, y = midpoint
        else:
            x , y = self._get_window_midpoint()

        if direction == "up":
            self._driver.swipe_point(x, y, x, y - pixel)
        elif direction == "down":
            self._driver.swipe_point(x, y, x, y + pixel)

    def sliding_search_element_action(self, element, element_type, pixel=0.3, direction: str = "up"):
        """ 滑动搜索元素，向上或向下滑动，直到找到该元素出现 """
        for i in range(7):
            if self.get_detection_result(element, element_type):
                break
            self.swipe_action(direction, pixel)
            wait_seconds(0.5)

    def assert_text_action(self, text):
        if self._ui.find_text_coordinates(self._driver.get_screenshot(), text):
            print("断言 PASS")
            return True
        else:
            print("断言 FAIL")
            return False
        
    def wait_seconds(self, seconds):
        sleep(seconds)