""" 
@ author: Kahoku
@ date: 2024/08
@ description: 串口模块接收发送日志与 日志模块交互。
@ version: 1.0
"""
import time
import serial
import threading
import queue

from utils.log_modules import LogDriver
from utils.method import find_value

class SerialModules:
    def __init__(self):
        """ 初始化串口模块 """
        self.serial = serial.Serial()

        log_path = 'runner/logs/serial_log.log'
        self.seral_log = LogDriver(log_path, console_printing=False)

        log_path = 'runner/logs/filter_log.log'
        self.filter_log = LogDriver(log_path, console_printing=True)

        self.keep_running = True
        
    def set_port_config(self, port, baudrate: int, timeout=1, rx_size = 1024 * 1024, tx_size = 128):
        """ 设置端口和波特率; 缓冲区大小默认是1M """
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
        while self.keep_running:
            data = self.serial.read(self.serial.in_waiting)
            if data:
                data_queue.put(data)
                self.seral_log.info(data)
            # time.sleep(0.01)  # 每10ms读取一次

    
    def process_data(self, data_queue):
        """处理接收到的数据"""

        while self.keep_running:
            if not data_queue.empty():
                line = data_queue.get()  # 从队列取出数据
                try:
                    data = line.decode('utf-8', errors='ignore').strip()
                except Exception as e:
                    data = str(data) 
                self._filter_data(data)

    def write_data(self, command: tuple, send_interval=1):
        """向串口发送数据"""

        if isinstance(command, tuple) and len(command) == 2:
            if command[1] == "hex":
                try:
                    data = bytes.fromhex(command[0])
                except ValueError as e:
                    data = command[0].encode()
                    print(f">>> [error]: {e}")
            else:
                data = command[0].encode()

            self.serial.write(data)
            time.sleep(send_interval)   # 发送间隔时间

        else:
            return ">>> [error]: 输入的命令格式不正确"

    
    def _filter_data(self, data):
        result = find_value(data, r"(switch.on|switch.off|color_configs_set_success)")
        if result:
            self.filter_log.info(f">>>[assert]: 串口返回 {result.group(1)} 消息")


    def stop(self):
        """停止读写操作"""
        self.keep_running = False
        self._close_serial()

    def main(self):

        data_queue = queue.Queue()

        self._open_serial()

        read_thread = threading.Thread(target=self.read_data, args=(data_queue,))
        read_thread.start()

        process_thread = threading.Thread(target=self.process_data,args=(data_queue,))
        process_thread.start()


