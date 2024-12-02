# auto_tools App UI 自动化代码

## 原理简介（草稿）
1. 实时获取手机屏幕内容，使用OpenCV算法与ocr模型识别图片内容。
2. 获取算法与模型的返回信息（坐标）， 使用 U2模块 操作手机
3. 读取CSV内容用例, 配合config里的配置参数执行点击、滑动、输入等操作。
4. 串口日志模块: 监控日志，抓取关键字信息并返回。

## 核心代码部分（草稿）
    1. uiatutomator2 模拟器操作
    2. opencv 图片识别
    3. 飞桨OCR 文字识别工具
    ** 替换方案 **
    1. wd14-tagger-standalone
    2. OmniParser

## 用例模版
    ``` csv
    location_method,action_type,action_value
    文本,点击,1
    元素,等待,2
    文本,向上滑动,3
    元素,等待,3
    ```

## 配置目标
    ``` yaml
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
