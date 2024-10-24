""" @author: Kahoku
@date: 2024/08
@description: 配置文件, 配置文件路径
@version: 1.0
"""

import sys
sys.path.append("/ihoment/goveetest/liuwenle/code/app_autotest/")

# local moudle
import os
import re
from pathlib import Path
from app.base.box import LogDriver, MyDatabase
from app.base.box import read_yaml_as_dict, wirte_csv_values, get_file_all

class Config():
    
    def __init__(self):

        self.config_path = "config/config.yaml"
        self._config = read_yaml_as_dict(self.config_path)

        """ ····································  输入文件路径 ······································""" 
        # 模型推理后图片位置
        self.DETECT_PATH = Path(self._config["DETECT_PATH"])
        self.CLASEES_PATH = Path(self._config["CLASEES_PATH"])    
        # 数据集路径
        self.DATASETS_PATH = Path(self._config["DATASETS_PATH"]) 
        # 视频路径
        self.VIDEO_CSV_PATH = Path(self._config["VIDEO_CSV_PATH"])   
        # 测试模型数据信息 csv路径 
        self.MODEL_CSV_PATH = Path(self._config["MODEL_CSV_PATH"])  
         # 测试集数据信息 csv路径
        self.TEST_DATASET_CSV_PATH = Path(self._config["TEST_DATASET_CSV_PATH"])   


        """ ····································  日志报告文件路径  ······································""" 
        # 日志文件路径
        self.LOGS_PATH = Path(self._config["LOGS_PATH"])      
        # 模型测试结果 csv文件
        self.MODEL_RESULT_CSV_PATH = Path(self._config["MODEL_RESULT_CSV_PATH"])  
        # 模型结果图片保存路径
        self.TEST_RESULT_IMAGE_PATH = Path(self._config["TEST_RESULT_IMAGE_PATH"])  

        # 报告日志文件配置
        auto_log_path = self.LOGS_PATH.joinpath("auto_log.txt")
        self.logs= LogDriver(auto_log_path)

        """ ····································  数据库配置  ······································""" 
        # 数据库配置
        self.db = MyDatabase(self._config["sqlite3_db"])

        """ ····································  游戏序号与列表  ······································""" 
        # 所有游戏列表
        self.GAME_LIST = self._config["GAME_LIST"]
        self.MODEL_LIST = self._config["MODEL_LIST"]
        self.VIDEO_FORMAT = self._config["VIDEO_FORMAT"]



class DatasetsInfo():

    def __init__(self):

        self.config = Config()

        # 测试数据集信息：游戏名称，标签名称，数据类型（训练集，测试集，其它类型）图片类型（正样本、负样本），图片名称， 图片路径
        self.test_datasets_tilte = ["game_name", "label_name", "data_type", "image_type", "image_name", "image_path",]
        # 测试模型信息：游戏名称，模型名称，模型类型(设备、服务器)，模型版本（V01, V02），yolo版本，备注，路径
        self.test_models_tilte = ["model_name", "model_type", "model_ver", "yolo_ver", "model_path"]
        # 测试视频信息: 游戏名称, 视频名称，视频路径
        self.test_videos_tilte = ["game_name", "video_name", "video_path"]
        # 测试结果信息: 游戏名称, 模型名称，模型类型(设备、服务器)，模型版本（V01, V02），yolo版本，备注，路径
        self.model_result_tilte = ["xmin", "ymin", "xmax", "ymax", "confidence", "class", "name", "image_name"]

        # 正则
        self.test_datasets_pattern = r".*/(uncleaned|test|train)/(.+?)/(.+?)/(images|negative)/(.+?)/"
        self.test_models_pattern = r".*/models/(server|device)/(.+?)/(.+?)/(.+?)/"
        self.test_video_pattern = r".*/video_game/(.+?)/"
        
    def wirte_test_datasets_csv_title(self, path):
        wirte_csv_values(path, self.test_datasets_tilte)

    def wirte_test_model_csv_title(self, path):
        wirte_csv_values(path, self.test_models_tilte)

    def wirte_test_videos_csv_title(self, path):
        wirte_csv_values(path, self.test_videos_tilte)

    def wirte_model_result_csv_title(self, path):
        wirte_csv_values(path, self.model_result_tilte)
        

    def wirte_test_datasets_csv_data(self, file_path, value):
        match = re.search(self.test_datasets_pattern, value)
        if match is None:
            return
        
        label_name = match.group(5).lower().replace(" ", "_")
        values = [match.group(3), label_name, match.group(1),match.group(4), Path(value).name, value]
        wirte_csv_values(file_path, values)

    def wirte_test_models_csv_data(self, file_path, value):
        match = re.search(self.test_models_pattern, value)
        if match is None:
            return
        
        values = [Path(value).name, match.group(1), match.group(3),match.group(2), value]
        wirte_csv_values(file_path, values)

    def wirte_test_videos_csv_data(self, file_path, value):
        match  = re.search(self.test_video_pattern, value)
        if match is None:
            return
        
        values = [match.group(1), Path(value).name, value]
        wirte_csv_values(file_path, values)

    def wirte_dataset_info(self):

        datasets_path = self.config.DATASETS_PATH
        for i in [self.config.TEST_DATASET_CSV_PATH, self.config.MODEL_CSV_PATH, self.config.VIDEO_CSV_PATH]:
            if os.path.exists(i):
                os.remove(i)

        # 图片
        self.wirte_test_datasets_csv_title(self.config.TEST_DATASET_CSV_PATH)
        for i in get_file_all(datasets_path, [".jpg"]):
            self.wirte_test_datasets_csv_data(self.config.TEST_DATASET_CSV_PATH, i)

        # 模型
        self.wirte_test_model_csv_title(self.config.MODEL_CSV_PATH)
        for i in get_file_all(datasets_path, [".pt"]):
            self.wirte_test_models_csv_data(self.config.MODEL_CSV_PATH, i)

        # 视频
        self.wirte_test_videos_csv_title(self.config.VIDEO_CSV_PATH)
        for i in get_file_all(datasets_path, [".mp4", ".webm"]):
            self.wirte_test_videos_csv_data(self.config.VIDEO_CSV_PATH, i)

if __name__ == "__main__":
    config = Config()

    number = 2
    print(config.GAME_LIST[number])
