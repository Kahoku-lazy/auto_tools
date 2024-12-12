""" 
@ author: Kahoku
@ date: 2024/08
@ description: UI 操作方法
@update: 2024/11
@ version: 2.1
    1. airtest 测试框架 更换为 图像识别算法
    2. 默认使用的 Uiautomator2 框架方法，针对Android 端测试
    3. 识别算法优化，针对不同分辨率手机

"""
import cv2
from time import sleep

from utils.ui_detection_system import UIDetectionSystem

class Action:
    def __init__(self, driver, ocr_language='ch') -> None:

        self._ocr_language = ocr_language
        self._ui = UIDetectionSystem(self._ocr_language)  # 识别工具

        self._driver = driver       # 驱动

    @staticmethod
    def wait_seconds(seconds):
        sleep(seconds)

    @staticmethod
    def rectangle_center(points: list):

        """ 计算由两个对角点定义的矩形的中心点坐标 """
        x1, y1, x2, y2 = [int(coordinate) for point in points for coordinate in point]
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        return (center_x, center_y)

    def sorting_value(self, value, mode):
        if mode == "text":
            return value
        elif mode == "image":
            return cv2.imread(value)

    def get_detection_result(self, value,  mode):
        """ 获取元素中心点的坐标位置 """
        value = self.sorting_value(value, mode)

        method = getattr(self._ui, f"find_{mode}_coordinates", lambda x, y: "None")
        points = method(self.get_screenshot(), value)
        try:
            midpoint = self.rectangle_center(points)
        except:
            midpoint = None
        finally:
            return midpoint


    """ --------------------------------------------------function:  元素方法 （不同系统【PC/IOS/Android】可能需要重构）------------------------------------------------------------"""
    def get_screenshot(self, save_img=False):
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
        self.wait_seconds(0.5)
        self._driver.send_keys(text)
    
    def keyevent_back(self):
        self._driver.press("BACK")

    def _get_window_midpoint(self):
        """ 获取设备屏幕中间位置的坐标 """
        width, height = self._driver.window_size()
        center_x = width / 2
        center_y = height / 2
        return center_x, center_y

    """ -------------------------------------------------- function:  元素操作 ------------------------------------------------------------"""

    def click_action(self,  element=None, element_type=None):
        """ 目标元素点击 """
        midpoint = self.get_detection_result(element, element_type)
        if midpoint:
            self.click_point(midpoint)
        else:
            return False
        
    def click_relative_location_action(self,  element=None, element_type=None, x_axial:int = 0, y_axial:int = 0):
        """ 以元素为参考点位，点击相对位置"""
        midpoint = self.get_detection_result(element, element_type)
        if midpoint:
            x, y = midpoint
            self.click_points((x + x_axial, y + y_axial))

    def swipe_action(self, element=None, element_type=None, direction: str = "up", pixel: float = 100.0):
        """ 滑动元素 """
        if element and element_type:
            midpoint = self.get_detection_result(element, element_type)
            if midpoint:
                x, y = midpoint
        else:
            x , y = self._get_window_midpoint()

        
        if direction == "up":
            self.swipe_point(x, y, x, y - pixel)
        elif direction == "down":
            self.swipe_point(x, y, x, y + pixel)

    def sliding_search_element_action(self, element, element_type, pixel=0.3, direction: str = "up"):
        """ 滑动搜索元素，向上或向下滑动，直到找到该元素出现 """
        
        for i in range(7):
            if self.get_detection_result(element, element_type):
                break
            self.swipe_action(direction, pixel)
            self.wait_seconds(0.5)
