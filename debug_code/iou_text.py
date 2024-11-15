import cv2
import json
import glob

from pathlib import Path

def get_images_from_directory(directory, extensions=["jpg", "jpeg", "png", "gif"]):

    image_files = []
    for ext in extensions:
        pattern = os.path.join(directory, f"*.{ext}")
        image_files.extend(glob.glob(pattern))
    
    return image_files

def read_iou_json(json_path):
    with open(json_path, 'r') as f:
        configs = json.load(f)
    return configs

colors = {
    "WHITE": (255, 255, 255),  
    "BLACK": (0, 0, 0),  
    "RED": (255, 0, 0),  
    "GREEN": (0, 255, 0),  
    "BLUE": (0, 0, 255),  
    "YELLOW": (0, 255, 255),  # 注意：这实际上是青色，但传统上也被称作黄色  
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

def iou_to_image(image_pth, json_pth, outpath, rate=1):
    im_index = int(Path(image_pth).stem.split("-")[0])
    image = cv2.imread(image_pth)
    height_img, width_img, _ = image.shape
    print(f">>>> image path: {image_pth}")
    print(f">>>> iou name: {json_pth}")
    configs = read_iou_json(json_pth)
    for content in configs["class"]:
        if content['label'] == im_index:
            for filt in content.get('filters', []):
                if 'iou_xywh' in filt:
                    iou_xywh = filt['iou_xywh']
                    print(f">>>>[iou_xywh] image label id: {im_index}")
                    print(f">>>>[iou_xywh] image iou iou_xywh: {iou_xywh}")
                    x_center = float(iou_xywh[0])*width_img + 1
                    y_center = float(iou_xywh[1])*height_img + 1

                    iou_xywh_width = 0.5*float(iou_xywh[2])*rate
                    print(f">>>>[iou_xywh] image iou iou_xywh width Rate x {rate}: {iou_xywh_width*2} {iou_xywh_width*2-float(iou_xywh[2])}")
                    iou_xywh_height = 0.5*float(iou_xywh[3])*rate
                    print(f">>>>[iou_xywh] image iou iou_xywh height Rate x {rate}: {iou_xywh_height*2} {iou_xywh_height*2-float(iou_xywh[3])}")

                    xminVal = int(x_center - iou_xywh_width*width_img)   # int(iou_xywh 列表中的元素都是字符串类型
                    yminVal = int(y_center - iou_xywh_height*height_img)
                    xmaxVal = int(x_center + iou_xywh_width*width_img)
                    ymaxVal = int(y_center + iou_xywh_height*height_img)

                    pt1 = (xmaxVal, ymaxVal)   
                    pt2 = (xminVal, yminVal)
                    # 定义矩形的颜色 (BGR) 和线条粗细  
                    color = colors['RED']
                    thickness = 4 
                    image = cv2.rectangle(image, pt1, pt2, color, thickness) 

                if 'region' in filt:
                    region = filt['region']
                    print(f">>>> image label id: {im_index}")
                    print(f">>>> image iou region: {region}")
                    x_center = float(region[0])*width_img + 1
                    y_center = float(region[1])*height_img + 1

                    region_width = 0.5*float(region[2])*rate
                    print(f">>>> image iou region width Rate x {rate}: {region_width*2} {region_width*2-float(region[2])}")
                    region_height = 0.5*float(region[3])*rate
                    print(f">>>> image iou region height Rate x {rate}: {region_height*2} {region_height*2-float(region[3])}")

                    xminVal = int(x_center - region_width*width_img)   # int(region 列表中的元素都是字符串类型
                    yminVal = int(y_center - region_height*height_img)
                    xmaxVal = int(x_center + region_width*width_img)
                    ymaxVal = int(y_center + region_height*height_img)

                    pt1 = (xmaxVal, ymaxVal)   
                    pt2 = (xminVal, yminVal)
                    # 定义矩形的颜色 (BGR) 和线条粗细  
                    color = colors['BLUE']
                    thickness = 4 
                    image = cv2.rectangle(image, pt1, pt2, color, thickness) 
    cv2.imwrite(outpath, image)


'''
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
'''