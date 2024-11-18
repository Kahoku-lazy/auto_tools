import sys
from pathlib import Path
ROOT = Path(__file__).parents
FILE = str(ROOT[1])
sys.path.append(FILE)

from utils.method import *

file_pth = "config/yandex_audio.csv"
values = read_csv_as_df(file_pth)
print(values)
