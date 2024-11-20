""" 
@ author: Kahoku
@ date: 2024/08
@ description: 串口模块接收发送日志与 日志模块交互。
    1. serial_modules.py  log_modules.py
@ version: 1.0
"""
import time
import serial
import threading

from utils.log_modules import LogDriver

class SerialModules:
    def __init__(self):
        """ 初始化串口模块 """
        self.serial = serial.Serial()

        log_path = 'runner/logs/serial_log.log'
        self.seral_log = LogDriver(log_path, console_printing=False)

        self.keep_running = True
        
    def set_port_config(self, port, baudrate: int, timeout=1, rx_size = 1024 * 1024, tx_size = 128):
        """ 设置端口和波特率; 缓冲区大小默认是1M """
        self.serial.port = port
        self.serial.baudrate = baudrate
        self.serial.timeout = timeout

        # 缓冲区大小 默认 1M 空间
        # self.serial.set_buffer_size(rx_size = rx_size, tx_size = tx_size) 

        # 清空缓冲区
        # self.serial.reset_input_buffer() 

    def _open_serial(self):
        """ 打开串口 """
        if not self.serial.is_open:
            self.serial.open()

    def _close_serial(self):
        """ 关闭串口 """
        if self.serial.is_open:
            self.serial.close()

    def read_data(self):
        """持续从串口读取数据"""
        while self.keep_running:
            # data = self.serial.read(self.serial.in_waiting)
            data = self.serial.readline()
            self.process_data(data)
            time.sleep(0.01)  # 每10ms读取一次

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

    def process_data(self, data):
        """处理接收到的数据"""
        try:
            data = data.decode('utf-8')
        except Exception as e:
            data = str(data)  
        self.seral_log.info(data)
        self._filter_data(data)

    def _filter_data(self, data):
        
        if "switch on" in data:
            print(f">>>[assert]: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 设备打开； 收到 switch on 消息")
        
        if "switch off" in data:
            print(f">>>[assert]: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 设备关闭； 收到 switch off 消息")

    # def start(self):
    #     """启动读取线程"""
    #     threading.Thread(target=self.read_data, daemon=True).start()

    def stop(self):
        """停止读写操作"""
        self.keep_running = False
        self._close_serial()

    # def main(self, command: tuple, send_interval=1):
    #     self._open_serial()

    #     self.start()
    #     try:
    #         while True:
    #             # self.write_data(command, send_interval)
    #             pass
    #     except KeyboardInterrupt:
    #         print(">>>[end]: 程序强制终止")
    #         self.stop()
    #     finally:
    #         pass

    def main(self):

        self._open_serial()
        try:
            while True:
                self.read_data()
                pass
        except KeyboardInterrupt:
            print(">>>[end]: 程序强制终止")
            self.stop()
        finally:
            pass
        

if __name__ == "__main__":
    
    serial_modules = SerialModules()
    serial_modules.set_port_config(port = "COM3", baudrate = 115200)
    command = ("00 00", "hex")
    serial_modules.main(command)


