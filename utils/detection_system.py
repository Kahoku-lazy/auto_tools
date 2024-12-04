""" 
@ author: Kahoku
@ date: 2024/08
@ description:  Android 设备UI自动化工具集合
@update: 2024/11
@ version: 2.1
    1. airtest 测试框架 更换为 图像识别算法

"""
import cv2
import difflib
import logging
from time import sleep

# APP 控制模块
import uiautomator2 as u2

#  图片识别算法选用
from paddleocr import PaddleOCR
from utils.template_matching import match_template

class UIDetectionSystem:

    # 关闭 PPocr debug； 将日志输出等级设置为 ERROR 
    logger_ppocr = logging.getLogger("ppocr")
    logger_ppocr.setLevel(logging.ERROR)

    def __init__(self, ocr_language='ru'):
        """
            args:
                |--- ocr_language: str
                    |--- # language: 语言类型，默认为'ru' （俄语）
                    |--- # 可选( 其它 可去查询 PaddleOCR 支持的语言):'ch'(中文)、'en'(英语)、'ru'(俄语)    
        """
        self.ocr_language = ocr_language
        self._ocr = PaddleOCR(use_angle_cls=True, lang=self.ocr_language)  
    
    """``````````````````````````````````````````` 图像icon识别方法 ````````````````````````````````````````````````"""

    def find_image_coordinates(self, target, template):
        """ 通过模板匹配的方式寻找目标图像在原始图像中的位置 """
        match_results = match_template(target, template)
        if match_results:
            return list(match_results)
        else:
            return False
    

    """``````````````````````````````````````````` 图片文字识别方法 ````````````````````````````````````````````````"""
    @staticmethod
    def _compare_strings(str1, str2):
        """ 比较两个字符串相似度; 范围: -1 ~ 1"""
        seq_matcher = difflib.SequenceMatcher(None, str1, str2)
        return seq_matcher.ratio()
    
    def find_text_coordinates(self, image, text, threshold=0.8):
        """ 通过OCR识别图像中的文本,返回坐标信息
        """
        result = self._ocr.ocr(image, cls=True)
        for idx in result[0]:
            similarity = self._compare_strings(idx[1][0], text)
            if similarity >= threshold:
                points = [idx[0][0], idx[0][2]]  # 左上角和右下角坐标
                conf_info = idx[1]      # 置信度信息
                return points
        return False
    

class Action:

    def __init__(self, driver, ocr_language='ru') -> None:

        self._ui = UIDetectionSystem(ocr_language)

        self._driver = driver       # 驱动

    @staticmethod
    def rectangle_center(points: list):

        """ 计算由两个对角点定义的矩形的中心点坐标 """
        x1, y1, x2, y2 = [int(coordinate) for point in points for coordinate in point]
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        return (center_x, center_y)

    def get_detection_result(self, value,  mode):
        """ 获取检测结果 """
        if mode == "text":
            points = self._ui.find_text_coordinates(self.get_screenshot(), value)
        elif mode == "image":
            template_image = cv2.imread(value)
            points = self._ui.find_image_coordinates(self.get_screenshot(), template_image)

        try:
            midpoint = self.rectangle_center(points)
        except:
            midpoint = None
        finally:
            return midpoint

    def wait_seconds(self, seconds):
        sleep(seconds)

    def click_action(self, target, target_type):
        midpoint = self.get_detection_result(target, target_type)
        if midpoint:
            self._driver.click_point(midpoint)

    

    


