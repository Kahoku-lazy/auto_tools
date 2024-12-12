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

from app.detection_system import Action
from utils.utils import read_yaml_as_dict, LogDriver

from app.windows_tools import WindowsDeviceUiTools

class AndroidUiAction:

    def __init__(self, config):

        self._config = config

        # device = u2.connect()   # Android UI 操作方法
        device = WindowsDeviceUiTools()  # windows UI 操作方法
        self._drive = device
        self._ocr_language = self._config.get("case", "ocr_language")

        self._action = Action(self._drive, ocr_language=self._ocr_language)
        

        self.action_list = self.get_section_name_values("action")    # 支持的动作列表: 点击/滑动/查找/等待
        self.location_method_list = self.get_section_name_values("location_method") # 支持的定位方式列表: 元素/文本/图片

        self.test_logs = LogDriver(self._config.get("Logs", "test_case_run"), "uiAction")    

    """ |------------------------------------ 功能： 配置信息处理 ----------------------------------| """
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
    
    def get_section_name_values(self, section_name):
        """ 获取配置文件中section下的所有键值对 """
        action = self._config.items(section_name)
        converted_list = [item for tuple_item in action for item in tuple_item]
        return converted_list            

    """ |----------------------------------------------------- 功能：异常处理 ---------------------------------------------------| """

    def _check_action_input(self, action_type):
        """ 检查用户输入的操作类型是否合法 """
        if action_type not in self.action_list:
            raise ValueError(f"不支持 {action_type} 操作")
        
    def _check_location_method_input(self, location_method):
        """ 检查用户输入的定位方式是否合法 """
        if location_method not in self.location_method_list:
            raise ValueError(f"不支持 {location_method} 定位方法")


    """ |------------------------------------ 页面功能实现: UI动作 (模拟人为操作) ----------------------------------| """
    
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
        element_type = element_type.lower()
        element = self.get_element_config(action_value, element_type)
        args = {"element": element, "element_type": element_type}

        if action_type  == "click" or action_type == "点击":
            method_name = "click_action"
            args = {"element": element, "element_type": element_type}
        
        elif action_type == "向上滑动":
            method_name = "swipe_action"
            args["direction"] =  "up"

        elif action_type == "向下滑动":
            method_name = "swipe_action"
            args["direction"] =  "down"

        elif action_type  == "wait"  or action_type == "等待":
            method_name = "wait_seconds"
            del args["element"]
            del args["element_type"]
            args["seconds"] = int(element)

        elif action_type == "输入文本":
            method_name = "input_text"
            del args["element"]
            del args["element_type"]
            args["text"] = element
        
        else:
            method_name = "None"

        method = getattr(self._action, method_name, lambda x, y: "None")
        result = method(**args)



    """ |------------------------------------------------- 函数: 业务功能 实现 -------------------------------------------------------| """
    def simulation_operation(self, location_method, action_type, action_value):

        # 检测用例输入数据是否合法
        self._check_location_method_input(location_method)
        self._check_action_input(action_type)

        if location_method == "启动":
            self._android.start_app(action_value)
        elif location_method == "关闭":
            self._android.close_app(action_value)

        # 检测方式
        if location_method == "图片":
            element_type="image"
        elif location_method == "文本":
            element_type="text"
        elif location_method == "元素":
            element_type="xpath"
        else:
            return
        
        self.execute_action(action_type, action_value, element_type=element_type)
        self._action.wait_seconds(1)




