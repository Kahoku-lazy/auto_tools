from ultralytics import YOLO

# pip install nvitop

# # Load a model
model = YOLO("yolo11x.pt")  # load a pretrained model (recommended for training)
results = model.train(data="yandex_yolo/yandex_icon.yaml", epochs=200, imgsz=640, device=[2, 3])

# Run inference on 'bus.jpg' with arguments
# model = YOLO(r"runs/detect/train2/weights/best.pt")
# results = model.predict("/ihoment/goveetest/liuwenle/yandex_yolo/images/train/1-V1006PWD011890.jpg", save=True, conf=0.1)

# for result in results:
#     result.show()