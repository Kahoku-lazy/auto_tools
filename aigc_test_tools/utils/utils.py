import pandas as pd
import csv
import cv2
import os
import fnmatch


def capture_single_frame(rtsp_url, save_path, crop_x):

    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        print("Error: Unable to open the RTSP stream.")
        return False
    try:
        # 读取一帧
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to fetch frame from the stream.")
            return False
        height, width = frame.shape[:2]
        new_width_start = crop_x
        new_width_end = width - crop_x

        cropped_frame = frame[:, new_width_start:new_width_end]

        cv2.imwrite(save_path, cropped_frame)
        return True
    finally:
        cap.release()

def write_csv_values(file_path, values):
    with open(file_path, mode='a+', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(values)

def get_images(directory):
    image_extensions = ["*.jpg", "*.jpeg", "*.png"]
    image_paths = []
    for root, _, files in os.walk(directory):
        for ext in image_extensions:
            for image in fnmatch.filter(files, ext):
                image_paths.append(os.path.join(root, image))

    return image_paths

def read_txt_values(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()
