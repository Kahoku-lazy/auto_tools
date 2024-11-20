from multiprocessing import Process

from runner.runner import Runner
from utils.serial_modules import SerialModules

def screenshot():
    Runner().get_app_screenshot()

def get_device_serial_logs(port, baudrate):
    """ 获取设备日志 """
    serial_modules = SerialModules()
    serial_modules.set_port_config(port, baudrate)
    serial_modules.main()

def main(count: int):
    Runner().run(count)


if __name__ == "__main__":

    # bug info: ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。
    # C:\Users\10035\anaconda3\envs\python39\lib\site-packages\airtest\core\android\cap_methods\minicap.py

    test_case = Process(target=main, args=(1000000,))

    port, baudrate = "COM12", 921600
    ser = Process(target=get_device_serial_logs, args=(port, baudrate,))

    test_case.start()
    ser.start()

    test_case.join()
    ser.join()

