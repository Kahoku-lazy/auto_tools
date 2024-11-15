import argparse, shutil, datetime
import os,time, json
import platform
import sys
from pathlib import Path
from govee import MovieCheck

import torch
import glob
import pandas as pd 

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from models.common import DetectMultiBackend
from utils.dataloaders import IMG_FORMATS, VID_FORMATS, LoadImages, LoadScreenshots, LoadStreams
from utils.general import (LOGGER, Profile, check_file, check_img_size, check_imshow, check_requirements, colorstr, cv2,
                           increment_path, non_max_suppression, print_args, scale_boxes, strip_optimizer, xyxy2xywh)
from utils.plots import Annotator, colors, save_one_box
from utils.torch_utils import select_device, smart_inference_mode

@smart_inference_mode()
def run(
        roi_file='',
        weights=ROOT / 'yolov5s.pt',  # model path or triton URL
        source=ROOT / 'data/images',  # file/dir/URL/glob/screen/0(webcam)
        data=ROOT / 'data/coco128.yaml',  # dataset.yaml path
        imgsz=(640, 640),  # inference size (height, width)
        conf_thres=0.25,  # confidence threshold
        iou_thres=0.45,  # NMS IOU threshold
        max_det=1000,  # maximum detections per image
        device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        view_img=False,  # show results
        save_txt=False,  # save results to *.txt
        save_conf=False,  # save confidences in --save-txt labels
        save_crop=True,  # save cropped prediction boxes
        nosave=False,  # do not save images/videos
        classes=None,  # filter by class: --class 0, or --class 0 2 3
        agnostic_nms=False,  # class-agnostic NMS
        augment=False,  # augmented inference
        visualize=False,  # visualize features
        update=False,  # update all models
        project=ROOT / 'runs/detect',  # save results to project/name
        name='exp',  # save results to project/name
        exist_ok=False,  # existing project/name ok, do not increment
        line_thickness=3,  # bounding box thickness (pixels)
        hide_labels=False,  # hide labels
        hide_conf=False,  # hide confidences
        half=False,  # use FP16 half-precision inference
        dnn=False,  # use OpenCV DNN for ONNX inference
        vid_stride=1,  # video frame-rate stride
        classify=False,  # classify function
        movie_info=None,  # check movie info
):
    source = str(source)
    save_img = not nosave and not source.endswith('.txt')  # save inference images
    is_file = Path(source).suffix[1:] in (IMG_FORMATS + VID_FORMATS)
    is_url = source.lower().startswith(('rtsp://', 'rtmp://', 'http://', 'https://'))
    webcam = source.isnumeric() or source.endswith('.txt') or (is_url and not is_file)
    screenshot = source.lower().startswith('screen')
    if is_url and is_file:
        source = check_file(source)  # download

    # 实例化 MovieCheck
    mc = MovieCheck() if movie_info else None

    # Directories
    save_dir = increment_path(Path(project) / name, exist_ok=exist_ok)  # increment run # 保存结果文件夹
    (save_dir / 'labels' if save_txt else save_dir).mkdir(parents=True, exist_ok=True)  # make dir

    # Load model
    device = select_device(device)
    model = DetectMultiBackend(weights, device=device, dnn=dnn, data=data, fp16=half)
    stride, names, pt = model.stride, model.names, model.pt
    imgsz = check_img_size(imgsz, s=stride)  # check image size

    # Dataloader
    bs = 1  # batch_size
    if webcam:
        view_img = check_imshow(warn=True)
        dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt, vid_stride=vid_stride)
        bs = len(dataset)
    elif screenshot:
        dataset = LoadScreenshots(source, img_size=imgsz, stride=stride, auto=pt)
    else:
        dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt, vid_stride=vid_stride)
    vid_path, vid_writer = [None] * bs, [None] * bs

    # Run inference
    model.warmup(imgsz=(1 if pt or model.triton else bs, 3, *imgsz))  # warmup
    seen, windows, dt = 0, [], (Profile(), Profile(), Profile())
    cls_path = ''

    # 创建分类文件夹
    if classify:
        cls_dir = increment_path(os.path.join(save_dir, 'classify'), exist_ok=exist_ok)  # increment run
        cls_cnt = 0

    for path, im, im0s, vid_cap, s in dataset:
        with dt[0]:
            im = torch.from_numpy(im).to(model.device)
            im = im.half() if model.fp16 else im.float()  # uint8 to fp16/32
            im /= 255  # 0 - 255 to 0.0 - 1.0
            if len(im.shape) == 3:
                im = im[None]  # expand for batch dim

        # Inference
        with dt[1]:
            visualize = increment_path(save_dir / Path(path).stem, mkdir=True) if visualize else False
            pred = model(im, augment=augment, visualize=visualize)

        # NMS
        with dt[2]:
            pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)

        # Process predictions
        for i, det in enumerate(pred):  # per image
            seen += 1
            if webcam:  # batch_size >= 1
                p, im0, frame = path[i], im0s[i].copy(), dataset.count
                s += f'{i}: '
            else:
                p, im0, frame = path, im0s.copy(), getattr(dataset, 'frame', 0)

            p = Path(p)  # to Path
            save_path = str(save_dir / p.name)  # im.jpg
            # save_dir = str(save_dir / 'labels' / p.stem) + ('' if dataset.mode == 'image' else f'_{frame}')
            txt_path = str(save_dir / 'labels' / p.stem) + ('' if dataset.mode == 'image' else f'_{frame}')  # im.txt
            s += '%gx%g ' % im.shape[2:]  # print string
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            imc = im0.copy() if save_crop else im0  # for save_crop
            annotator = Annotator(im0, line_width=line_thickness, example=str(names))

            # 没有预测结果也需要 check
            if mc and len(det) == 0 and dataset.mode == 'video':
                mc.check_movie(path, movie_info, vid_stride, dataset.frame, None, im0s, None, save_dir)

            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()

                if classify and dataset.mode == 'video':
                    cls_cnt += 1

                # Print results
                for c in det[:, 5].unique():
                    n = (det[:, 5] == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                    if classify:
                        if dataset.mode == 'image':
                            dest_dir = os.path.join(cls_dir, str(names[int(c)]))
                            os.makedirs(dest_dir, exist_ok=True)
                            shutil.copy(p, dest_dir)
                        else:
                            if cls_path != path:
                                cls_cnt = 0
                                # cls_prefix = datetime.datetime.now().strftime("%S")
                                cls_path = path
                                print("switch video source path:", path)
                            # 判断是视频 则创建视频文件夹
                            dest_dir = os.path.join(cls_dir, Path(path).stem, str(names[int(c)]))
                            os.makedirs(dest_dir, exist_ok=True)
                            # cls_file_name =f"{cls_prefix}_{cls_cnt:07d}.jpg"
                            cls_file_name = os.path.split(txt_path)[-1] + '.jpg'
                            img_path = os.path.join(dest_dir, cls_file_name)
                            cv2.imwrite(img_path, im0)


                # Write results
                for *xyxy, conf, cls in reversed(det):
                    if save_txt:  # Write to file
                        xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                        line = (cls, *xywh, conf) if save_conf else (cls, *xywh)  # label format
                        with open(f'{txt_path}.txt', 'a') as f:
                            f.write(('%g ' * len(line)).rstrip() % line + '\n')
                    
                    threshold = None
                    if save_img or save_crop or view_img:  # Add bbox to image
                        c = int(cls)  # integer class
                        label = None if hide_labels else (names[c] if hide_conf else f'{names[c]} {conf:.2f}')

                        if c in rect_dict.keys():
                            _xywh = rect_dict[c]
                            theo_xyxy = [_xywh[0] - _xywh[2] / 2, _xywh[1] - _xywh[3] / 2, _xywh[0] + _xywh[2] / 2,
                                         _xywh[1] + _xywh[3] / 2]
                            theo_xyxy = [theo_xyxy[0] * im0.shape[1], theo_xyxy[1] * im0.shape[0],
                                         theo_xyxy[2] * im0.shape[1], theo_xyxy[3] * im0.shape[0]]

                            act_xyxy = [x.item() for x in xyxy]
                            iou = IoU(act_xyxy, theo_xyxy)

                            label += f' iou: {str(iou)}'
                            annotator.box_label(theo_xyxy, "theo", color=colors(c + 1, True))


                        if os.path.exists(roi_file):
                            with open(roi_file, 'r') as f:
                                global configs
                                configs = json.load(f)

                            for content in configs["class"]:

                                if content['label'] == c:
                                    act_xyxy = [x.item() for x in xyxy]

                                    for filt in content['filters']:
                                        if ("iou_xywh" in filt) and ("iou_threshold" in filt):
                                            region = filt['iou_xywh']
                                            threshold = filt['iou_threshold']

                                            theo_xyxy = [region[0] - region[2]/2, region[1] - region[3]/2, region[0] + region[2]/2, region[1] + region[3]/2]
                                            theo_xyxy = [theo_xyxy[0] * im0.shape[1], theo_xyxy[1] * im0.shape[0], theo_xyxy[2] * im0.shape[1], theo_xyxy[3] * im0.shape[0]]

                                            iou = IoU(act_xyxy, theo_xyxy)
                                            if iou >= threshold:
                                                save_one_box(xyxy, imc, file=save_dir / 'iou_xywh' / names[c] / f'{p.stem}.jpg', BGR=True)
                                            label += f' iou: {str(iou)}'

                                            annotator.box_label(theo_xyxy, "iou_xywh", color = colors(c + 1, True))


                                        if 'region' in filt:
                                            region = filt['region']
                                            threshold = filt['iou_threshold']

                                            theo_xyxy = [region[0] - region[2]/2, region[1] - region[3]/2, region[0] + region[2]/2, region[1] + region[3]/2]
                                            theo_xyxy = [theo_xyxy[0] * im0.shape[1], theo_xyxy[1] * im0.shape[0], theo_xyxy[2] * im0.shape[1], theo_xyxy[3] * im0.shape[0]]
                                            # print('=region:')
                                            # print(theo_xyxy)
                                            # print(act_xyxy)

                                            # if [act_xyxy[0], theo_xyxy[1], theo_xyxy[2], act_xyxy[3]] < [theo_xyxy[0], act_xyxy[1], act_xyxy[2], theo_xyxy[3]]:
        
                                            def is_rectangle_inside(act, theo):

                                                result = act[0] >= theo[0] and act[1] > theo[1] and \
                                                        act[2] <= theo[2] and act[3] <= theo[3]
                                                return result
                                            if is_rectangle_inside(act_xyxy, theo_xyxy):
                                                save_one_box(xyxy, imc, file=save_dir / 'region' / names[c] / f'{p.stem}.jpg', BGR=True)
                                                
                                            annotator.box_label(theo_xyxy, "region", color = colors(c + 2, True))
                                        
                                        # if 'weight' in filt:
                                        #     weight = filt['weight']

                                        #     xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()
                                        #     if not (weight[0] < xywh[2] < weight[1]):
                                        #         save_one_box(xyxy, imc, file=save_dir / 'weight' / names[c] / f'{p.stem}.jpg', BGR=True)
                                        #         print("weight is error")


                                        # if 'height' in filt:
                                        #     height = filt['height']

                                        #     xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()
                                        #     if not (height[0] < xywh[2] < height[1]):
                                        #         save_one_box(xyxy, imc, file=save_dir / 'height' / names[c] / f'{p.stem}.jpg', BGR=True)
                                        #         print("height is error")

                        annotator.box_label(xyxy, label, color=colors(c, True))

                    if save_crop and threshold is None:
                        save_one_box(xyxy, imc, file=save_dir / 'crops' / names[c] / f'{p.stem}.jpg', BGR=True)

                    if mc and dataset.mode == 'video':
                        mc.check_movie(path, movie_info, vid_stride, dataset.frame, names[int(c)], im0s, annotator.result(), save_dir)

            # Stream results
            im0 = annotator.result()
            if view_img:
                if platform.system() == 'Linux' and p not in windows:
                    windows.append(p)
                    cv2.namedWindow(str(p), cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)  # allow window resize (Linux)
                    cv2.resizeWindow(str(p), im0.shape[1], im0.shape[0])
                cv2.imshow(str(p), im0)
                cv2.waitKey(1)  # 1 millisecond

            # Save results (image with detections)
            if save_img:
                if dataset.mode == 'image':
                    cv2.imwrite(save_path, im0)
                else:  # 'video' or 'stream'
                    if vid_path[i] != save_path:  # new video
                        vid_path[i] = save_path
                        if isinstance(vid_writer[i], cv2.VideoWriter):
                            vid_writer[i].release()  # release previous video writer
                        if vid_cap:  # video
                            fps = vid_cap.get(cv2.CAP_PROP_FPS)
                            w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        else:  # stream
                            fps, w, h = 30, im0.shape[1], im0.shape[0]
                        save_path = str(Path(save_path).with_suffix('.mp4'))  # force *.mp4 suffix on results videos
                        vid_writer[i] = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                    vid_writer[i].write(im0)

        # Print time (inference-only)
        LOGGER.info(f"{s}{'' if len(det) else '(no detections), '}{dt[1].dt * 1E3:.1f}ms")

    # Print results
    t = tuple(x.t / seen * 1E3 for x in dt)  # speeds per image
    LOGGER.info(f'Speed: %.1fms pre-process, %.1fms inference, %.1fms NMS per image at shape {(1, 3, *imgsz)}' % t)
    if save_txt or save_img:
        s = f"\n{len(list(save_dir.glob('labels/*.txt')))} labels saved to {save_dir / 'labels'}" if save_txt else ''
        LOGGER.info(f"Results saved to {colorstr('bold', save_dir)}{s}")
    if update:
        strip_optimizer(weights[0])  # update model (to fix SourceChangeWarning)

rect_dict = {}
def read_rect(rect_file):
    with open(rect_file) as f:
        for line in f.readlines():
            content = line.splitlines()[0].split(" ")
            print(content)
            rect_dict[int(content[0])] = [float(x) for x in content[1:]]

def IoU(box1, box2):
    in_w = min(box1[2], box2[2]) - max(box1[0], box2[0])
    in_h = min(box1[3], box2[3]) - max(box1[1], box2[1])

    inter = 0 if in_w <= 0 or in_h <= 0 else in_h * in_w
    union = (box2[2] - box2[0]) * (box2[3] - box2[1]) +\
            (box1[2] - box1[0]) * (box1[3] - box1[1]) - inter
    iou = inter / union
    return iou

def get_file_all(file_path, suffix):
    files = []
    for ext in suffix:
        files.extend(glob.glob(os.path.join(file_path, f'**/**{ext}'),  recursive=True))
    return files

def test_data_info(timer="20240924"):

    pictures_path = None
    models_path = None
    iou_path = None
    test_data = []

    models = get_file_all(models_path, [".pt"])
    for model in models:
        game_name = Path(model).name.split("_V5s")[0]
        model_ver = Path(model).parent.name
        image_path = os.path.join(pictures_path, game_name)
        iou = Path(iou_path).joinpath(game_name).with_suffix(".json")

        test_data.append([model_ver, game_name, model, image_path, iou])
        # print(model_ver, game_name, model, image_path, iou)
    
    df = pd.DataFrame(test_data, columns=["model_ver", "game_name", "model", "image_path", "iou"])

def test_pictures_info(file_path=None, timer="20240924"):

    if file_path is None:
        file_path = None
    images = get_file_all(file_path, [".jpg"])

    save_path = None

    images_info = []
    for i, im in enumerate(images):
        print(f">>>[info:] {i}/{len(images)}  image path: {im}")
        image_name = Path(im).name

        pth = Path(im).parents
        label_name = pth[0].name.lower()
        data_type = pth[1].name
        game_name = pth[2].name

        print(f">>>[info:] game name: {game_name}, label name: {label_name}, data type: {data_type}, image name: {image_name}")
        images_info.append([game_name, data_type, label_name, image_name, im])

        output_path = os.path.join(save_path, game_name)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        shutil.copy(im, output_path)
    df = pd.DataFrame(images_info, columns=["GameName", "DataType", "LabelName", "ImageName", "ImagePath"])
