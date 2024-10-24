import yaml
import csv
import os
import pandas as pd
from pathlib import Path


# 配置文件路径
ROOT = Path(os.path.dirname(os.path.abspath(__file__)))
FILE = ROOT.parents
CONFIG_PATH = FILE[0] / 'config/config.yaml'

def read_yaml_file(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)

class Config:
    
    def __init__(self):
        self._config = read_yaml_file(CONFIG_PATH)

    def get_image_classify_api_values(self):

        return self._config['image_classify']
    
    def get_upload_image_to_url_api_values(self):

        return self._config['upload_image_to_url']
    
    def get_ai_sqs_request_api_values(self):

        return self._config['ai_sqs_request']
    
    def test_image_to_light_config(self):
        config = self._config['main_config']
        test_datasets_values = pd.read_csv(config["test_datasets_csv"])  

        return test_datasets_values, config
    
    def get_resp_img_url_values(self):

        return self._config['rtsp_img_url']

    def get_workflow_config_values(self):

        return self._config['workflow_config']





