""" 
@author: Kahoku
@date: 2024/12
@description: 
    |-- 1. 基础方法, 包括文件操作, 字符串处理, 图片处理, 模型使用等
    |-- 2. 串口模块接收发送日志与 日志模块交互。
    |-- 3. logging 日志文件生成器
@version: 2.0
"""
import yaml, re, os, csv, glob
import configparser 
import pandas as pd

def read_yaml_as_dict(file_path):
    with open(file_path, mode='r', encoding="utf8") as f:
        yaml_values = yaml.load(f, Loader=yaml.FullLoader)

    return yaml_values

def read_csv_as_dict(file_path):
    data = pd.read_csv(file_path)

    return data.to_dict('records')

def read_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config

def get_section_name_values(config_path, section_name):
    """ 获取配置文件中section下的所有键值对 """
    config = read_config(config_path)
    action = config.items(section_name)
    converted_list = [item for tuple_item in action for item in tuple_item]
    return converted_list    

def write_csv_values(file_path, values, mode="a+"):
    with open(file_path, mode, newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(values)

def get_file_all(file_path, suffix):
    """ 获取指定目录下的所有文件路径 """
    files = []
    for ext in suffix:
        files.extend(glob.glob(os.path.join(file_path, f'**/**{ext}'),  recursive=True))
    return files


def find_value(text, pattern):
    """ 查找符合模式的第一个匹配项 """
    match = re.search(pattern, text)
    # match = re.findall(pattern, text)
    if match:
        return match
    else:
        return None

def time_difference_in_minutes(start_time, end_time):
    """ 计算两个时间差值并以分钟为单位返回 """
    time_difference = end_time - start_time
    
    time_difference_seconds = time_difference.total_seconds()
    time_difference_minutes = time_difference_seconds / 60
    
    return time_difference_minutes


import sys
import logging

class LogDriver:

    def __init__(self, file_path, logger_name="root", console_printing=True):
        
        self.logger = logging.Logger(logger_name)
        self.logger.setLevel(logging.INFO)

        self.fmts = "%(asctime)s.%(msecs)03d--[%(name)s] -> %(levelname)s |>>> %(message)s"   # log输出格式
        self.dmt = "%Y/%m/%d %H:%M:%S"      # log时间格式
        
        self.log_path = file_path

        self.console_printing = console_printing    # 是否输出到控制台

        self.logger_init()  # 初始化 logger

    def __getstate__(self):
        # 返回一个不包含logger的字典
        state = self.__dict__.copy()
        del state['logger']
        return state

    def __setstate__(self, state):
        # 重新创建logger并恢复其他状态
        self.__dict__ = state
        self.logger = logging.getLogger('MyLogger')

    def logger_init(self):
        """ 配置 logger """
        self.handler = logging.FileHandler(self.log_path, 'a+')
        self.rf_handler = logging.StreamHandler(sys.stderr)      #默认是sys.stderr
        formatter = logging.Formatter(self.fmts, self.dmt)

        # 保存至本地文件
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)

        # 控制台打印日志
        if self.console_printing:
            self.rf_handler.setFormatter(formatter)
            self.logger.addHandler(self.rf_handler)

    def info(self, message):

        self.logger.info(message)
        
    def error(self, message):

        self.logger.error(message)


import time
import serial
import threading
import queue

class SerialModules:
    def __init__(self, config):
        """ 初始化串口模块 """

        self.config = config

        self.serial = serial.Serial()

        log_path = config.get("Logs", "serial")
        self.seral_log = LogDriver(log_path, logger_name="serila", console_printing=False)

        log_path = config.get("Logs", "test_case_run")
        self.filter_log = LogDriver(log_path, logger_name="assert", console_printing=True)

        self.stop_event = threading.Event()
        
    def set_port_config(self, port, baudrate: int, timeout=1):
        """ 设置端口和波特率 """
        self.serial.port = port
        self.serial.baudrate = baudrate
        self.serial.timeout = timeout

    def _open_serial(self):
        """ 打开串口 """
        if not self.serial.is_open:
            self.serial.open()

    def _close_serial(self):
        """ 关闭串口 """
        if self.serial.is_open:
            self.serial.close()

    def read_data(self, data_queue):
        """持续从串口读取数据"""
        while not self.stop_event.is_set():
            try:
                data = self.serial.read(self.serial.in_waiting)
                if data:
                    data_queue.put(data)
                    self.seral_log.info(f"Read {len(data)} bytes from serial port")
                    self.seral_log.info(data)
            except Exception as e:
                self.seral_log.error(f"Error reading data from serial port: {e}")
            time.sleep(0.01)  # 每10ms读取一次

    def process_data(self, data_queue):
        """处理接收到的数据"""
        while not self.stop_event.is_set():
            try:
                if not data_queue.empty():
                    line = data_queue.get()  # 从队列取出数据
                    try:
                        data = line.decode('utf-8', errors='ignore').strip()
                    except Exception as e:
                        data = str(line)
                    self._filter_data(data)
            except Exception as e:
                self.seral_log.error(f"Error processing data: {e}")

    def _filter_data(self, data):
        result = find_value(data, r"(switch.on|switch.off|color_configs_set_success)")
        if result:
            self.filter_log.info(f">>>[assert]: 串口返回 {result.group(1)} 消息")

    def stop(self):
        """停止读写操作"""
        self.stop_event.set()
        self._close_serial()

    def main(self):

        self.set_port_config(self.config.get("Serial", "port"), self.config.getint("Serial", "baudrate"))
        data_queue = queue.Queue()

        self._open_serial()

        read_thread = threading.Thread(target=self.read_data, args=(data_queue,))
        process_thread = threading.Thread(target=self.process_data, args=(data_queue,))

        try:
            
            read_thread.start()
            process_thread.start()

            read_thread.join()
            process_thread.join()
    
        except KeyboardInterrupt:
            self.stop()
            print("线程程被手动终止")


