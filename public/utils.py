""" 
@ author: Kahoku
@ date: 2024/08
@ description: 基础方法, 包括文件操作, 字符串处理, 图片处理, 模型使用等
@ version: 1.0
"""
import json, yaml, csv, re, os, glob, cv2
import pandas as pd

from cnocr import CnOcr
from difflib import SequenceMatcher
from pathlib import Path

class box:

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
        
    def get_file_all(file_path, suffix):
        files = []
        for ext in suffix:
            files.extend(glob.glob(os.path.join(file_path, f'**/**{ext}'),  recursive=True))
        return files

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


import configparser

def read_config(file_path):
    # 创建 ConfigParser 对象
    config = configparser.ConfigParser()

    # 读取配置文件
    config.read(file_path)

    return config










