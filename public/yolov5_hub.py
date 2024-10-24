import sys
from pathlib import Path
sys.path.append("/ihoment/goveetest/liuwenle/code/app_autotest")
import platform
import pathlib
plt = platform.system()
if plt != 'Windows':
  pathlib.WindowsPath = pathlib.PosixPath


from app.base.box import YOLOTools, get_file_all, wirte_csv_values

# model = "/ihoment/goveetest/ai_team/game_datasets/models/server/yolov5/V02-20240717/phase1/mario_Kart8_V5s-2024-08-08.pt"
# image_path = "/ihoment/goveetest/liuwenle/data/pictures/game_R/mario_Kart8_pictures"

model = "/ihoment/goveetest/ai_team/game_datasets/models/server/yolov5/V03-20240815/debug_models/Sekiro_Shadows_Die_Twice-08144.pt"
image_path = "/ihoment/goveetest/liuwenle/20240819/Sekiro - Shadows Die Twice"

images = get_file_all(image_path, [".jpg"])
title = ["image_name", "conf", "class", "id", "image_path"]
game_name = "Sekiro_Shadows_Die_Twice"
csv_file = f"/ihoment/goveetest/liuwenle/code/app_autotest/debug/labels/{game_name}.csv"

wirte_csv_values(csv_file, title)
# for index, image in enumerate(images):
#     print(f">>>  {index+1} / {len(images)}  {image}")
#     results = YOLOTools().yolov8_predict_image(model, image, device=3, conf=0.25)
#     for result in results:
#         # label_txt_path = Path(result.path).with_suffix(".txt").name
#         # result.save_txt(f"/ihoment/goveetest/liuwenle/code/app_autotest/debug/labels/{label_txt_path}")
#         for box in result.boxes:
#             # c, conf, id = int(box.cls), float(box.conf), None if box.id is None else int(box.id.item())
#             # classes_name = ('' if id is None else f'id:{id} ') + result.names[c]
#             # print("image_name: ", Path(image).name, "conf: ", conf, "class: ", classes_name, "id: ", c)
#             values = [Path(image).name, float(box.conf), result.names[int(box.cls)], int(box.cls), image]
#             wirte_csv_values(csv_file, values)

df = YOLOTools().yolov5_hub_predict_image(model, images, device=3)
result_csv_path = "/ihoment/goveetest/liuwenle/code/app_autotest/result/model_results/debug_test_result/yolov5_hub.csv"
df.to_csv(result_csv_path, index=False)