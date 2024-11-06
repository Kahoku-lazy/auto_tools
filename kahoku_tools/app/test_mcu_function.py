"""  Laziness is my only productivity.
@ author: Kahoku
@ date: 2024/11
@ description: 通过串口发送指令与接收返回值, 来压测MCU功能
@ version: 1.0
"""
import sys
sys.path.append(r'D:\Kahoku\auto_tools\kahoku_tools')
from utils.serial import SerialWindows

import random
import time
import re

def add_end_check_bit(hex_string):
    """ 计算校验值字符串末尾 """
    numbers = [int(num, 16) for num in hex_string.split()]
    hex_result = hex(sum(numbers) % 256)[2:].upper()
    result = hex_string + " " + hex_result
    return result

def serial_command_sender(ser, values, mode='sequential', interval=1):
    """ 发送指令功能
        values: (commands, keywords);     commands: 指令列表  keyword: 检查指令是否生效的关键字
        mode: 'sequential', 'random', 'all'
        interval: 指令间隔时间，单位秒
    """
    responses = []
    
    if mode == 'random':
        random.shuffle(values)

    # 准备数据
    commands = [command[0] for command in values]
    keywords = [keyword[1] for keyword in values]

    for i, command in enumerate(commands):
        # 清空缓冲区
        serial_port.reset_buffer()

        # 添加校验位，发送指令
        command = add_end_check_bit(command)
        print(f">>>[{i+1}/{len(commands)}] Sending Command: {command}")
        ser.write_serial_data(command.encode("utf8"))

        time.sleep(interval)  # 设置间隔

        # 读取串口返回值, 抓取关键字，判断是否发送成功
        response = ser.get_buffer_data()
        print(f">>>[Receive] Receive Data: {response}; keyword: {keywords[i]}")
        if re.search(keywords[i], response):
            flag = True
        else:
            flag = False

        # 记录输入与输出结果
        responses.append((command, flag, response, keywords[i]))

    return responses

# 示例用法
if __name__ == "__main__":

    # 输入、输出
    # values: (commands, keywords);   commands: 指令列表      keyword: 检查指令是否生效的关键字
    values = [
        ('55 00 0B 00 00 60','aaf0019b'),
        ('55 F0 01 46', 'aaf0019c'),  # 心跳
        ('55 F7 01 4d', 'aaf0019d'),  # 软件版本
        ('55 F7 02 4e', 'aaf0019e' )# 硬件版本
    ]

    # 打开串口
    serial_port = SerialWindows('COM13', 9600)
    serial_port.open_serial()
    # 设置缓冲区
    serial_port.set_buffer_size(rx_size=1024 * 1024, tx_size=128)
    # 针对 MCU 专项测试，随机发送指令
    results = serial_command_sender( serial_port, values, mode="random", interval=1)
    # 测试结束, 关闭串口
    serial_port.close_serial()