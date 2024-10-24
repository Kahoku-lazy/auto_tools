import os
from pathlib import Path
import pandas as pd
import shutil
from pathlib import Path

import yaml
import random
import os
import cv2
from ultralytics import YOLO

# Local module
from app.base.box import YOLOTools, read_txt_as_list, CnocrTools, get_file_all
from app.config import Config
from app.dataset import select_model, select_videos, DatasetsInfo


class GameImageCapture():
    """ yolo应用场景一: 游戏图片数据采集"""

    def __init__(self):

        self.yolo_tools = YOLOTools()
        self.ocr_tools = CnocrTools()
        self.config = Config()

    def call_other_class_method(self, obj, method_name, **method_args):
        method = getattr(obj, method_name)
        if method:
            method(**method_args)
        else:
            print(f"Method '{method_name}' not found")

    def yolo_detect_db(self, game_name, model_ver, device=[3], conf=0.8, yolo_model="yolov5"):

        video_path_list = select_videos(game_name)["video_path"].tolist()
        self.config.logs.info(f"{game_name} 游戏视频数量 {len(video_path_list)}")
        for video in video_path_list:
            self.config.logs.info(f"视频路径 {video}")
            video_name = Path(video).name
            video_stem = Path(video).stem
 
            file_type = Path(video).suffix if os.path.isfile(video) else "dir"  
            self.config.db.insert_record(video_stem, file_type, game_name, "False", "False")

            if self.config.db.get_user_detect_state(video_stem) == "True" or \
                file_type.lower()  not in self.config.VIDEO_FORMAT:     # 不符合视频格式
                continue
           
            model = select_model(game_name=game_name, model_type="server", model_ver=model_ver, yolo_ver=yolo_model)
            if model is None:
                self.config.logs.error(f"{game_name}模型不存在; {model}")
                continue
            self.config.logs.info(f"开始推理 {game_name}: {video_name}")
            self.config.logs.info(f"加载{model}模型")
            if not Path(model).exists():
                self.config.logs.info(f"{game_name}: {model} 模型不存在")
                return
        
            method_args = {"video_path": video, "frames_per_second": 3,
                           "model": model,"device": device,"conf": conf,
                           "output_path": self.config.DETECT_PATH.joinpath(game_name)
                           }
            
            if yolo_model in ["yolov8", "yolov5"]:
                method_name = f"{yolo_model}_predict_video"
            else:
                self.config.logs.error(f"yolo_model = {yolo_model} 参数错误")
                continue
 
            state = self.call_other_class_method(self.yolo_tools, method_name, **method_args)
            if state: # 推理成功
                self.config.db.update_record_detect_state(video.stem, "True")
                self.config.logs.info(f"{video.parents[0].name} -- {video.name} 推理成功")

    def the_first_descendant(self):
        ocr_text_list = [ "Vulgus Data Transmitter",
                    "Level Reached",
                    "Mastery Rank Up Available",
                    "Activate New Field",
                    "Intercept Successful",
                    "Mission Complete",
                    "Mission Failed",
                    ]
        top_left = (600, 100)
        bottom_right = (1500, 300)
        game_name = "the_first_descendant"
        game_video_path = "/ihoment/goveetest/liuwenle/20240819/the_first_descendant"
        video_path_list = get_file_all(game_video_path, ".mp4")
        self.config.logs.info(f"{game_name} 游戏视频数量 {len(video_path_list)}")
        for video in video_path_list:
            self.config.logs.info(f"视频路径 {video}")
            video_name = Path(video).name
            video_stem = Path(video).stem

            file_type = Path(video).suffix if os.path.isfile(video) else "dir"  
            # self.config.db.insert_record(video_stem, file_type, game_name, "False", "False")

            if self.config.db.get_user_detect_state(video_stem) == "True" or \
                file_type.lower()  not in self.config.VIDEO_FORMAT:     # 不符合视频格式
                continue

            self.config.logs.info(f"开始推理 {game_name}: {video_name}")

            video_capture = cv2.VideoCapture(video)   
            frame_rate = int(video_capture.get(cv2.CAP_PROP_FPS))
            if frame_rate < 20 and frame_rate > 144:
                return False
            
            frame_interval = frame_rate // 3
            frame_count = 0
            while True:
                success, frame = video_capture.read()

                if not success:
                    break

                frame_count += 1
                if frame_count % frame_interval == 0:
                    # image_arr = cv2.imread(image_path)
                    cropped_image = frame[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
                    ocr_text = CnocrTools().ocr_text(ocr_text_list, cropped_image)
                    if ocr_text is not None:
                        out_path = "/ihoment/goveetest/liuwenle/20240819/the_first_descendant_images"
                        print(f">>> save image path: {out_path}")
                        print(f">>> ocr_text result: {ocr_text}")
                        output_path = os.path.join(out_path, ocr_text.lower().replace(" ", "_"))
                        if not os.path.exists(output_path):
                            os.makedirs(output_path)
                        try:
                            # shutil.move(image, output_path)
                            cv2.imwrite(os.path.join(output_path, f"{ocr_text}_{frame_count}.jpg"), frame)
                        except shutil.Error as e:
                            pass
                            # print(f">>> shutil.move({image}, {output_path}) error: {e}")
                            # os.remove(image)
            video_capture.release()

    def yolo_classify_picture(self, model_ver, yolo_model, device):
        """ 使用 yolo 分类图片 """
        model_list = self.config.MODEL_LIST    # 模型列表
        self.config.logs.info("当前 yolo 支持的模型列表如下:")
        df = pd.DataFrame(model_list, columns=['game_name'])
        self.config.logs.info(df)
        DatasetsInfo().video_csv_init()
        for game_name in model_list:
            self.yolo_detect_db(game_name=game_name, model_ver=model_ver, yolo_model=yolo_model, device=device)  # 模型推理

# 运行环境安装：pip install ultralytics opencv-python
""" 训练yolov8模型

准备数据：数据格式如下
游戏名称目录 --- 特征名称目录 --- images/labels
游戏名称目录 --- classses.txt

"""
class Yolov8Train():

    import os
    # 关闭 wandb
    os.environ['WANDB_MODE'] = 'disabled'

    def yolov8_train(self, train_yaml, device: list):
        model = YOLO("yolov10x.pt")
        results = model.train(data=train_yaml,  
                            #   project=project, 
                              device=device,
                            batch=16*len(device), save_json=True, epochs=200,   
                            )
        return results

    def read_classes_text(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:  
            for line in f:  
                yield line.strip()

    def model_start_training(self, game_name, training_data_path, classes_txt_path):

        # 训练数据
        training_data_path = Path(training_data_path)
        training_dataset_path = training_data_path.parent / "yolo" / game_name
        if not training_dataset_path.exists():
            training_dataset_path.mkdir(parents=True, exist_ok=True)
        train_ratio = 0.8

        train_path = training_dataset_path.joinpath("train")
        val_path = training_dataset_path.joinpath("val")

        # yolo 训练配置文件
        train_config = {}
        train_config["train"] = str(train_path)
        train_config["val"] = str(train_path)
        train_config["names"] = [txt for txt in self.read_classes_text(classes_txt_path)]
        train_config["nc"] = len(train_config["names"])
        # 保存配置文件
        save_config_path = training_dataset_path.joinpath("config.yaml")
        with open(save_config_path, 'w') as file:  
            yaml.dump(train_config, file, default_flow_style=False, sort_keys=False)

        # 划分训练数据集
        for dirpath, _, filenames in os.walk(training_data_path):
            # 随机打乱数据
            random.shuffle(filenames)
            # 拆分数据
            split_point = int(train_ratio * len(filenames))
            train_files = filenames[:split_point]
            val_files = filenames[split_point:]

            # 移动train数据
            for filename in train_files:
                if filename.lower().endswith(".jpg"):
                    image = os.path.join(dirpath, filename)
                    label = image.replace("images", "labels").replace("jpg", "txt")

                    training_images = train_path / "images"
                    if not os.path.exists(training_images):
                        os.makedirs(training_images)

                    training_labels = train_path / "labels"
                    if not os.path.exists(training_labels):
                        os.makedirs(training_labels)

                    shutil.copy(image, training_images)
                    shutil.copy(label, training_labels)

            # 移动val数据
            for filename in val_files:
                if filename.lower().endswith(".jpg"):
                    image = os.path.join(dirpath, filename)
                    label = image.replace("images", "labels").replace("jpg", "txt")

    
                    validation_images= val_path / "images"
                    if not os.path.exists(validation_images):
                        os.makedirs(validation_images)

                    validation_labels = val_path / "labels"
                    if not os.path.exists(validation_labels):
                        os.makedirs(validation_labels)

                    shutil.copy(image, validation_images)
                    shutil.copy(label, validation_labels)

        return  save_config_path, training_dataset_path
            
def yolov8_train(training_data_path):

    print(f">>> 开始准备训练数据：{training_data_path}")
    game_names = os.listdir(training_data_path)
    with open("result/game_list.txt", "w") as f:
        for item in game_names :
            f.write(item + "\n")
    for game_name in game_names:
        game_training_data_path = training_data_path + "/" + game_name
        classes_txt_path = game_training_data_path + "/classes.txt"

        training_dataset_path = game_training_data_path

        print(f">>> 开始准备训练数据：{game_name}")
        print(f">>> 训练数据路径：{training_dataset_path}")
        print(f">>> classes标签路径: {classes_txt_path}")
        config, training_dataset = Yolov8Train().model_start_training(game_name, training_dataset_path, classes_txt_path)

        print(f">>> 开始训练：{dir}")
        print(f">>> 训练数据路径：{training_dataset}")
        results = Yolov8Train().yolov8_train(config, [2,3])
        print(f">>> 训练完成, 删除文件：{training_dataset}")
        # print(f">>> 训练完成, 模型路径：{results}")
        shutil.rmtree(training_dataset)


















