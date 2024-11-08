"""  Laziness is my only productivity.
@ author: Kahoku
@ date: 2024/11
@ description: 通过串口发送指令与接收返回值, 来压测MCU功能
@ version: 1.0
"""
import sys
sys.path.append(r'D:\Kahoku\auto_tools\kahoku_tools')
from utils.serial import SerialWindows
from utils.logs import LogDriver
from utils.box import Utils

import random
import time
import re
import math

def add_end_check_bit(hex_string):
    """ 计算校验值字符串末尾 """
    numbers = [int(num, 16) for num in hex_string.split()]
    hex_result = hex(sum(numbers) % 256)[2:].upper().zfill(2)
    result = hex_string + " " + hex_result
    return result

def test_command_random_init(command_length: int):
    """ 初始化指令数据 """
    commands = []
    for _ in range(command_length):
        command = f"{random.randrange(0, 256, 1):02X}"
        commands.append(command)
    return " ".join(commands)

def increment_hex_string(start_hex):
    # 将输入的16进制字符串转换为整数列表
    hex_values = [int(x, 16) for x in start_hex.split()]
    hex_values[-1] += 1
    # 检查是否需要进位
    for i in reversed(range(len(hex_values))):
        if hex_values[i] > 255:
            hex_values[i] = 0
            if i > 0:
                hex_values[i-1] += 1
    # 将整数列表转换为16进制字符串，格式化为两位数
    hex_string = ' '.join(format(x, '02X') for x in hex_values)
    return hex_string

def test_command_sequential_init(command, command_length:int):
    """ 初始化指令数据 """
    commands = ' '.join(["00" for _ in range(command_length)])
    hex_string = increment_hex_string(command)
    return hex_string

def serial_command_sender(run_log, ser, command, keyword=None, interval=2):
    """ 发送指令功能
        ser: 串口对象
        commands: 指令列表  
        keyword: 检查指令是否生效的关键字
        interval: 指令间隔时间，单位秒
    """
    responses = []

    # 清空缓冲区
    ser.reset_buffer()

    # 添加校验位，发送指令
    command = add_end_check_bit(command)
    run_log.info(f">>>[Sending] Sending Command: {command}")
    ser.write_serial_data(bytes.fromhex(command))

    time.sleep(interval)  # 设置间隔
    # 读取串口返回值, 抓取关键字，判断是否发送成功
    response = ser.get_buffer_data_hex()
    run_log.info(f">>>[Receive] serial result hex: {response}")
    hex_string = ' '.join(f'{byte:02X}' for byte in response)
    if keyword and re.search(keyword, hex_string):
        flag = True
    elif keyword:
        flag = False
    else:
        flag = None
    
    run_log.info(f">>>[check] Receive Data: {hex_string}")
    run_log.info(f">>>[check] keyword: {keyword}")
    run_log.info(f">>>[check] check result: {flag}")
    # 记录输入与输出结果
    responses.append((command, flag, response, keyword))

    return responses


def run(port, baudrate: int, values, interval=1, command_mode='random', random_count=100, command_length=5, log_path="run_log.log"):
    """ 发送指令功能
        values: (commands, keywords);     commands: 指令列表  keyword: 检查指令是否生效的关键字
        mode: 'sequential': 递增, 'random': 随机, 'assign': 指定
        interval: 指令间隔时间，单位秒
    """
    # 日志记录器
    run_log = LogDriver(log_path)

    # 打开串口
    serial_port = SerialWindows(port, baudrate)
    serial_port.open_serial()
    # 设置缓冲区
    serial_port.set_buffer_size(rx_size=1024 * 1024, tx_size=128)

    # 准备数据
    if command_mode == 'random':
        for _ in range(random_count):
            serial_port.reset_buffer()
            command =  test_command_random_init(command_length)
            results = serial_command_sender(run_log, serial_port, command, keyword=None, interval=interval)
    
    elif command_mode == 'sequential':
        command = ' '.join(["00" for _ in range(command_length)])
        for _ in range(int(math.pow(255, command_length))):
            serial_port.reset_buffer()
            command = test_command_sequential_init(command, command_length)
            results = serial_command_sender(run_log, serial_port, command, keyword=None, interval=interval)
    
    elif command_mode == 'assign':
        commands = [command[0] for command in values]
        keywords = [keyword[1] for keyword in values]
    
        for i, command in enumerate(commands):
            # 清空缓冲区
            serial_port.reset_buffer()

            if keywords is not None:
                keyword = keywords[i]

            results = serial_command_sender(run_log, serial_port, command, keyword, interval)

    serial_port.close_serial()

    
# 示例用法
if __name__ == "__main__":

    args = Utils().read_yaml_dict(r"D:\Kahoku\auto_tools\kahoku_tools\config\test_mcu_function.yaml")
    # 运行程序
    run(**args)