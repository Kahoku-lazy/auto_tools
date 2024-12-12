# auto_tools App UI 自动化代码

## 原理简介（草稿）
1. 实时获取手机屏幕内容，使用OpenCV算法与ocr模型识别图片内容。
2. 获取算法与模型的返回信息（坐标）， 使用 U2模块 操作手机
3. 读取CSV内容用例, 配合config里的配置参数执行点击、滑动、输入等操作。
4. 串口日志模块: 监控日志，抓取关键字信息并返回。

## 代码框架
1. app
    - Android 驱动器： 在安卓手机上套用 OCR与图像检测
    *待更新*
    - Ios 驱动器： 在苹果手机上套用CR与图像检测
    - PC 驱动器： 在电脑上套用CR与图像检测
2. case
    - 测试用例存放位置
3. config
    - 配置文件
4. runner
    - 日志 报告 表格 图表 存放点
    - 运行方法
5. test
    - 调试代码
6. utils
    - 基本方法；不含业务逻辑
7. main.py
    - 唯一运行入口


## 核心代码部分（草稿）
    1. uiatutomator2 模拟器操作
    2. opencv 图片识别
    3. 飞桨OCR 文字识别工具
    ** 替换方案 **
    1. wd14-tagger-standalone
    2. OmniParser

## 用例模版: csv文件
    ```csv
    location_method,action_type,action_value
    文本,点击,1
    元素,等待,2
    文本,向上滑动,3
    元素,等待,3
    ```

## 配置文件模板：yaml文件
    ```yaml
    TEXT:   
        - "以下为text元素信息"

    ICON:
        - "以下为icon图片路径信息"
    
    ELEMENTS:
        - "以下为xpath定位元素图片路径信息（默认只支持xpath）"
    ```
#  运行方式（草稿）
    1. python main.py
    2. 参数解析
        略过
    3. 运行
        略过

# 部分代码简介

## 一. UI 操作部分：detection_system.py

    1. UIDetectionSystem: UI页面检测
        - find_image_coordinates: OpenCV 图像匹配算法配对图片，返回矩形对角点坐标
        - find_text_coordinates: OCR 查找文字 返回矩形对角点坐标

    2. AndroidDeviceUiTools: Android UI界面控制
        - start_app： 启动APP
        - close_app: 关闭APP
        - wait_seconds： 等待
        - click_image: 点击图片
        - click_text：点击文字
        - click_relative_location：以文字或图片为参考点，点击附近相对坐标
        - sliding_search_element： 上下滑动，直到指定的文字或图片出现。
        - input_text: 输入文本
        - get_screenshot: 获取屏幕截图

    3. IOSDeviceUiTools: iPhone UI界面控制
        - 待更新

## 二、用例执行部分：android_tools.py
    1. AndroidUiAction: 安卓手机操作方法
        - get_ui_icon_config： 获取用例与配置
        - execute_action： 执行指定的操作，包括点击、滑动、查找等
        - simulation_operation：读取用例步骤，并执行