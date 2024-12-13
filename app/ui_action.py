""" 
@ author: Kahoku
@ date: 2024/08
@ description:  安卓手机 UI模块 业务功能
@update: 2024/12
@ version: 3.1
    1. 优化： 使用 getattr 方法重构了一下代码
    2  优化了 实参与形参的传参逻辑
"""
from pathlib import Path
import uiautomator2 as u2

from app.android_tools import AndroidUiAction
from utils.utils import LogDriver, read_yaml_as_dict, read_config, get_section_name_values

from app.windows_tools import WindowsDeviceUiTools

class UiAction:

    def __init__(self, config):

        self._config = config

        device = u2.connect()   # Android UI 操作方法
        # device = WindowsDeviceUiTools()  # windows UI 操作方法

        self._drive = device
        self._ocr_language = self._config.get("case", "ocr_language")
        self._action = AndroidUiAction(self._drive, ocr_language=self._ocr_language)
        
        # 支持的动作列表
        self.action_list = get_section_name_values(self._config.get("UiConfig", "check_config"), "action")    
        # 支持的识别方法
        self.location_method_list = get_section_name_values(self._config.get("UiConfig", "check_config"), "location_method") 

        self.test_logs = LogDriver(self._config.get("Logs", "test_case_run"), "uiAction")    

    def get_ui_config(self):
        config_path = Path(self._config.get("UiConfig", "path"))

        if not config_path.exists():
            raise FileNotFoundError("配置文件不存在")

        elif config_path.suffix == ".yaml":
            values = read_yaml_as_dict(config_path)
            
        return values
    
    def get_element_config(self, element, type):
        if type == "image":
            config = self.get_ui_config()["ICON"]
            return config[element]
        elif type == "text":
            return element
        elif type == "xpath":
            self.get_ui_config()["ELEMENTS"]
            return config[element]     
    
    def check_case_input(self, action_type, location_method):
        """ 检查用户输入的操作类型是否合法 """
        if action_type not in self.action_list:
            raise ValueError(f"不支持 {action_type} 操作方法")
        if location_method not in self.location_method_list:
            raise ValueError(f"不支持 {location_method} 识别方法")
    
    def execute_action(self, action_type, action_value, element_type: str):
        """ 执行指定的操作，包括点击、滑动、查找等 
        args:
            action_type: 操作类型，
                |-- 点击、滑动、查找等 
            action_value:  操作的值
                |-- 点击的元素、滑动的距离等
            element_type: 元素的类型
                |-- 图片、文本、坐标等
        """

        # 适配操作的值; 例如 文本是字符串， 图片是图片路径，控件是定位元素
        # element_type = element_type.lower()
        # 操作元素
        element = self.get_element_config(action_value, element_type)   
        # 操作方法    
        args = {"element": element, "element_type": element_type}           
        add_to_dict = lambda d, k, v: {**d, k: v}

        action_method = {
            "点击": ["click_action", args],
            "向上滑动": ["swipe_action", add_to_dict(args, "direction", "up")],
            "向下滑动": ["swipe_action", add_to_dict(args, "direction", "down")],
            "等待": ["wait_seconds", {"seconds": element}],
            "输入文本": ["input_text", {"text": element}],
        }

        method = getattr(self._action, action_method[action_type][0], lambda x, y: "None")
        result = method(**action_method[action_type][1])

        return result

    def simulation_operation(self, location_method_name, action_type, action_value):
        """ 执行测试用例  """
        # 检测用例输入数据是否合法
        self.check_case_input(action_type, location_method_name)

        location_method = {"图片": "image", "文本": "text", "元素": "xpath"}
        
        self.execute_action(action_type, action_value, location_method[location_method_name])
        self._action.wait_seconds(1)

        # |******  待优化 *******|
        if location_method == "启动":
            self._android.start_app(action_value)
        elif location_method == "关闭":
            self._android.close_app(action_value)




