import pandas as pd
from datetime import datetime


import re

import csv

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
