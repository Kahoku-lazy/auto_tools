""" 
@ author: Kahoku
@ date: 2024/08
@ description:  多进程运行脚本
@update: 2024/11
@ version: 2.1
    1. 执行测试用例
    2. 获取设备日志
    3. 通过设备日志断言操作结果
"""
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

"""
    ## Airtest 框架的截图功能，在截图时会出现异常，具体原因是：
        # 1. bug info: ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。
        # 2. minicap.py
"""
if __name__ == "__main__":
    # screenshot()


    test_case = Process(target=main, args=(1,))

    port, baud_rate = "COM12", 921600
    ser = Process(target=get_device_serial_logs, args=(port, baud_rate,))


    # -------------------------------------- 启动进程  --------------------------------------
    test_case.start()
    ser.start()

    test_case.join()
    ser.join()

