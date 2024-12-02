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

# 串口
def get_device_serial_logs(port, baudrate):
    """ 获取设备日志 """
    serial_modules = SerialModules()
    serial_modules.set_port_config(port, baudrate)
    serial_modules.main()

# APP 用例执行
def main(count: int):
    Runner().run(count)

if __name__ == "__main__":

    test_case = Process(target=main, args=(100000,))

    port, baud_rate = "COM11", 921600
    ser = Process(target=get_device_serial_logs, args=(port, baud_rate,))

    # -------------------------------------- 启动进程  --------------------------------------
    ser.start()
    test_case.start()
    

    # test_case.join()
    # ser.join()
    try:
        test_case.join()
        ser.join()
    except KeyboardInterrupt:
        print("进程被手动终止")
    except Exception as e:
        print(f"进程终止时发生异常: {e}")
    finally:
        # 此处可以添加清理代码，例如关闭设备连接等
        print("进行清理操作...")

