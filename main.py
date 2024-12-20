""" 
@ author: Kahoku
@ date: 2024/08
@ description:  多进程运行脚本
@update: 2024/12
@ version: 2.1
    |-- 1. 执行测试用例
    |-- 2. 获取设备日志
@问题:
    |-- 1. 进程关闭的同时 关闭进程中的线程
"""
from multiprocessing import Process
from runner.runner import run_case, get_device_serial_logs


if __name__ == "__main__":

    run_case()

    # test_case = Process(target=run_case)
    # ser = Process(target=get_device_serial_logs)

    # # -------------------------------------- 启动进程  --------------------------------------
    # # ser.start()
    # test_case.start()
    
    # try:
    #     test_case.join()
    #     # ser.join()
    # except KeyboardInterrupt:
    #     print("|>>> 测试结束 |")
    #     print(">>> 退出中...")

