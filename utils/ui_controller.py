""" 
@ author: Kahoku
@ date: 2024/08
@ description:  Android 设备UI自动化工具集合
@update: 2024/11
@ version: 2.1
    1. 新增获取APP日志功能
"""
import os
import cv2
import difflib
import psutil
import numpy as np
from time import sleep

# UI自动化工具选用
import uiautomator2 as u2
from airtest.core.api import *
from paddleocr import PaddleOCR, draw_ocr



#  图片识别算法选用
from utils.template_matching import TemplateMatcher, MultiScale, SIFTFeatureMatcher
# from template_matching import TemplateMatcher, MultiScale, SIFTFeatureMatcher

class AndroidDeviceUiTools:
    
    # ---------------------- 关闭 Airtest, PPOcr debug日志； 将日志输出等级设置为 ERROR ----------------------
    import logging
    logger_air = logging.getLogger("airtest")
    logger_air.setLevel(logging.ERROR)

    logger_ppocr = logging.getLogger("ppocr")
    logger_ppocr.setLevel(logging.ERROR)


    def __init__(self, ocr_language='ru'):
        self._u2 = u2.connect()

        # language: 语言类型，默认为'ru'(俄语)，可选( 其它 可去查询 PaddleOCR 支持的语言):'ch'(中文)、'en'(英语)、'ru'(俄语)
        self.ocr_language = ocr_language
        self._ocr = PaddleOCR(use_angle_cls=True, lang=self.ocr_language)  

    """ --------------------------------------------------  init:  初始化 android UI 自动化工具 --------------------------------------------------------------------------------"""
    def airtest_init(self):
        init_device("Android")

    def u2_init(self):
        self._u2 = u2.connect()

    """ --------------------------------------------------  function:  APP 启动与关闭 or 强制延时等待  --------------------------------------------------------------------------------"""
    def start_app(self, package_name):
        self._u2.app_start(package_name)

    def close_app(self, package_name):
        self._u2.app_stop(package_name)

    def wait_seconds(self, seconds):
        sleep(seconds)

    """ --------------------------------------------------  function:  UI 页面点击方法  --------------------------------------------------------------------------------"""

    # ------------------------------------------------------------- 元素控件 --------------------------------------------------------------------------------
    def click_xpath_u2(self, element_xpath, timeout=0.5):
        element_xpath = self._u2.xpath(element_xpath)
        # bounds = element_xpath.bounds
        # text = element_xpath.text
        if element_xpath.wait(timeout=timeout):
            element_xpath.click()

    def click_fuzzy_text_xpath(self, text, timeout=0.5):
        text_element = self._u2.xpath(f"//*[contains(@text, '{text}')]")
        # if text_element.exists:
        if text_element.wait(timeout=timeout):
            text_element.click()

    def click_text(self, text, timeout=0.5):
        text_element = self._u2(text=text)
        if text_element.wait(timeout=timeout):
            text_element.click()

    def click_points(self, coordinates: tuple):
        """ 点击坐标点 """
        x, y = coordinates
        self._u2.click(x,y)

    # ------------------------------------------------------------- 图像识别 --------------------------------------------------------------------------------
    def click_icon_air(self, icon_path):
        if exists(Template(icon_path)):
            touch(Template(icon_path))

    def is_icon_exist_air(self, icon_path):
        """ 判断图标是否存在; 找到目标返回坐标点, 未找到目标返回False """
        return exists(Template(icon_path))

    def click_image(self, icon_path):
        image = self.get_screenshot()
        template = cv2.imread(icon_path)
        results = TemplateMatcher().match(image, template)
        if results:
            x, y = self.rectangle_center(*results)
            self.click_points((x,y))
        else:
            raise Exception('No matching icon found')
        
    # ------------------------------------------------------------- OCR 识别--------------------------------------------------------------------------------
    def click_text_ocr(self, text, height_rate=1):
        """ 通过OCR识别图像中的文本, 然后点击匹配到的第一个结果。
        args:
        icon_path: 要点击的图标路径
        language: 语言类型，默认为'ru'(俄语)，可选( 其它 可去查询 PaddleOCR 支持的语言):'ch'(中文)、'en'(英语)、'ru'(俄语)
        """
        # self._ocr = PaddleOCR(use_angle_cls=True, lang=self.ocr_language)  

        def compare_strings(str1, str2):
            seq_matcher = difflib.SequenceMatcher(None, str1, str2)
            return seq_matcher.ratio()
        
        image = self.get_screenshot()
        height, width, channels = image.shape

        # 截取上半部分
        upper_height = int(height * height_rate)
        upper_part = image[:upper_height, :, :]
        result = self._ocr.ocr(upper_part, cls=True)
        for idx in result[0]:
            if compare_strings(idx[1][0], text) > 0.8:
                x1,y1= idx[0][0]; x2,y2 = idx[0][2]
                x, y = self.rectangle_center(x1,y1,x2,y2)
                self.click_points((x,y))

    def is_text_exits_ocr(self, text):
        """ 通过OCR识别图像中的文本, 匹配到结果返回True, 否则返回False"""  

        def compare_strings(str1, str2):
            seq_matcher = difflib.SequenceMatcher(None, str1, str2)
            return seq_matcher.ratio()
        image = self.get_screenshot()
        result = self._ocr.ocr(image, cls=True)
        for idx in result[0]:
            if compare_strings(idx[1][0], text) > 0.8:
                return True
        return False
    
    def click_text_relative_location_ocr(self, text, x_axial:int = 0, y_axial:int = 0):

        """ 通过OCR识别图像中的文本, 然后点击匹配到的第一个结果。
        args:
        icon_path: 要点击的图标路径
        language: 语言类型，默认为'ru'(俄语)，可选( 其它 可去查询 PaddleOCR 支持的语言):'ch'(中文)、'en'(英语)、'ru'(俄语)
        """
        # self._ocr = PaddleOCR(use_angle_cls=True, lang=self.ocr_language)  

        def compare_strings(str1, str2):
            seq_matcher = difflib.SequenceMatcher(None, str1, str2)
            return seq_matcher.ratio()
        
        image = self.get_screenshot()
        height, width, channels = image.shape

        # 截取上半部分
        upper_height = int(height * height_rate)
        upper_part = image[:upper_height, :, :]
        result = self._ocr.ocr(upper_part, cls=True)
        for idx in result[0]:
            if compare_strings(idx[1][0], text) > 0.8:
                x1,y1= idx[0][0]; x2,y2 = idx[0][2]
                x, y = self.rectangle_center(x1,y1,x2,y2)
                self.click_points((x + x_axial, y + y_axial))

    """ --------------------------------------------------  function:  Android 滑动与拖动操作方法 --------------------------------------------------------------------------------"""
    def _swipe_y(self, flag: str = "up", height: float = 0.3):
        """ 滑动屏幕，向上或向下滑动，高度由height决定 """
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

    def sliding_search_element_android(self, element, element_type=None, pixel=0.3, direction: str = "up"):
        """ 滑动搜索元素，向上或向下滑动，直到找到该元素出现 """
        midpoint_x, midpoint_y = self._get_window_midpoint()
        for i in range(20):
            if element_type == "icon":
                if exists(Template(element), threshold=0.9):
                    break
            elif element_type == "text":
                if self.is_text_exits_ocr(element):
                    break
            else:       #  默认使用 u2 判断元素是否存在
                self.is_element_text_exist(element)
            self._swipe_y(direction, 0.3)

    """ --------------------------------------------------  function:  Android 文本框（文本输入）与 弹窗操作方法 --------------------------------------------------------------------------------"""
    def input_text_u2(self, element_xpath, text):
        element_xpath = self._u2.xpath(element_xpath)
        if element_xpath.exists:
            element_xpath.set_text(text)
            return True
        return False
    
    def input_text_air(self, text_value):
        text(text_value)

    """ --------------------------------------------------  function:  Android 模拟按键操作  --------------------------------------------------------------------------------"""
    def keyevent_back_air(self):
        keyevent("BACK")

    def keyevent_back_u2(self):
        self._u2.press("BACK")

    """ --------------------------------------------------  function:  Android U2操作辅助方法: 异常处理  --------------------------------------------------------------------------------"""
    def element_wait_exist(self, element_xpath, timeout=0.5):
        """ 等待元素出现 """
        element_xpath = self._u2.xpath(element_xpath)
        return element_xpath.wait(timeout=timeout)

    def element_wait_gone(self, element_xpath, timeout=0.5):
        """ 等待元素消失 """
        element_xpath = self._u2.xpath(element_xpath)
        return element_xpath.wait_gone(timeout=timeout)
    
    def is_element_text_exist(self, element_text):
        """ 判断元素是否存在 """
        element_text = self._u2(text=element_text)
        return element_text.exists

    """ --------------------------------------------------  function:  Android U2操作辅助方法: 获取信息  --------------------------------------------------------------------------------"""
    def get_element_text(self, element_xpath):
        """ 获取元素的文本内容 """
        element_xpath = self._u2(element_xpath)
        if element_xpath.exists:
            return element_xpath.text
        return None
    
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

        # 使用ADB命令获取屏幕截图，并使用Pillow处理图像 (弃用方法)
        # import subprocess
        # from PIL import Image
        # import io
        # import numpy as np
        # result = subprocess.run(['adb', 'exec-out', 'screencap', '-p'], stdout=subprocess.PIPE)
        # image_bytes = result.stdout
        # image = Image.open(io.BytesIO(image_bytes))

        image = self._u2.screenshot()
        if save_img:
            image.save("screenshot.png") # 保存图像到文件  

        image_np = np.array(image)          # 将 PIL 图像转换为 NumPy 数组

        return image_np 
    
    def get_app_memory_usage_records(self, package_name):
        """" 获取APP 内存使用情况与CPU占用率
        return: 
            cpu_usage: CPU占用率
            mem_info: 内存使用情况
        """
        cpu_usage = psutil.cpu_percent(interval=1)

        # 获取应用内存使用情况
        response = self._u2.shell(f'dumpsys meminfo {package_name}')
        mem_info = response.output  # 使用 output 属性获取输出
        # total_pss = find_value(mem_info, r'TOTAL PSS:\s+(\d+)').group(1)
        return cpu_usage, mem_info

    @staticmethod
    def get_android_app_logs(device_serial, package_name, output_file):
        """ 获取adb logcat 日志
            Args:
                device_serial (str): 设备序列号
                package_name (str): 包名
                output_file (str): 输出文件路径
        """
        logcat_command = f"adb -s {device_serial} logcat -v threadtime | findstr {package_name} > {output_file}"
        os.system(logcat_command)


    """ --------------------------------------------------  function:  Android 操作辅助方法: 计算  --------------------------------------------------------------------------"""
    @staticmethod
    def rectangle_center(x1, y1, x2, y2):
        """ 计算由两个对角点定义的矩形的中心点坐标 """
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        return center_x, center_y
    
    @staticmethod
    def compare_strings(str1, str2):
        """ 比较两个字符串相似度 -1 ~ 1"""
        seq_matcher = difflib.SequenceMatcher(None, str1, str2)
        return seq_matcher.ratio()

if __name__ == "__main__":
    
    ui = AndroidDeviceUiTools()

    text_dict = {
                "green": "Элис, включи зеленый свет на занавесках.", 
                "red":"Алиса, включи красный свет на занавесках.",
                "H6079": "тест 6079"
            }
    
    # ui.input_text_u2('//*[@resource-id="com.yandex.iot:id/dialog_text_input"]',text_dict["H6079"])

    ui.click_image(r"config\yandex\yandex_icon\detail_page_on.png")