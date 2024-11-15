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
