''' @author: Kahoku 
    @date: 2024/10/28
'''
import logging
import serial
import re
import uiautomator2 as u2
import time

class SwitchGameModel:

    def __init__(self):
        self.d = u2.connect()

    def swipe_find(self, text):
        width, height = self.d.window_size()
        start_x = width * 0.5
        start_y = int(height * 0.5)
        end_x = start_x
        end_y = int(height * 0.3)

        element_text =  self.d(text=text)
        for i in range(10):
            time.sleep(0.5)
            if element_text.exists:
                return element_text
            self.d.swipe(start_x, start_y, end_x, end_y)
        
        return None
    
    def click_text(self, text):
        text_element = self.d.xpath(f"//*[contains(@text, '{text}')]")
        if text_element.exists:
            text_element.click()

    def switch_model(self, button_name, model_name):

        self.click_text(button_name)
        text_element = self.swipe_find(model_name)
        if text_element:
            text_element.click()
        time.sleep(0.5)
        self.d(text='确认').click()

class GetLog:

    def __init__(self,log_path, logger_name="root"):

        self.logger = logging.Logger(logger_name)
        self.logger.setLevel(logging.INFO)
        self.fmts = "%(asctime)s-:%(levelname)s: -- %(message)s"   # log输出格式
        self.dmt = "%Y/%m/%d %H:%M:%S"      # log时间格式   
        self.log_path = log_path

    def logger_init(self):
        """ 配置 logger """
        self.handler = logging.FileHandler(self.log_path, 'a+')
        formatter = logging.Formatter(self.fmts, self.dmt)
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)

    def info(self, message):
        """ 记录 log 信息 """
        self.logger_init()
        self.logger.info(message)
        self.logger.removeHandler(self.handler)

    def error(self, message):
        """ 记录 error 信息 """
        self.logger_init()
        self.logger.error(message)
        self.logger.removeHandler(self.handler)

class SerialWindows:

    def __init__(self, port, baudrate: int):
        """ 构造方法
            串口参数设置
        """
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate

    def get_serial_info(self):
        """ 获取串口信息 """
        serial_info = self.ser.get_settings()   
        return serial_info  

    def open_serial(self):
        """ 打开串口 """
        if not self.ser.is_open:
            self.ser.open()

    def close_serial(self):
        """ 关闭串口 """
        if self.ser.is_open:
            self.ser.close()

    def read_serila_data(self, size):
        """ 读取串口数据 """
        # data = self.ser.readline()
        data = self.ser.read(size)
        try:
            data = data.decode("utf8")      # DEBUG： 转编码会出错
        except UnicodeDecodeError:
            data = str(data)
        return data
    
    def wirte_serial_data(self, data):
        """ 写串口数据 """
        data = data + r"\r\n"
        self.ser.write(data)     # data.encode("utf8")
        
    def get_buffer_data(self):
        """ 读取串口缓冲区的数据 """
        return self.read_serila_data(self.ser.in_waiting)

    def set_buffer_size(self, rx_size = 1024 * 1024, tx_size = 128):
        """ 设置缓冲区大小"""
        self.ser.set_buffer_size(rx_size = rx_size, tx_size = tx_size)      

    def reset_buffer(self):
        """ 清除缓冲区 """
        self.ser.reset_input_buffer() 

def find_value(text, pattern = r'Detect class:\s*(\d+)'):
    """
    从给定文本中提取 "Detect class: <数字>" 中的数字。

    :param text: 包含 "Detect class: <数字>" 的字符串
    :return: 提取的数字，如果没有找到，则返回 None
    """
    # 定义正则表达式模式
    # pattern = r'Detect class:\s*(\d+)'

    match = re.search(pattern, text)
    
    if match:
        return match.group(1)
    else:
        return None

def find_all_values(text, pattern = r'Detect class:\s*(\d+)'):
    """
    查找字符串中所有包含 'Detect class: 0' 的部分，并提取其中的 '0'。

    :param text: 输入的字符串
    :return: 包含所有 '0' 的列表
    """
    # >> send >> d0 00 26 46 46 4f ff ff f5 40 00 70
    # pattern = r'Detect class:\s*(0)'  # 匹配 'Detect class: 0' 并捕获 0
    matches = re.findall(pattern, text)
    return matches
    

import glob
import os

def get_images_from_directory(directory, extensions=["jpg", "jpeg", "png", "gif"]):
    """
    获取指定目录中的所有图片文件。

    :param directory: 要查找图片的目录路径
    :param extensions: 图片文件的扩展名列表（默认包括 jpg、jpeg、png、gif）
    :return: 图片文件路径列表
    """
    image_files = []
    for ext in extensions:
        # 拼接匹配模式
        # pattern = os.path.join(directory, "**", f"*.{ext}")
        pattern = os.path.join(directory, f"*.{ext}")
        # 查找所有匹配的文件
        image_files.extend(glob.glob(pattern))
    
    return image_files

import configparser

def read_config(file_path):
    # 创建 ConfigParser 对象
    config = configparser.ConfigParser()

    # 读取配置文件
    config.read(file_path)

    return config