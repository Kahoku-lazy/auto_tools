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
from runner.runner import Runner
from utils.utils import SerialModules, read_config

from multiprocessing import Process

CONFIG_PATH = "config.ini"
CONFIG = read_config(CONFIG_PATH)

# 串口
def get_device_serial_logs():
    serial_modules = SerialModules(CONFIG)
    serial_modules.main()

# APP 用例执行
def main():
    Runner(CONFIG).run()

if __name__ == "__main__":

    # 进程关闭的同时 关闭进程中的线程

    test_case = Process(target=main)
    ser = Process(target=get_device_serial_logs)

    # -------------------------------------- 启动进程  --------------------------------------
    # ser.start()
    test_case.start()
    
    try:
        test_case.join()
        # ser.join()
    except KeyboardInterrupt:
        print("进程被手动终止")

