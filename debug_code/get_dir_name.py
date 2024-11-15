import os


import sys
from pathlib import Path
ROOT = Path(__file__).parents
FILE = str(ROOT[1])
sys.path.append(FILE)


from utils.method import read_csv_as_dict

file_path = r"E:\video_picture_material"
folder_name = os.listdir(file_path)

values = read_csv_as_dict(r"E:\video_picture_material\source_of_material.csv")
for value in values:
    # print(value["序号"], value["英文名称"], value["中文名称"])
    name = str(value["序号"]) + "-" + value["英文名称"]

    for dir in folder_name:
        if value["中文名称"] in dir:
            print(f">>>[name] {dir} in {name}")

            os.rename(os.path.join(file_path, dir), os.path.join(file_path, name))
            
    



