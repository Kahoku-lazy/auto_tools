""" @author: Kahoku
@date: 2023/10
@description: YOLO模型测试, 包括模型测试结果计算与可视化
@version: 1.0
"""

import pandas as pd
import os
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix,precision_score, recall_score, f1_score, accuracy_score
import seaborn as sns


from app.config import DatasetsInfo, Config
from app.base.box import YOLOTools
from app.dataset import select_datasets, select_model

def time_name():
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d")
    return formatted_date        

class YoloModelTest(DatasetsInfo):
    def __init__(self):

        self.datasets_config = DatasetsInfo()
        self.detect_info_title = self.datasets_config.model_result_tilte

        self.ouput_path = self.datasets_config.config.MODEL_RESULT_CSV_PATH
        if not os.path.exists(self.ouput_path):
            os.makedirs(self.ouput_path)

    def yolo_detect_test(self, game_name, model_type, model_ver, yolo_ver, data_type):

        self.datasets_config.wirte_dataset_info()

        model_path = select_model(game_name, model_type, model_ver, yolo_ver)
        if model_path is None:
            print(f"model: {game_name} not found")
            return

        test_datasets = select_datasets(game_name, data_type)["image_path"].tolist()
        df = YOLOTools().yolov5_hub_predict_image(model_path, test_datasets, title=self.detect_info_title)
        # 保存结果
        result_csv_path = Path(self.ouput_path) / f"{game_name.lower()}_{data_type}_{time_name()}.csv"
        df.to_csv(str(result_csv_path), index_label='index')

        return result_csv_path

class YoloModelTestResult(Config):

    def __init__(self):

        self.config = Config()
        self.conf_threshold = 0.8
    
    def yolov5_model_test_results(self, game_name, data_type, model_result_csv_path, save_image=False):

        if not os.path.exists(model_result_csv_path):
            print(f"{game_name} detect info not found")
            return
        
        output_path = self.config.TEST_RESULT_IMAGE_PATH / game_name
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        test_datasets = select_datasets(game_name, data_type)
        model_result = pd.read_csv(model_result_csv_path)

        # 合并测试数据和模型识别结果，比较'image_name'和'name'列，如果相同则为'PASS'，否则为'FAIL'
        model_result_df = pd.merge(test_datasets, model_result, on='image_name')
        model_result_df['check_result'] = model_result_df.apply(lambda row: 'PASS' 
                                              if ((row['label_name'] == row['name']) and (row["image_type"] == "images")) # negative
                                               else 'FAIL', axis=1)
        # 保存结果
        model_result_df.to_excel(os.path.join(output_path, f"{game_name}_result_{time_name()}.xlsx"), index=False)

        
        # 预期输入特征数量
        anticipated = test_datasets[(test_datasets["game_name"]== game_name) & (test_datasets["image_type"]== "images")].groupby("label_name").size()

        # 计算模型结果
        self.sklearn_metrics(model_result_df, output_path)
        df = self.save_result_df(anticipated, model_result_df, output_path)

        # 保存 PR曲线图片结果
        self.save_draw(df, output_path)

        # 保存识别结果
        if save_image:
            self.save_sings(model_result_df, output_path, self.conf_threshold)

    def save_draw(self, df, output_path):
        
        df.plot(y=['Recall', 'Precision'], xlabel='Index', ylabel='Value', title='Recall and Precision', grid=True)
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig(os.path.join(output_path, f"PR.png"), dpi=1080)

    def save_sings(self, df, outpath, conf_min):

        groupby_df = df[df["confidence"] > conf_min].groupby("image_path")
        for name, value in groupby_df:
            im = Image.open(name).convert("RGBA")
            draw = ImageDraw.Draw(im)
            dir_name = "error"
            for index, row in value.iterrows():
                if row["check_result"] == "PASS":
                    dir_name = "sings"
                    
                draw.rectangle([(row["xmin"], row["ymin"]), (row["xmax"], row["ymax"])], 
                                outline="red", width=3)
                
                text = row["name"] + "_" + str(row["confidence"])
                # 选择字体和字号
                font = ImageFont.truetype("arial.ttf", 36)  
                draw.text((row["xmin"], row["ymax"]), 
                        text, font=font, fill="red")
                
            save_sing = f"{outpath}/{row['game_name']}/{row['label_name']}/{dir_name}/{row['image_name']}"
            if not Path(save_sing).parent.exists():
                Path(save_sing).parent.mkdir(parents=True, exist_ok=True)
        
            im.save(save_sing, format='PNG')

    def save_result_df(self, anticipated, result_df, output_path):
         
        # 模型识别结果 Positives（TP, FP）
        group_names = [name for name, _ in result_df.groupby("label_name")]
        positives = [(name, len(result_df[(result_df["label_name"]== name) & (result_df["confidence"] > self.conf_threshold)].groupby("image_path"))) for name in group_names]
        tp = result_df[(result_df["confidence"] > self.conf_threshold) & (result_df["check_result"] == "PASS")].groupby("label_name").nunique()

        # 模型识别结果 Positives（TP, FP）, Negatives（FN, TN）, Anticipated(TP, FN)
        df = pd.DataFrame({'Anticipated': anticipated, 'Positives': dict(positives), "TP": tp["image_name"]}).fillna(0)
        df["FP"] = df["Positives"] - df["TP"]
        df['Recall'] = df['TP'] / df['Anticipated']   
        df['Precision'] = df['TP'] / df['Positives']

         # 保存模型识别结果xlsx文件
        df.to_excel(os.path.join(output_path, f"PR_{time_name()}.xlsx"),index=True)
        
        return df

    def sklearn_metrics(self, result_df, outpath_path):

        # 计算混淆矩阵
        classes = [cls.lower() for cls in sorted(list(set(result_df["label_name"].tolist())))]
        actual = result_df["label_name"].tolist()
        predicted = result_df["name"].tolist()
        cm = confusion_matrix(actual, predicted, labels=classes)
        # 可视化混淆矩阵
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)

        plt.xlabel('Predicted labels')
        plt.ylabel('True labels')
        plt.title('Confusion Matrix')

        plt.savefig(f"{outpath_path}/confusion_matrix_{time_name()}.png")

        # 计算查准率（Precision）
        precision = precision_score(actual, predicted, average=None)

        # 计算查全率（Recall）
        recall = recall_score(actual, predicted, average=None, zero_division='warn')

        # 计算 F1 分数
        f1 = f1_score(actual, predicted, average=None)

        # 计算准确率（Accuracy）
        accuracy = accuracy_score(actual, predicted)

        # 保存 sklearn_metrics 结果
        df = pd.DataFrame({'label_name': classes, "Precision": precision, "Recall": recall, 
                           "F1 Score": f1, "Accuracy": accuracy})
        df.to_excel(os.path.join(outpath_path, f"sklearn_metrics_results_{time_name()}.xlsx"),index=True)




    
    



