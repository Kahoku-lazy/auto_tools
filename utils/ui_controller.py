""" 
@ author: Kahoku
@ date: 2024/08
@ description: 
    -- uiatutomator2 模拟器操作
        抓取定位元素工具下载地址: URL: https://uiauto.dev/
        1. 安装: pip3 install -U uiautodev -i https://pypi.doubanio.com/simple
        2. 运行: uiauto.dev  or python3 -m uiautodev

    -- airtest 图片点击方法: https://github.com/AirtestProject/Airtest
        1. api 教程： https://airtest.readthedocs.io/en/latest/all_module/airtest.core.api.html

    -- OmniParser AI模型 UI识别工具: https://github.com/microsoft/OmniParser
        1. 模型库：https://huggingface.co/spaces/microsoft/OmniParser
@ version: 1.1
    1. WEditor 工具替换为 uiauto
    2. 新增获取APP日志功能


@ 功能：
    1. PP-OCR: https://paddlepaddle.github.io/PaddleOCR/latest/ppocr/infer_deploy/python_infer.html#1
    2. Airtest 图片点击方法

"""
import os
import time
import uiautomator2 as u2

from airtest.core.api import *

def get_android_app_logs(device_serial, package_name='com.govee.home', output_file="govee_home_app.log"):
    logcat_command = f"adb -s {device_serial} logcat -v threadtime | findstr {package_name} > {output_file}"
    os.system(logcat_command)

class UiAutomationTools:

    def __init__(self):
        self.d = u2.connect()

    def _get_window_midpoint(self):
        width, height = self.d.window_size()
        center_x = width / 2
        center_y = height / 2
        return center_x, center_y
    
    def _relative_screen_position(self, x, y):
        screen_width, screen_height = self.d.window_size()
        rel_x = x / screen_width
        rel_y = y / screen_height
        return rel_x, rel_y
    
    @staticmethod
    def rectangle_center(x1, y1, x2, y2):
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        return center_x, center_y
        
    def _swipe_y(self, flag: str = "up", height: float = 0.3):
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
        
        self.d.swipe(start_x, start_y, end_x, end_y)

    def swipe_click_text_y(self, text, flag: str = "up", height=0.3):
        element_text= self.d.xpath(f"//*[contains(@text, '{text}')]")

        count = 0
        for i in range(10):
            if element_text.wait(timeout=0.5):
                return element_text
            self._swipe_y(flag, height)

        return None
    
    def click_text_xpath(self, text, timeout=0.5):
        text_element = self.d.xpath(f"//*[contains(@text, '{text}')]")
        # if text_element.exists:
        if text_element.wait(timeout=timeout):
            text_element.click()

    def click_text(self, text, timeout=0.5):
        text_element = self.d(text=text)
        if text_element.wait(timeout=timeout):
            text_element.click()

    def click_points(self, coordinates: tuple):
        x, y = coordinates
        self.d.click(x,y)

    def click_rectangle(self, rect: list):
        x1, y1, x2, y2 = rect
        center_x, center_y = self.rectangle_center(x1, y1, x2, y2)
        self.d.click(center_x, center_y)

    def click_xpath(self, element_xpath, timeout=0.5):

        element_xpath = self.d.xpath(element_xpath)
        # bounds = element_xpath.bounds
        # text = element_xpath.text
        if element_xpath.wait(timeout=timeout):
            element_xpath.click()

    def get_element_text(self, element_xpath):
        element_xpath = self.d.xpath(element_xpath)
        if element_xpath.exists:
            return element_xpath.text
        return None

    def start_app(self, package_name):
        self.d.app_start(package_name)

    def element_wait_exist(self, element_xpath, timeout=0.5):
        element_xpath = self.d.xpath(element_xpath)
        return element_xpath.wait(timeout=timeout)

    def element_wait_gone(self, element_xpath, timeout=0.5):
        element_xpath = self.d.xpath(element_xpath)
        return element_xpath.wait_gone(timeout=timeout)
    
    def element_wait_exist(self, element_xpath, timeout=0.5):
        element_xpath = self.d.xpath(element_xpath)
        return element_xpath.wait(timeout=timeout)
    
    def close_app(self, package_name):
        self.d.app_stop(package_name)

    def wait_seconds(self, seconds):
        time.sleep(seconds)

    def input_text(self, element_xpath, text):
        element_xpath = self.d.xpath(element_xpath)
        if element_xpath:
            element_xpath.set_text(text)

class AirtestTools:

    import logging
    logger = logging.getLogger("airtest")
    logger.setLevel(logging.ERROR)

    
    def __init__(self):
        init_device("Android")
        pass

    def start_app(self, package_name):
        # init_device("Android")
        start_app(package_name)

    def close_app(self, package_name):
        stop_app(package_name)

    def click_icon(self, icon_path):
        if exists(Template(icon_path)):
            touch(Template(icon_path))

    def wait_seconds(self, seconds):
        sleep(seconds)

    def is_icon_exist(self, icon_path):
        return exists(Template(icon_path))

    def keyevent_back(self):
        keyevent("BACK")

    
    