class AndroidDeviceUiTools:
    def __init__(self, ocr_language='ru'):

        self._u2 = u2.connect()

        self._ui = UIDetectionSystem(ocr_language)

    #------------------------------------------------------ APP 启动与关闭 --------------------------------------------------------------
    def start_app(self, package_name):
        self._u2.app_start(package_name)

    def close_app(self, package_name):
        self._u2.app_stop(package_name)

    def wait_seconds(self, seconds):
        sleep(seconds)

    # ------------------------------------------------------ 元素控件 --------------------------------------------------------------------------------
    def _click_xpath(self, element_xpath, timeout=0.5):
        element_xpath = self._u2.xpath(element_xpath)
        if element_xpath.wait(timeout=timeout):
            element_xpath.click()

    def _click_fuzzy_text_xpath(self, text, timeout=0.5):
        text_element = self._u2.xpath(f"//*[contains(@text, '{text}')]")
        if text_element.wait(timeout=timeout):
            text_element.click()

    def click_points(self, coordinates: tuple):
        """ 点击坐标点 """
        x, y = coordinates
        self._u2.click(x,y)

    """ --------------------------------------------------function:   点击 --------------------------------------------------------------------------------"""
    def click_image(self, icon_path):
        template_image = cv2.imread(icon_path)
        points = self._ui.find_image_coordinates(self.get_screenshot(), template_image)
        if points:
            self.click_points(self.rectangle_center(points))
        else:
            return '>>>[Match Template] No matching icon found'

    def click_text(self, text):
        points = self._ui.find_text_coordinates(self.get_screenshot(), text)
        if points:
            self.click_points(self.rectangle_center(points))
        else:
            print('>>>[OCR] No matching text found')

    def click_relative_location(self, element_value, x_axial:int = 0, y_axial:int = 0, mode: str = "text"):
        """ 以文本为原点，点击相对位置"""

        if mode == "text":
            points = self._ui.find_text_coordinates(self.get_screenshot(), element_value)
        elif mode == "image":
            template_image = cv2.imread(element_value)
            points = self._ui.find_image_coordinates(self.get_screenshot(), template_image)
        else:
            return

        if points:
            x, y = self.rectangle_center(points)
            self.click_points((x + x_axial, y + y_axial))
        else:
            print('>>>[OCR] No matching text found')
    
    """ --------------------------------------------------function: 滑动与拖动 --------------------------------------------------------------------------------"""
    def _swipe_y(self, flag: str = "up", height: float = 0.4):
        """ 滑动屏幕, 以手机屏幕中心点坐标为起点, 向上下滑动"""
        start_x, start_y = self._get_window_midpoint()
        end_x = start_x
        height = height * start_y
        if flag.lower() == "down":
            end_y = start_y - height
            if end_y <= 0:
                end_y = 0
        
        elif flag.lower() == "up":
            end_y = start_y + height
            if end_y >= start_y * 2:
                end_y = start_y * 2
        
        self._u2.swipe(start_x, start_y, end_x, end_y)

    def sliding_search_element(self, element_value, pixel=0.3, direction: str = "up", mode: str = "text"):
        """ 滑动搜索元素，向上或向下滑动，直到找到该元素出现 """
        
        for i in range(7):
            if mode == "image":
                image = cv2.imread(element_value)
                result = self._ui.find_image_coordinates(self.get_screenshot(), image)
            elif mode == "text":
                result = self._ui.find_text_coordinates(self.get_screenshot(), element_value)

            if result:
                break
            self._swipe_y(direction, pixel)
            self.wait_seconds(0.5)

    """ --------------------------------------------------  function:  文本输入 --------------------------------------------------------------------------------"""
    def input_text(self, text):
        self.wait_seconds(0.5)
        self._u2.send_keys(text)
    
    """ --------------------------------------------------  function:  模拟按键操作  --------------------------------------------------------------------------------"""
    def keyevent_back(self):
        self._u2.press("BACK")

    """ --------------------------------------------------  function:  查找与等待  --------------------------------------------------------------------------------"""
    def element_wait_exist(self, element_xpath, timeout=0.5):
        """ 等待元素出现 """
        element_xpath = self._u2.xpath(element_xpath)
        return element_xpath.wait(timeout=timeout)
    
    def is_element_text_exist(self, element_text):
        """ 判断元素是否存在 """
        element_text = self._u2(text=element_text)
        return element_text.exists

    """ --------------------------------------------------  function:  获取 UI界面信息  --------------------------------------------------------------------------------"""
    def _get_window_midpoint(self):
        """ 获取设备屏幕中间位置的坐标 """
        width, height = self._u2.window_size()
        center_x = width / 2
        center_y = height / 2
        return center_x, center_y
    
    def _relative_screen_position(self, x, y):
        """ 将绝对坐标转换为相对坐标 """
        screen_width, screen_height = self._u2.window_size()
        rel_x = x / screen_width
        rel_y = y / screen_height
        return rel_x, rel_y
    
    def get_screenshot(self, save_img=False):
        """ 获取手机当前屏幕截图并将其转化为numpy数组 """
        image = self._u2.screenshot(format='opencv')
        return image

    """ --------------------------------------------------  function:  坐标计算 --------------------------------------------------------------------------"""
    @staticmethod
    def rectangle_center(points: list):
        """ 计算由两个对角点定义的矩形的中心点坐标 """
        x1, y1, x2, y2 = [int(coordinate) for point in points for coordinate in point]
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        return (center_x, center_y)


if __name__ == "__main__":
    
    ui = AndroidDeviceUiTools()
