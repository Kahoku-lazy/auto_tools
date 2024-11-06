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
from datetime import datetime
import time

from utils.serial import SerialWindows
from utils.logs import LogDriver
from public.utils import Utils


# ------------------------------ 记录设备日志 ------------------------------
def receive_serial_data(queue, prot, baud_rate, save_log_path):
    """ 串口接收模块: 循环读取串口数据并放入队列中 """
    ser = SerialWindows(prot, baud_rate)
    ser.open_serial()

    ser_log = LogDriver(save_log_path)
    while True:
        data = ser.read_line()
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
            relay_ser.wirte_serial_data(bytes.fromhex(i))
        
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
            print(f">>> [OTA Success] {results}")
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
    
    # ------------------------------多进程业务逻辑 串口数据接收与处理 ------------------------------
    # 串口接收进程
    prot, baud_rate = "COM12", 115200
    save_log = r"D:\Kahoku\H7148_OTA\results\h7148_serial.log"
    receiver = Process(target=receive_serial_data, args=(data_queue, prot, baud_rate,save_log,))

    # 继电器发送进程
    common = ['A0 01 01 A2', 'A0 01 00 A1']
    prot, baud_rate = "COM11", 9600
    relay = Process(target=send_relay_serial_common, args=(common, prot, baud_rate,))


    # OTA数据处理进程
    find_regex = r'MQTT OTA Process : (\d+) / (\d+)'
    is_regex_exist = r'checkDone\s*success'
    csv_title = ["ota_percent", "ota_maxsize", "timer",  "OTA_start_time",  "OTA_end_time", "OTA_times", "ota_status"]
    save_csv_path = r"D:\Kahoku\H7148_OTA\results\h7148_ota_result.csv"
    ota_log= Process(target=ota_log_filter, args=(data_queue,find_regex, is_regex_exist, csv_title, save_csv_path,))


    is_regex_exist = r'insert trigger sensor data is OK'
    csv_title = ["receive_time", "receive_status"]
    save_csv_path = r"D:\Kahoku\H7148_OTA\results\h7148_sensor_result.csv"
    sensor_log = Process(target=sensor_log_filter, args=(data_queue,is_regex_exist, csv_title, save_csv_path,))


    # ------------------------------ 多进程运行 ------------------------------
    receiver.start()
    relay.start()

    ota_log.start()
    sensor_log.start()



    receiver.join()
    relay.join()

    ota_log.join()
    sensor_log.join()
