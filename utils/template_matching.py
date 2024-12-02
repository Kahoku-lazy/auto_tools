""" 
@ author: Kahoku
@ date: 2024/08
@ description:  图像识别算法一： 模板匹配算法
@update: 2024/11
@ version: 3.1
@ update:
    1. SIFT特征匹配器: 待优化，准确率不高； 针对不同尺寸的算法MultiScale 与 SIFI 准确率都待提高, 已测试的压缩尺寸[1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
    2. TemplateMatcher(针对同一尺寸分辨率手机), MultiScale(针对不同尺寸分辨率手机) 使用的 cv2.TM_CCOEFF_NORMED 选择二者中最大值的结果
        |- cv2.TM_CCOEFF_NORMED: 标准化相关系数匹配，值越大表示匹配越好。
    3. 修改了返回值的类型： 返回值为： 左上角坐标，右下角坐标，匹配置信度(当前算法越大越好, 范围[0 ~ 1])
"""

import cv2
import numpy as np

class TemplateMatcher:
    def __init__(self, method=cv2.TM_CCOEFF_NORMED, threshold=0.7):
        self.method = method
        self.threshold = max(0.7, threshold)  # 确保阈值不低于0.7

    def match(self,image, template):
        h, w = template.shape[:2]

        res = cv2.matchTemplate(image, template, self.method)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val >= self.threshold:
            top_left = max_loc
        else:
            return 0, 0, 0
                
        bottom_right = (top_left[0] + w, top_left[1] + h)
        return top_left, bottom_right, round(max_val, 3)

class MultiScale:
    def __init__(self, scales=None, threshold=0.7):
        if scales is None:
            # 不同缩放比例，从1.0到0.5，步长为0.1
            self.scales = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
        else:
            self.scales = scales

        self.threshold = max(0.7, threshold)  # 确保阈值不低于0.7

    def match(self, image, template, method = cv2.TM_CCOEFF_NORMED):
        template_h, template_w = template.shape[:2]

        best_loc = None
        best_scale = 1
        best_value = -1

        # 在不同的尺度上进行模板匹配
        for scale in self.scales:
            # 缩放模板
            resized = cv2.resize(template, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
            
            # 模板匹配
            res = cv2.matchTemplate(image, resized, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            if max_val > best_value and max_val > self.threshold:
                value = max_val
                loc = max_loc
            else:
                continue

            if value > best_value:
                best_value = value
                best_loc = loc
                best_scale = scale

        best_h, best_w = int(template_h * best_scale), int(template_w * best_scale)
        top_left = best_loc
        if top_left is None:
            return 0, 0, 0
        bottom_right = (top_left[0] + best_w, top_left[1] + best_h)
        return top_left, bottom_right, round(value, 3)

# SIFT特征匹配器： 待优化，准确率不高
class SIFTFeatureMatcher:
    def __init__(self):
        # 初始化SIFT检测器
        self.sift = cv2.SIFT_create()

    def match(self, image, template):

        # 灰度化
        img1_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        img2_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        # 寻找关键点和描述符
        keypoints1, descriptors1 = self.sift.detectAndCompute(img1_gray, None)
        keypoints2, descriptors2 = self.sift.detectAndCompute(img2_gray, None)

        # 匹配算法：FLANN（快速最近邻搜索库）或BFMatcher（暴力匹配器）等匹配算法
        matcher = cv2.BFMatcher()   # 创建匹配器对象
        # 使用knnMatch方法找到每个描述符的前两个最佳匹配（k=2），这有助于后续通过距离比测试筛选匹配点。
        matches = matcher.knnMatch(descriptors1, descriptors2, k=2)

        # 筛选匹配点
        good = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good.append(m)

        # 绘制匹配结果
        result = cv2.drawMatches(image, keypoints1, template, keypoints2, good, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        cv2.imwrite('result.png', result)
        if len(good) > 10:  # 如果匹配点数量大于10，则计算变换矩阵
            src_pts = np.float32([keypoints1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

            # 计算从模板图像到输入图像的透视变换矩阵（M）
            M, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)

            h, w = template.shape[:2]
            pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, M)
            print(dst)

        points = np.int32(dst).flatten().tolist()
        y1, x1 = points[0:2]
        y2, x2 = points[4:6]

        image = cv2.rectangle(image, points[0:2], points[4:6], (255, 0, 0), 2)
        cv2.imwrite('ret.png', image)
        return x1, y1, x2, y2


def match_template(image, template):
    template_matcher = TemplateMatcher().match(image, template)
    multi_scale = MultiScale().match(image, template)
    # print(f"template_matcher: {template_matcher};  multi_scale: {multi_scale}")
    if template_matcher[2] > 0 and template_matcher[2] >= multi_scale[2]:
        return template_matcher[:2] 
    elif multi_scale[2] > 0 and template_matcher[2] < multi_scale[2]:
        return multi_scale[:2]
    else:
        return None

if __name__ == '__main__':

    # 加载图像和模板
    # detail_page_off_1.png
    template_path = r"D:\Kahoku\auto_tools\config\yandex\yandex_icon\detail_page_on.png"

    image_path = r"D:\Kahoku\auto_tools\screenshot.png"

    image = cv2.imread(image_path)
    template = cv2.imread(template_path)

    print(type(image))
    
    # result = match_template(image, template)
    # print(result)
