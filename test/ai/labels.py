"""
贴图脚本，批量复制标签到
"""

import shutil
import os
from pathlib import Path

im_path = r"C:\Users\10035\Pictures\yandex\images"

le_path = r"C:\Users\10035\Pictures\yandex\1-V1006PWD011891.txt"
out_path = r"C:\Users\10035\Pictures\yandex\labels"

for im_name in os.listdir(im_path):
    le_name = Path(im_name).with_suffix(".txt")
    shutil.copy(le_path , os.path.join(out_path, le_name))

