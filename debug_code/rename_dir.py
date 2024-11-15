import os

import sys
sys.path.append(r"auto_tools\kahoku_tools")
from utils.method import read_txt_as_list


anime_name = read_txt_as_list(r"E:\KahokuCodeFiles\image_dirname.txt")


file_path = r"E:\video_picture_material\【Pictures】未归类的图片\otaku_pictures"
anime_name_path = r"E:\KahokuCodeFiles\image_dirname.txt"

for dir in os.listdir(file_path):
    path = os.path.join(file_path, dir)
    name = anime_name[int(dir)]
    new = os.path.join(file_path, name)
    print(f"{path} --> {new}")
    os.rename(path, new)
