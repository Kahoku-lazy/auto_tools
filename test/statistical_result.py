import pandas as pd
import numpy as np
from datetime import datetime


import re

import csv

def analyze_list(data):
    # 将列表转换为NumPy数组
    np_array = np.array(data)

    # 计算平均值、最大值和最小值
    mean_value = np.mean(np_array)
    max_value = np.max(np_array)
    min_value = np.min(np_array)

    # 统计最大值和最小值的数量
    max_count = np.sum(np_array == max_value)
    min_count = np.sum(np_array == min_value)

    # 找到最大值和最小值的索引
    max_index = np.argmax(np_array)
    min_index = np.argmin(np_array)

    return mean_value, max_value, min_value, max_count, min_count, max_index, min_index

def calculate_time_difference(target_time_str, current_time):
    # 将字符串转换为datetime对象
    target_time = datetime.strptime(target_time_str, '%Y-%m-%d %H:%M:%S')
    
    # 获取当前时间
    current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
    
    # 计算时间差
    time_difference = current_time - target_time
    
    # 返回差值的总秒数
    return time_difference.total_seconds()

def write_csv_values(file_path, values, mode="a+"):
    with open(file_path, mode, newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(values)

log_file_paths = [
        (r'D:\Kahoku\auto_tools\runner\logs\filter_log.log', 
            r"(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}).*(switch.on|switch.off|color_configs_set_success)"),
        (r"D:\Kahoku\auto_tools\runner\logs\runner_log.log",
            r"(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}).*(Done|Match Template:)")
        ]


log_entries = []
for i in log_file_paths:
    log_file_path, log_pattern = i
    with open(log_file_path, 'r') as file:
        for line in file:
            match = re.search(log_pattern, line)
            if match:
                timer = match.group(1)
                value = match.group(2)
                # 提取整行作为日志条目
                log_entries.append((timer, value))

data_with_datetime = [(datetime.strptime(timestamp, '%Y/%m/%d %H:%M:%S'), message) for timestamp, message in log_entries]
data_with_datetime.sort()

write_csv_values(r"D:\Kahoku\auto_tools\runner\excel\test_result.csv", ["timer", "value"])
for entry in data_with_datetime:
    timer = entry[0].strftime('%Y-%m-%d %H:%M:%S')
    value = entry[1]
    write_csv_values(r"D:\Kahoku\auto_tools\runner\excel\test_result.csv", [timer, value])


df = pd.read_csv(r"D:\Kahoku\auto_tools\runner\excel\test_result.csv")

# 初始化一个空的列表来保存结果
filtered_rows = []

# 遍历DataFrame，查找相邻的"Done"和"color_configs_set_success"
response_time = []
for i in range(len(df) - 1):
    if (df.iloc[i]['value'] == 'Done' and df.iloc[i + 1]['value'] != 'Done'):
        filtered_rows.append(df.iloc[i])
        filtered_rows.append(df.iloc[i + 1])
        timer = calculate_time_difference(df.iloc[i]["timer"], df.iloc[i+1]["timer"])
        response_time.append(timer)

# 将结果转换为新的DataFrame
result_df = pd.DataFrame(filtered_rows).drop_duplicates().reset_index(drop=True)

result_df.to_csv(r"D:\Kahoku\auto_tools\runner\excel\timer_result_1.csv", index=False)

analyze_list(response_time)
mean, maximum, minimum, max_count, min_count, max_index, min_index = analyze_list(response_time)
print(f">>> 总次数: {len(response_time)}")
print(f">>> 平均值: {mean}")
print(f">>> 最大值: {maximum}，数量: {max_count}, 下标: {max_index}")
print(f">>> 最小值: {minimum}，数量: {min_count}, 下标: {min_index}")
