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


