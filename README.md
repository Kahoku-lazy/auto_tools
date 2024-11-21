# auto_tools App UI 自动化代码

## 简介
1. 使用 图像识别的方法 做UI自动化测试


## 代码部分
- uiatutomator2 模拟器操作
    抓取定位元素工具下载地址: URL: https://uiauto.dev/
    1. 安装: pip3 install -U uiautodev -i https://pypi.doubanio.com/simple
    2. 运行: uiauto.dev  or python3 -m uiautodev

    -- airtest 图片点击方法: https://github.com/AirtestProject/Airtest
    1. api 教程： https://airtest.readthedocs.io/en/latest/all_module/airtest.core.api.html

    -- OmniParser AI模型 UI识别工具: https://github.com/microsoft/OmniParser
    1. 模型库：https://huggingface.co/spaces/microsoft/OmniParser

    omniparser.py

    多模型备选方案: ollama, 优势: 多模型且可本地部署，离线服务

    -- PaddleOCR 文字识别工具: https://github.com/PaddlePaddle/PaddleOCR
    https://paddlepaddle.github.io/PaddleOCR/latest/paddlex/quick_start.html#python
    --- 备选方案: CnOcr
    -- Poco 多平台:    https://poco.readthedocs.io/en/latest/source/poco.sdk.html
    from poco.drivers.android.uiautomation import AndroidUiautomationPoco

    self._poco = AndroidUiautomationPoco()
    self._poco(xpath=element_xpath).wait(timeout=timeout).click()
    
功能：
    1. PP-OCR: https://paddlepaddle.github.io/PaddleOCR/latest/ppocr/infer_deploy/python_infer.html#1
    2. Airtest 图片点击方法:
        -- TemplateMatching
        -- MultiScaleTemplateMatchingPre
        -- SIFTMatching


        -- 识别方法:
        1. MultiScaleTemplateMatchingPre, 
        2. TemplateMatching, 
        3. SURFMatching, 
        4. BRISKMatching, 
        5. MultiScaleTemplateMatchingPre, 
        6. TemplateMatching
        MultiScaleTemplateMatchingPre 、 
        TemplateMatching 、 SURFMatching 
        和 BRISKMatching
        -- 问题： 半透明或透明背景识别率低， 当前可实践的替代方案: YOLO;  备选方案: OmniParser
    3. Poco 多平台（游戏类优先选择）
    4. 飞桨OCR 文字识别工具


## 收藏
1. wd14-tagger-standalone
2. OmniParser