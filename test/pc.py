# appium + WinAppDriver + selenium
# 定位软件 inspect

import subprocess
import time
import pyautogui
import win32gui
import win32con
import os, cv2
import numpy as np

from utils.ui_detection_system import match_template

def rectangle_center(points: list):
    """ 计算由两个对角点定义的矩形的中心点坐标 """
    x1, y1, x2, y2 = [int(coordinate) for point in points for coordinate in point]
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    return (center_x, center_y)

def get_all_windows():
    """获取所有可见窗口的名称"""
    windows = []

    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd):
            hwnds.append(hwnd)
        return True

    win32gui.EnumWindows(callback, windows)
    return windows

def start_application(app_path):
    """启动指定的应用程序"""
    subprocess.Popen(app_path)  # 使用Popen启动应用

def get_window_rect(window_name):
    """获取指定窗口的矩形区域"""
    hwnd = win32gui.FindWindow(None, window_name)
    if not hwnd:
        raise Exception("未找到窗口: {}".format(window_name))
    rect = win32gui.GetWindowRect(hwnd)
    return rect

def screenshot_window(window_name, save_path):
    """截取指定窗口的截图并保存"""
    rect = get_window_rect(window_name)
    x1, y1, x2, y2 = rect
    screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
    screenshot.save(save_path)

def set_fullscreen(window_name):
    """将指定窗口设置为全屏"""
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd:
        # 获取屏幕分辨率
        screen_width = win32gui.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32gui.GetSystemMetrics(win32con.SM_CYSCREEN)
        
        # 设置窗口为全屏
        win32gui.MoveWindow(hwnd, 0, 0, screen_width, screen_height, True)
    else:
        print(f"未找到窗口: {window_name}")

def close_application(window_name):
    """关闭指定窗口"""
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd:
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

def pil_to_opencv(pil_image):
    # 将PIL图像转换为numpy数组
    open_cv_image = np.array(pil_image)

    # 检查图像模式并进行颜色空间转换
    if pil_image.mode == 'RGB':
        # OpenCV使用BGR格式，因此需要进行颜色转换
        open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
    elif pil_image.mode == 'RGBA':
        # 对于带有透明通道的图像
        open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGBA2BGRA)

    return open_cv_image

# import pyautogui
# import time

# # 等待几秒钟，以便用户可以切换到目标窗口
# time.sleep(5)

# # 获取当前鼠标位置
# current_position = pyautogui.position()
# print(f"当前鼠标位置: {current_position}")

# # 移动鼠标到指定位置（例如，(100, 200)）
# pyautogui.moveTo(100, 200, duration=1)  # duration为移动时间，单位为秒

# # 单击左键
# pyautogui.click()

# # 双击左键
# pyautogui.doubleClick()

# # 右键单击
# pyautogui.rightClick()

# 示例调用
if __name__ == "__main__":
    app_path = r"C:\Program Files\Govee\Govee Desktop\GoveeDesktop.exe"  # 替换为您要启动的应用路径
    window_name = "Govee Desktop"  # 替换为您要截取的窗口名称
    save_path = "screenshot.png"

    # windows = get_all_windows()
    # print(window_name)

    # def get_window_title(hwnd):
    #     """获取指定窗口句柄的标题"""
    #     return win32gui.GetWindowText(hwnd)
    
    # window_titles = [get_window_title(hwnd) for hwnd in windows]
    # print(window_titles)
    # # # 启动应用程序
    # start_application(app_path)
    
    # # 等待一段时间以确保应用程序完全启动
    # time.sleep(5)

    # 模拟按下F11键（通常用于浏览器全屏）
    # set_fullscreen(window_name)

    time.sleep(5)

    # 截取窗口截图
    # screenshot_window(window_name, save_path)
    # print(f"已保存截图到 {save_path}")

    screenshot = pyautogui.screenshot()
    print(type(screenshot))

    window_im = pil_to_opencv(screenshot)
    te_im = r"D:\Kahoku\auto_tools\111.png"
    template = cv2.imread(te_im)
    points = match_template(window_im, template)
    x, y = rectangle_center(list(points))
    print(points)

    # # 移动鼠标到指定位置（例如，(100, 200)）
    pyautogui.moveTo(x, y, duration=0.25)  # duration为移动时间，单位为秒

    # # 单击左键
    pyautogui.click()

    # 保存截图
    screenshot.save("screenshot_pyautogui.png")
    print("全屏截图已保存为 screenshot_pyautogui.png")

    # 关闭应用程序
    # close_application(window_name)

from pywinauto import Application

# 启动记事本
app = Application().start('notepad.exe')

# 启动微信
app1 = Application().start(r'C:\Program Files (x86)\Tencent\WeChat\WeChat.exe')

# 启动迅雷
app2 = Application().start(r'C:\Program Files (x86)\Thunder Network\Thunder\Program\ThunderStart.exe')
