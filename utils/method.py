""" 
@author: Kahoku
@date: 2024/08
@description: 基础方法, 包括文件操作, 字符串处理, 图片处理, 模型使用等
@version: 1.0
"""
import json, yaml, csv, re, os
import glob, cv2
import pandas as pd
import configparser 
from datetime import datetime
import pandas as pd
import csv
import cv2
import os
import fnmatch
import os
import time
# from playsound import playsound
from pathlib import Path


# ------------------------------------------------   装饰器：正则匹配  ------------------------------------------------
def regex_findall_return(pattern):
    """装饰器: 使用正则匹配返回参数"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if result:
                matchs = re.findall(pattern, result)
                if matchs:
                    return matchs
            return None
        return wrapper
    return decorator

def regex_findall(pattern):
    """装饰器: 使用正则匹配输入参数"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 应用正则表达式于输入参数
            matches = [re.findall(pattern, arg) for arg in args]
            matches = [item for sublist in matches for item in sublist]
            # 将匹配结果传递给被装饰的函数
            return func(matches, **kwargs)
        return wrapper
    return decorator


# ------------------------------------------------   Function： 文件读取（data）  ------------------------------------------------
def read_txt_as_list( file_path):
    path = Path(file_path)
    contents = path.read_text(encoding='utf-8')

    return contents.splitlines()

def read_yaml_as_dict( file_path):
    with open(file_path, mode='r', encoding="utf8") as f:
        yaml_values = yaml.load(f, Loader=yaml.FullLoader)

    return yaml_values

def read_csv_as_dict( file_path):
    data = pd.read_csv(file_path)

    return data.to_dict('records')

def read_csv_as_df( file_path):
    df = pd.read_csv(file_path)

    return df

def read_json_as_dict( configs_file):
    with open(configs_file, 'r') as f:
        configs = json.load(f)
    return configs

def read_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config

def read_json(json_path):
    with open(json_path, 'r') as f:
        configs = json.load(f)
    return configs

# ------------------------------------------------   Function： 文件写入（data）  ------------------------------------------------
def write_text(file_path, values: list):
    """ Function: 将列表类型数据写入文本文档中，逐行写入。
    args:
        - file_path: 文本文档的路径
        - values: 需要写入的数据； type: list。
    """
    path = Path(file_path)

    path.write_text("\n".join(values))

def write_csv_values(file_path, values, mode="a+"):
    with open(file_path, mode, newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(values)


# ------------------------------------------------   Function： 获取文件（file）  ------------------------------------------------
def get_file_all(file_path, suffix):
    """ 获取指定目录下的所有文件路径 """
    files = []
    for ext in suffix:
        files.extend(glob.glob(os.path.join(file_path, f'**/**{ext}'),  recursive=True))
    return files

def is_value_exist(text, pattern):
    """ 判断是否存在某个特定的值 """
    match = re.findall(pattern, text)
    if match:
        return True
    return None

def find_value(text, pattern):
    """ 查找符合模式的第一个匹配项 """
    match = re.search(pattern, text)
    if match:
        return match
    else:
        return None

def get_images_all(directory):
    """ 获取指定目录下的所有图像文件路径 """
    image_extensions = ["*.jpg", "*.jpeg", "*.png"]
    image_paths = []
    for root, _, files in os.walk(directory):
        for ext in image_extensions:
            for image in fnmatch.filter(files, ext):
                image_paths.append(os.path.join(root, image))

    return image_paths
# ------------------------------------------------   Function： 获取数据（time）  ------------------------------------------------
def get_current_time():
    """ 获取当前系统时间 """
    current_time = datetime.now()
    return current_time 

def time_difference_in_minutes(start_time, end_time):
    """ 计算两个时间差值并以分钟为单位返回 """
    time_difference = end_time - start_time
    
    time_difference_seconds = time_difference.total_seconds()
    time_difference_minutes = time_difference_seconds / 60
    
    return time_difference_minutes


# ------------------------------------------------   Function： 音频处理   ------------------------------------------------
def play_audio(file_path, second):
    """ 播放目录下所有的音频文件 """
    for dirpath, _, filenames in os.walk(file_path):
        for file in filenames:
            audio_path = os.path.join(dirpath, file)
            playsound(audio_path)
            time.sleep(second)

# ------------------------------------------------   Function： 不常用的方法  ------------------------------------------------
def capture_single_frame(rtsp_url, save_path, crop_x):
    """ 从RTSP流中抓取单帧并保存到本地磁盘 （摄像头拍摄）"""
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        print("Error: Unable to open the RTSP stream.")
        return False
    try:
        # 读取一帧
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to fetch frame from the stream.")
            return False
        height, width = frame.shape[:2]
        new_width_start = crop_x
        new_width_end = width - crop_x

        cropped_frame = frame[:, new_width_start:new_width_end]

        cv2.imwrite(save_path, cropped_frame)
        return True
    finally:
        cap.release()

def find_keys_by_value( my_dict, value_to_find):
    """ Function: 通过字典的值去查找与配对应字典的键
    args:
        - my_dict:  字典
        - value_to_find: 值
    return:
        - keys: 值对应的键； 无对应的键则返回为空
    """
    for key, value in my_dict.items():
        if value == value_to_find:
            return key
    return None












