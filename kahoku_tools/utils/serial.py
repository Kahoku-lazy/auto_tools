""" 
@ author: Kahoku
@ date: 2024/08
@ description: logging 日志文件生成器
@ version: 1.0
"""
import serial

class SerialWindows:

    def __init__(self, port, baudrate: int):

        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate

    def get_serial_info(self):

        serial_info = self.ser.get_settings()   
        return serial_info  

    def open_serial(self):
        if not self.ser.is_open:
            self.ser.open()

    def close_serial(self):
        if self.ser.is_open:
            self.ser.close()

    def _read_serial_data(self, size):
        data = self.ser.read(size)
        try:
            data = data.decode("utf8")      # DEBUG： 转编码会出错
        except UnicodeDecodeError:
            data = str(data)
        return data
    
    def write_serial_data(self, data):
        self.ser.write(data)     # data.encode("utf8")

    def get_buffer_data(self):
        return self._read_serial_data(self.ser.in_waiting)

    def set_buffer_size(self, rx_size = 1024 * 1024, tx_size = 128):
        self.ser.set_buffer_size(rx_size = rx_size, tx_size = tx_size)     

    def reset_buffer(self):
        self.ser.reset_input_buffer() 

    def read_line_data(self):
        """ 读取一行数据 """
        try:
            return self.ser.readline().decode('utf-8')
        except UnicodeDecodeError:
            return str(self.ser.readline())

    def write_line_data(self, data):
        """ 写入一行数据 """
        self.write_serial_data(data)