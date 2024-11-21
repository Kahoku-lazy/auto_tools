""" 
@ author: Kahoku
@ date: 2024/08
@ description:  图像识别算法
@update: 2024/11
@ version: 2.1
@ update:
    1. 增加了多尺度匹配算法
    2. 修改了返回值
    3. 修改了返回值的类型
"""

import cv2
import numpy as np

class TemplateMatcher:
    def __init__(self, method=cv2.TM_CCOEFF_NORMED):
        self.method = method

    def match(self,image, template):
        h, w = template.shape[:2]
        res = cv2.matchTemplate(image, template, self.method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if self.method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
        else:
            top_left = max_loc
        
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)

        x1, y1 = top_left
        x2, y2 = bottom_right
        return x1, y1, x2, y2
        # return image

class MultiScale:
    def __init__(self, scales=None):
        if scales is None:
            self.scales = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
        else:
            self.scales = scales

    def match(self, image, template, method=cv2.TM_CCOEFF_NORMED):
        template_h, template_w = template.shape[:2]
        best_loc = None
        best_scale = 1
        best_value = -1

        for scale in self.scales:
            resized = cv2.resize(template, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
            res = cv2.matchTemplate(image, resized, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                value = min_val
                loc = min_loc
            else:
                value = max_val
                loc = max_loc

            if value > best_value:
                best_value = value
                best_loc = loc
                best_scale = scale

        best_h, best_w = int(template_h * best_scale), int(template_w * best_scale)
        top_left = best_loc
        bottom_right = (top_left[0] + best_w, top_left[1] + best_h)
        cv2.rectangle(image, top_left, bottom_right, (255, 0, 0), 2)
        return top_left, bottom_right
        # return image

class SIFTFeatureMatcher:
    def __init__(self):
        self.sift = cv2.SIFT_create()

    def match(self, image, template):
        img1_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        img2_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        keypoints1, descriptors1 = self.sift.detectAndCompute(img1_gray, None)
        keypoints2, descriptors2 = self.sift.detectAndCompute(img2_gray, None)

        matcher = cv2.BFMatcher()
        matches = matcher.knnMatch(descriptors1, descriptors2, k=2)

        good = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good.append(m)

        if len(good) > 10:
            src_pts = np.float32([keypoints1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

            M, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
            h, w = template.shape[:2]
            pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, M)

            image = cv2.polylines(image, [np.int32(dst)], True, (0, 255, 255), 3, cv2.LINE_AA)
        points = np.int32(dst).flatten().tolist()
        y1, x1 = points[0:2]
        y2, x2 = points[4:6]
        return x1, y1, x2, y2


if __name__ == '__main__':

    # 加载图像和模板
    image = cv2.imread('screenshot.png')
    template = cv2.imread("template.jpg")
    
    # 创建对象并进行匹配
    template_matcher = TemplateMatcher()
    result = template_matcher.match(image.copy(), template)
    print(result)

