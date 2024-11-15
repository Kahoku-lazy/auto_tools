"""  Laziness is my only productivity.
@ author: Kahoku
@ date: 2024/08
@ description: 多进程模块
    1. 串口接收模块
    2. 继电器控制模块
    3. 数据筛选器

@ version: 1.0
"""

from multiprocessing import Process, Queue
import time

import sys
sys.path.append("kahoku_tools")

from utils.serial_modules import SerialWindows
from utils.log_modules import LogDriver
from utils.method import Utils


# ------------------------------ 记录设备日志 ------------------------------
def receive_serial_data(queue, prot, baud_rate, save_log):
    """ 串口接收模块: 循环读取串口数据并放入队列中 """
    ser = SerialWindows(prot, baud_rate)
    ser.open_serial()

    ser_log = LogDriver(save_log)
    while True:
        data = ser.read_line_data()
        queue.put(data)
        ser_log.info(data)

# ------------------------------ 继电器控制： 发送sensor ------------------------------
def send_relay_serial_common(common: list, prot, baud_rate):
    """ 继电器指令发送模块: 循环每10秒发送一轮指令 """
    relay_ser = SerialWindows(prot, baud_rate)
    relay_ser.open_serial()

    while True:
        for i in common:
            time.sleep(0.5)
            relay_ser.write_serial_data(bytes.fromhex(i))
        
        time.sleep(10)

# ------------------------------ 数据筛选器 ------------------------------
def ota_log_filter(queue, find_regex, is_regex_exist, csv_title, save_csv_path):

    utils = Utils()
    utils.write_csv_values(save_csv_path, csv_title)

    global ota_start_time

    ota_start_time = None
    while True:
        if queue.empty():  
            continue

        data = queue.get()
        if utils.is_value_exist(data, is_regex_exist):
            status = "success"
        else:
            status = None

        results = utils.find_value(data, find_regex)
        if results:
            values =  [None for _ in range(len(csv_title))]

            values[0] = results.group(1)
            values[1] = results.group(2)
            values[2] = utils.get_current_time()
            values[6] = status

            if int(values[0]) == 1:
                ota_start_time = utils.get_current_time()
                values[3] = ota_start_time

            elif int(values[0]) == int(values[1]) or status == "success":
                values[4] =  utils.get_current_time()
                if ota_start_time is not None:
                    values[3] = ota_start_time
                    values[5] = utils.time_difference_in_minutes(ota_start_time, values[4])
            utils.write_csv_values(save_csv_path, values)
        elif status == "success":
            values =  [None for _ in range(len(csv_title))]
            values[6] = status
            utils.write_csv_values(save_csv_path, values)

def sensor_log_filter(queue, is_regex_exist, csv_title, save_csv_path):

    utils = Utils()
    utils.write_csv_values(save_csv_path, csv_title)

    global ota_start_time

    ota_start_time = None
    while True:
        values =  [None for _ in range(len(csv_title))]
        if not queue.empty():
            data = queue.get()

            if utils.is_value_exist(data, is_regex_exist):
                values[0] = utils.get_current_time()
                values[1] = "success"

                utils.write_csv_values(save_csv_path, values)


if __name__ == '__main__':

    data_queue = Queue()

    # ------------------------------ 参数 ------------------------------
    config = Utils().read_yaml_dict(r"D:\Kahoku\auto_tools\kahoku_tools\config\test_device_ota_function.yaml")
    
    # ------------------------------多进程业务逻辑 串口数据接收与处理 ------------------------------
    # 串口接收进程
    receiver = Process(target=receive_serial_data,
                        args=(data_queue, 
                                config["device_info"]["prot"],  # 串口号
                                config["device_info"]["baud_rate"],  # 波特率
                                config["device_info"]["save_log"],     # 日志保存路径
                                )
                                )

    # 继电器发送进程
    relay = Process(target=send_relay_serial_common, 
                    args=(config["relay_info"]["common"],       # 继电器指令列表
                            config["relay_info"]["prot"],   # 继电器串口号
                            config["relay_info"]["baud_rate"], # 继电器波特率
                            ))


    # OTA数据处理进程
    # ind_regex, is_regex_exist, csv_title, save_csv_path
    ota_log= Process(target=ota_log_filter, 
                    args=(data_queue, 
                            config["ota_log_info"]["find_regex"],       # OTA 进度
                            config["ota_log_info"]["is_regex_exist"],   # OTA 成功标志
                            config["ota_log_info"]["csv_title"],         # OTA 表格标题
                            config["ota_log_info"]["save_csv_path"],       # OTA 表格保存路径
                            )
                        )



    # ------------------------------ 多进程运行 ------------------------------
    receiver.start()
    relay.start()
    ota_log.start()



    receiver.join()
    relay.join()
    ota_log.join()

