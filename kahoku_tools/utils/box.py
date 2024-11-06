""" @author: Kahoku
@date: 2024/08
@description: 基础方法, 包括文件操作, 字符串处理, 图片处理, 模型使用等
@version: 1.0
"""
import json, yaml, csv, sqlite3
import re, sys, shutil, os, logging
import glob, cv2, torch
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd

import PIL
from cnocr import CnOcr
from difflib import SequenceMatcher
from ultralytics import YOLO
from pathlib import Path

class MyDatabase:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        # self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS records (
                                id INTEGER PRIMARY KEY,
                                name TEXT UNIQUE,
                                video_state TEXT,
                                detect_state TEXT,
                                file_type TEXT,
                                game_name TEXT
                            )''')
        self.conn.commit()

    def insert_record(self, name, suffix, game_name, video_state, detect_state):
        try:
            self.cursor.execute("INSERT INTO records (name, video_state, detect_state, file_type, game_name) VALUES (?, ?, ?, ?, ?)", (name,video_state, detect_state, suffix, game_name))
            self.conn.commit()
            return True
            # print("Record inserted successfully.")
        except sqlite3.IntegrityError:
            return False
            # print("Error: User with the same name already exists.")

    def update_record_video_state(self, name, video_state):
        self.cursor.execute("UPDATE records SET video_state = ? WHERE name = ?", (video_state, name))
        self.conn.commit()
        print("Record updated successfully.")

    def update_record_detect_state(self, name, detect_state):
        self.cursor.execute("UPDATE records SET detect_state = ? WHERE name = ?", (detect_state, name))
        self.conn.commit()
        print("Record updated successfully.")

    def delete_record(self, name):
        self.cursor.execute("DELETE FROM records WHERE name = ?", (name,))
        self.conn.commit()
        print("Record deleted successfully.")

    def fetch_all_records(self):
        self.cursor.execute("SELECT * FROM records")
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def get_user_video_state(self, name):
        self.cursor.execute('SELECT video_state FROM records WHERE name = ?', (name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        
    def get_user_detect_state(self, name):
        self.cursor.execute('SELECT detect_state FROM records WHERE name = ?', (name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]

    def close_connection(self):
        self.conn.close()
        print("Database connection closed.")

    def add_column_text(self, column_name):
        self.cursor.execute(f'ALTER TABLE records ADD COLUMN {column_name} TEXT')
        self.conn.commit()
        print(f"Column '{column_name}' added successfully.")

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

def read_yaml_dict(yaml_path):

    yaml_file = Path(yaml_path)  
    if yaml_file.exists():  
        with yaml_file.open('r') as file:  
            data = yaml.safe_load(file)  
    else:  
        return False
    
    return data

def read_txt_as_list( file_path):
    path = Path(file_path)
    contents = path.read_text()

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

def wirte_text(file_path, values: list):
    """ Function: 将列表类型数据写入文本文档中，逐行写入。
    args:
        - file_path: 文本文档的路径
        - values: 需要写入的数据； type: list。
    """
    path = Path(file_path)

    path.write_text("\n".join(values))

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

def wirte_csv_values(file_path, values, mode="a+"):
    with open(file_path, mode, newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(values)

def get_file_all(file_path, suffix):
    files = []
    for ext in suffix:
        files.extend(glob.glob(os.path.join(file_path, f'**/**{ext}'),  recursive=True))
    return files


class YOLOTools:
    """ 目标检测模型 """

    def yolov8_predict_image(self, model, source, device=2, conf=0.8):
        model = YOLO(model)  # load an official model
        results = model(source=source, conf=conf, device=device, save_conf=True, stream=True)
        return results
    
    def yolov5_hub_predict_image(self, model, images, device=2, title=None):

        if title is None:
            title = ["xmin", "ymin", "xmax", "ymax", "confidence", "class", "name", "image_name"]
        model = torch.hub.load("ultralytics/yolov5", 'custom', path=model, device=device) # load an official model
        df = pd.DataFrame(columns=title)
        for im in images:
            try:
                result = model(im)
            except PIL.UnidentifiedImageError as e:
                print("UnidentifiedImageError: ", im)
                continue
            except Exception as e:
                print("Exception: ", im)
                continue
            # result = model(im)
            result_xyxy = result.pandas().xyxy[0]
            if result_xyxy.empty:
                continue
            result_xyxy["image_name"] = Path(im).name
            
            # 修改标签名称，转为小写字符
            for i in range(len(result_xyxy)):
                result_xyxy["name"].values[i] = result_xyxy["name"].values[i].lower()
            df = pd.concat([df, result_xyxy], ignore_index=True)
        return df
    
    def yolov8_reuslts(self, results, outpath, video_name, count, save_txt=False):

        image_name = f"{Path(video_name).stem}_{count}.jpg"
        label_txt_name = str(Path(image_name).with_suffix(".txt"))

        for result in results:
            for box in result.boxes:
                c, conf, id = int(box.cls), float(box.conf), None if box.id is None else int(box.id.item())
                classes_name = ('' if id is None else f'id:{id} ') + result.names[c]  # classes 标签  

            if len(result.boxes) > 0:
           
                # 保存图片结果 (原始图像的 numpy 数组)
                output_image = Path(outpath) / "images" / classes_name / image_name
                if not output_image.parent.exists():
                    output_image.parent.mkdir(parents=True, exist_ok=True) 
                cv2.imwrite(str(output_image), result.orig_img)

                if not save_txt: 
                    return
                # 保存txt标签结果
                output_label = Path(outpath) / "labels" / classes_name / label_txt_name
                if not output_label.parent.exists():
                    output_label.parent.mkdir(parents=True, exist_ok=True)  

                if output_label.exists():
                    output_label.unlink()
                result.save_txt(output_label)

    def yolov8_predict_video(self, video_path, frames_per_second, output_path, model, device=2, conf=0.8):

        model = YOLO(model) 
        video_name = Path(video_path).stem

        video_capture = cv2.VideoCapture(video_path)   
        frame_rate = int(video_capture.get(cv2.CAP_PROP_FPS))
        if frame_rate < 20 and frame_rate > 144:
            return False
        
        frame_interval = frame_rate // frames_per_second
        frame_count = 0
        while True:
            success, frame = video_capture.read()

            if not success:
                break

            frame_count += 1
            if frame_count % frame_interval == 0:
                results = model.predict(source=frame, conf=conf, device=device, stream=True)
                self.yolov8_reuslts(results, output_path, video_name, frame_count) 

        video_capture.release()

        return True

    def yolov5_results(self, image, results, outpath, video_name, count, save_json=True):

        result_xyxy = results.pandas().xyxy[0]
        if result_xyxy.empty:
            return
        
        image_name = f"{Path(video_name).stem}_{count}.jpg"
        result_json_name = Path(image_name).with_suffix(".json")

        result_xyxy["image_name"] = image_name
        clasees_name = result_xyxy["name"].values[0]

        # 保存图片结果 (原始图像的 numpy 数组)
        output_image =  Path( outpath) / "images" / clasees_name / image_name
        if not output_image.parent.exists():
            output_image.parent.mkdir(parents=True, exist_ok=True) 
        if isinstance(image, np.ndarray):
            cv2.imwrite(str(output_image), image)

        if not save_json: 
            return
        # 保存json标签结果
        output_json =  Path( outpath) / "json" / clasees_name / result_json_name
        if not output_json.parent.exists():
            output_json.parent.mkdir(parents=True, exist_ok=True) 
        if output_json.exists():
            output_json.unlink()
        result_xyxy.to_json(str(output_json), orient='records', lines=True)

    def yolov5_predict_video(self, video_path, frames_per_second, output_path, model, device=2, conf=0.8):

        if isinstance(device, list):
            device = device[0]
        model = torch.hub.load("ultralytics/yolov5", 'custom', path=model, device=device)
    
        video_name = Path(video_path).stem

        video_capture = cv2.VideoCapture(video_path)   
        frame_rate = int(video_capture.get(cv2.CAP_PROP_FPS))
        if frame_rate < 20 and frame_rate > 144:
            return False
        
        frame_interval = frame_rate // frames_per_second
        frame_count = 0
        while True:
            success, frame = video_capture.read()
            if not success:
                break

            frame_count += 1
            if frame_count % frame_interval == 0:
                yolo_result = model(frame)
                df1 = self.yolov5_results(frame, yolo_result, output_path, video_name, frame_count)

        video_capture.release()

        return True

    def convert_annotation(self, classes, input_file, output_file):
        """ Function: yolov5 XML标签转换为 txt标签
        args:
            - classes:   特性标签序列
            - input_file,: 输入XML文件
            - output_file:  输出txt文档
        """
        @staticmethod
        def xml_convert(img_size, box):
            """ 转换公式: 将图片坐标换算为yolo text标签 """
            dw = 1. / (img_size[0])
            dh = 1. / (img_size[1])
            x = (box[0] + box[2]) / 2.0 - 1
            y = (box[1] + box[3]) / 2.0 - 1
            w = box[2] - box[0]
            h = box[3] - box[1]
            x = x * dw
            w = w * dw
            y = y * dh
            h = h * dh
            return x, y, w, h
      
        with open(input_file, encoding='UTF-8') as xmls:
            tree = ET.parse(xmls)       # xml解析文件
            root = tree.getroot()

            """ 获得size字段内容 width, height """
            size = root.find('size')    
            w = int(size.find('width').text)
            h = int(size.find('height').text)
            if w == 0 and h == 0:
                print(f"width = {w}, height = {h}")
                return
            
            for obj in root.iter('object'):
                difficult = obj.find('difficult').text
                cls = obj.find('name').text
                if cls not in classes or int(difficult) != 0:
                    print(f"cls not in classes or difficult != 0, skip this obj, cls = {cls} difficult = {difficult}")
                    continue
                cls_id = classes.index(cls)  # 获得打标元祖下标
                xml_box = obj.find('bndbox')
                box = (float(xml_box.find('xmin').text),
                    float(xml_box.find('ymin').text),
                    float(xml_box.find('xmax').text),
                    float(xml_box.find('ymax').text))
                convert_box = xml_convert((w, h), box)

                with open(output_file, 'w') as txt:
                    txt.write(str(cls_id) + " " + " ".join([str(a) for a in convert_box]) + '\n')

    def label_to_coord(self, image, label_txt: str):
        """ Function: yolov5标签 转图片实际坐标
        args:
            - img_path:  图片路径
            - label_txt: 图片对应的标签值
        """
        @staticmethod
        def text_convert(label_txt):
            # yolo label转坐标 公式
            x_center = float(label_txt[1])*width_img + 1
            y_center = float(label_txt[2])*height_img + 1

            xminVal = int(x_center - 0.5*float(label_txt[3])*width_img)   # int(label_txt列表中的元素都是字符串类型
            yminVal = int(y_center - 0.5*float(label_txt[4])*height_img)
            xmaxVal = int(x_center + 0.5*float(label_txt[3])*width_img)
            ymaxVal = int(y_center + 0.5*float(label_txt[4])*height_img)

            pt1 = (xmaxVal, ymaxVal)   
            pt2 = (xminVal, yminVal)
            
            return pt1, pt2, int(label_txt[0])

        height_img, width_img, _ = image.shape
        
        pt1, pt2, index = text_convert(label_txt.split(" "))
        
        return pt1, pt2, index

    def coord_to_label(self, img_path, coord):
        """ Function: yolov5标签 转图片实际坐标
        args:
            - img_path:  图片路径
            - label_txt: 图片对应的标签值
        """
        @staticmethod
        def xml_convert(img_size, box):
            """ 转换公式: 将图片坐标换算为yolo text标签 """
            dw = 1. / (img_size[1])
            dh = 1. / (img_size[0])
            x = (box[0] + box[2]) / 2.0 - 1
            y = (box[1] + box[3]) / 2.0 - 1
            w = box[2] - box[0]
            h = box[3] - box[1]
            x = x * dw
            w = w * dw
            y = y * dh
            h = h * dh
            return x, y, w, h

        img = cv2.imread(img_path)
        
        return xml_convert(img.shape, coord)
    
    def yolo_img_label(self, image_pth, label_pth, outpath):
        """ 在图片上框出label标签的位置
        用来检查标注框位置
        """
        colors = {"WHITE": (255, 255, 255),  
                    # "BLACK": (0, 0, 0),  
                    "RED": (255, 0, 0),  
                    "GREEN": (0, 255, 0),  
                    "BLUE": (0, 0, 255),  
                    # "YELLOW": (0, 255, 255),  # 注意：这实际上是青色，但传统上也被称作黄色  
                    "CYAN": (0, 255, 255),    # 真正的青色  
                    "MAGENTA": (255, 0, 255),  
                    "PINK": (255, 192, 203),  # 浅粉色  
                    "DEEP_PINK": (255, 20, 147),  
                    "ORANGE": (255, 165, 0),  
                    "GOLD": (255, 215, 0),    # 金色的一种近似  
                    "LIGHT_GREEN": (144, 238, 144),  
                    "DARK_CYAN": (0, 139, 139),  
                    "SKY_BLUE": (135, 206, 250),  # 天蓝色的一种近似  
                    "BROWN": (165, 42, 42),  
                    "GRAY": (128, 128, 128),  
                    "SILVER": (192, 192, 192),  
                    "PURPLE": (128, 0, 128),  
                    "TEAL": (0, 128, 128)  # 茶色（或称为海蓝色），这是另一种常用的颜色  
                }  

        image = cv2.imread(image_pth)
        txts = read_txt_as_list(label_pth)
        for txt in txts:
            coold = self.label_to_coord(image, txt)
            # 定义矩形的颜色 (BGR) 和线条粗细  
            color = list(colors.values())[coold[2]]
            thickness = 2  
            image = cv2.rectangle(image, coold[0], coold[1], color, thickness) 
            # print(coold)

        # 保存图像  
        save_dir = Path(outpath) / Path(image_pth).name
        if save_dir.parent.exists():
            save_dir.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(save_dir), image)  


class CnocrTools():

    def ocr_text(self, text, image_path, threshold=0.9):
        """ Function: 
            1、Cnocr 模型识别图片中文字；
            2、对比文字内容, 相似度大于0.6则返回True
        args:
            - text: 文字内容
            - image_path 要识别的图片路径
            - threshold: 文字相似度, 文字相似程度[-1 ~ 1]
        """
        def text_similarity(a, b):
            """ 对比文字 相似程度范围[-1 ~ 1]"""
            return SequenceMatcher(None, a, b).ratio()
        
        govee_ocr = CnOcr(det_model_name='en_PP-OCRv3_det', rec_model_name='en_PP-OCRv3',context='cuda:2')
        ocr_results = govee_ocr.ocr(image_path)
        for ocr_result in ocr_results:
            for txt in text:
                similarity = text_similarity(txt, ocr_result["text"])
                if similarity > threshold:
                    return txt
        return None

    def ocr_text_img(self, image_path, output_path):
        """ Function: Cnocr 模型识别图片中文字, 输出识别结果
        """
        govee_ocr = CnOcr(det_model_name='en_PP-OCRv3_det', rec_model_name='en_PP-OCRv3',context='cuda:0')
        ocr_results = govee_ocr.ocr(image_path)
        image = cv2.imread(image_path)
        for ocr_result in ocr_results:
            
            # 定义矩形的左上角和右下角坐标
            top_left = [int(x) for x in tuple(ocr_result["position"][0])]
            bottom_right = [int(x) for x in tuple(ocr_result["position"][2])]
            cv2.rectangle(image, top_left , bottom_right, (0, 0, 255), 2)
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.8
            font_color = (0, 255, 0)  # 白色
            cv2.putText(image, f'{ocr_result["text"]} {ocr_result["score"]:.2f}', bottom_right, font, font_scale, font_color, 2, cv2.LINE_AA)
    
        cv2.imwrite(os.path.join(output_path, os.path.basename(image_path)), image)
        

def find_value(text, pattern = r'Detect class:\s*(\d+)'):
    """
    从给定文本中提取 "Detect class: <数字>" 中的数字。

    :param text: 包含 "Detect class: <数字>" 的字符串
    :return: 提取的数字，如果没有找到，则返回 None
    """
    # 定义正则表达式模式
    # pattern = r'Detect class:\s*(\d+)'

    match = re.search(pattern, text)
    
    if match:
        return match.group(1)
    else:
        return None

def find_all_values(text, pattern = r'Detect class:\s*(\d+)'):
    """
    查找字符串中所有包含 'Detect class: 0' 的部分，并提取其中的 '0'。

    :param text: 输入的字符串
    :return: 包含所有 '0' 的列表
    """
    # >> send >> d0 00 26 46 46 4f ff ff f5 40 00 70
    # pattern = r'Detect class:\s*(0)'  # 匹配 'Detect class: 0' 并捕获 0
    matches = re.findall(pattern, text)
    return matches
    

import glob
import os

def get_images_from_directory(directory, extensions=["jpg", "jpeg", "png", "gif"]):
    """
    获取指定目录中的所有图片文件。

    :param directory: 要查找图片的目录路径
    :param extensions: 图片文件的扩展名列表（默认包括 jpg、jpeg、png、gif）
    :return: 图片文件路径列表
    """
    image_files = []
    for ext in extensions:
        # 拼接匹配模式
        # pattern = os.path.join(directory, "**", f"*.{ext}")
        pattern = os.path.join(directory, f"*.{ext}")
        # 查找所有匹配的文件
        image_files.extend(glob.glob(pattern))
    
    return image_files

import configparser

def read_config(file_path):
    pass

from datetime import datetime

class Utils:
    
    def read_config(self, file_path):
        # 创建 ConfigParser 对象
        config = configparser.ConfigParser()
        # 读取配置文件
        config.read(file_path)
        return config

    def is_value_exist(self, text, pattern):
        match = re.findall(pattern, text)
        if match:
            return True
        return None

    def find_value(self, text, pattern):
        match = re.search(pattern, text)
        if match:
            return match
        else:
            return None

    def write_csv_values(self, file_path, values):
        with open(file_path, mode='a+', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(values)

    def get_current_time(self):
        current_time = datetime.now()
        return current_time 
    
    def time_difference_in_minutes(self, start_time, end_time):

        time_difference = end_time - start_time
        
        time_difference_seconds = time_difference.total_seconds()
        time_difference_minutes = time_difference_seconds / 60
        
        return time_difference_minutes
    