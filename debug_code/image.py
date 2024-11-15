import os
import cv2
from pathlib import Path

from kahoku_tools.utils.logs import LogDriver

def get_image_size_opencv(image_path):
    img = cv2.imread(image_path)
    return img.shape[1], img.shape[0]  # 返回 (width, height)

def get_all_files(directory, extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tif', '.tiff')):
    """ 获取多层文件夹下的所有文件"""
    files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(extensions):
                files.append(os.path.join(root, file))
    return files

import os
import shutil
import csv
def write_csv_values(file_path, values):
    with open(file_path, mode='a+', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(values)

def classify_files_by_extension(source_dir):
    """ 根据文件扩展名对文件进行分类 """
    # 遍历目录中的所有文件和子目录
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            # 获取文件的完整路径
            file_path = os.path.join(root, file)
            # 提取文件扩展名
            extension = os.path.splitext(file)[1].lower()
            
            # 如果文件有扩展名，则处理
            if extension:
                # 创建一个新目录名基于文件扩展名
                dest_dir = os.path.join(source_dir, extension[1:])  # 移除点号
                # 如果目录不存在，则创建目录
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                
                # 构建目标文件路径
                dest_path = os.path.join(dest_dir, file)
                # 移动文件
                shutil.move(file_path, dest_path)
                print(f"Moved '{file}' to '{dest_dir}'")
            else:
                print(f"No extension found for '{file}', file not moved.")

def classify_extension(directory):
    """ 获取目录下所有类型的文件，并将所有的文件按扩展名分类 """

    file_types = set()

    # 遍历目录中的所有文件和子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 获取文件扩展名
            extension = os.path.splitext(file)[1].lower()
            if extension:  # 确保扩展名存在
                file_types.add(extension)

    # 打印所有唯一的文件类型
    print("File types found:", file_types)


def rename_images(directory, label=None):
    """ 重命名图片文件为数字序列 格式: 大小_标签_序号.扩展名
    Args:
        directory (str): 需要重命名的图片所在目录
    """
    extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tif', '.tiff')
    i = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(extensions):
                im = os.path.join(root, file)

                try:
                    width, height = get_image_size_opencv(im)
                except:
                    shutil.move(im, r'E:\video_picture_material\Non')
                    continue
                im_name = Path(im).with_stem(f"{width}X{height}_{label}_1v{i}")
                print(f"{i} {im} {width}X{height} => {im_name}")
                i += 1
                # break
                os.rename(im, im_name)


from PIL import Image
import imagehash
import os
def remove_duplicate_images(directory):
    hashes = {}
    duplicates = []

    log = LogDriver(r'E:\video_picture_material\remove_duplicate_images.log')
    # 使用 os.walk 遍历目录及其所有子目录
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                # 获取文件的完整路径
                image_path = os.path.join(root, filename)
                try:
                    with Image.open(image_path) as img:
                        # 计算图片的哈希值
                        hash = imagehash.average_hash(img)

                    # 检查哈希值是否已存在
                    if hash in hashes:
                        duplicates.append(image_path)
                        
                        print(f"Duplicate found: {image_path} is a duplicate of {hashes[hash]}")
                        log.info(f"Duplicate found: {image_path} is a duplicate of {hashes[hash]}")
                        # 可选：删除重复图片
                        # os.remove(image_path)
                        shutil.move(image_path, r'E:\video_picture_material\Non\repetition')
                    else:
                        hashes[hash] = image_path
                except Exception as e:
                    print(f"Error opening {image_path}: {e}")
                    log.error(f"Error opening {image_path}: {e}")

    return duplicates

# 示例用法
if __name__ == '__main__':
    current_directory = r'E:\video_picture_material\pictures'  # 当前目录
    duplicates = remove_duplicate_images(current_directory)
    print("Duplicates:", duplicates)

