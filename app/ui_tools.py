""" 
@ author: Kahoku
@ date: 2024/08
@ description:  UI模块 业务功能
@update: 2024/11
"""

from pathlib import Path

from utils.ui_controller import AndroidDeviceUiTools
from utils.method import play_audio, read_yaml_as_dict, read_config, read_csv_as_dict
from utils.log_modules import LogDriver

CONFIG_PATH = "config/config.ini"

class UIModule:

    def __init__(self):
        
        self._config= read_config(CONFIG_PATH)

        self.action_list = self.get_section_name_values("action")    # 支持的动作列表: 点击/滑动/查找/等待
        self.location_method_list = self.get_section_name_values("location_method") # 支持的定位方式列表: 元素/文本/图片

        # UI 操作方法
        self._u2 = AndroidDeviceUiTools(self._config("OCR_Config", "language"))
        self.test_logs = LogDriver(self._config("Logs", "runner_log"))     # LogDriver 保持路径

    """ |------------------------------------ 功能： 配置信息处理 ----------------------------------| """
    def get_ui_icon_config(self):

        """ 获取UI界面图标的截图配置信息; 配置文件只支持两种格式： yaml和csv"""
        config_path = Path(self._config.get("ui_elements", "icon_config"))
        if not config_path.exists():
            raise FileNotFoundError("配置文件不存在")
        
        if config_path.suffix == ".yaml":
            return read_yaml_as_dict(config_path)
        
        if config_path.suffix == ".csv":
            return read_csv_as_dict(config_path)
        

    def get_section_name_values(self, section_name):
        """ 获取配置文件中section下的所有键值对,返回一个列表"""
        action = self._config.items(section_name)
        converted_list = [item for tuple_item in action for item in tuple_item]
        return converted_list            

    """ |----------------------------------------------------- 功能：异常处理 ---------------------------------------------------| """

    def _check_action_input(self, action_type):
        """ 检查用户输入的操作类型是否合法 """
        if action_type not in self.action_list:
            raise ValueError("请输入正确的操作方式")
        
    def _check_location_method_input(self, location_method):
        """ 检查用户输入的定位方式是否合法 """
        if location_method not in self.location_method_list:
            raise ValueError("请输入正确的定位方式")

    """ |---------------------------------------------------------- 功能: UI 动作 (模拟视觉) -------------------------------------------------------| """
    def click_action(self, element, element_type):

        element_type = element_type.lower()
        if element_type == "icon":      # icon 图标定位方式
            config = self.get_ui_icon_config()["ICON"]
            self._u2.airtest_init()
            self._u2.click_icon_air(config[element])

        elif element_type == "text":    # 文本定位方式
            self._u2.click_text_ocr(element)

        #  准备弃用 元素定位方式
        elif element_type == "xpath":
            config = self.get_ui_icon_config()["ELEMENTS"]
            self._u2.click_xpath_u2(config[element])

    def click_text_relative_location_action(self, element, x_axial, y_axial):
        """ 点击文本相对位置的元素 """
        self._u2.click_text_relative_location_ocr(element, x_axial, y_axial)

    def swipe_up_action(self, element, element_type):
        """ 向上滑动直至某个元素出现 """
        self._u2.sliding_search_element_android(element=element, element_type=element_type, direction="down")

    def swipe_down_action(self, element, element_type):
        """ 向下滑动直至某个元素出现 """
        self._u2.sliding_search_element_android(element=element, element_type=element_type, direction="up")

    def wait_element_action(self, element, seconds):
        """ 等待元素出现 """
        self._u2.wait_seconds(seconds)

    def wait_element_gone_action(self, element, seconds):
        """ 点击元素, 直至元素消失 """
        self._u2.wait_seconds(seconds)

    """ |------------------------------------ 页面功能实现: UI动作 (模拟人为操作) ----------------------------------| """
    
    def execute_action(self, action_type, action_value, element_type: str):
        """ 执行指定的操作，包括点击、滑动、查找等 """
        
        if action_type  == "click" or action_type == "点击":
            self.click_action(action_value, element_type)
        elif action_type == "向上滑动":
            self.swipe_up_action(action_value, element_type)
        elif action_type == "向下滑动":
            self.swipe_down_action(action_value, element_type)
        elif action_type  == "wait"  or action_type == "等待":
            self._u2.wait_seconds(int(action_value))


    """ |------------------------------------------------- 函数: 业务功能 实现 -------------------------------------------------------| """
    def simulation_operation(self, location_method, action_type, action_value):

        # 元素定位方式
        self._check_location_method_input(location_method)
        self._check_action_input(action_type)

        if location_method == "启动":
            self._u2.start_app(action_value)

        # 检测方式
        if location_method  == "icon" or location_method == "图片":
            self.execute_action(action_type, action_value, element_type="icon")
        elif location_method  == "element" or location_method == "元素":
            self.execute_action(action_type, action_value, element_type="xpath")
        elif location_method  == "text" or location_method == "文本":
            self.execute_action(action_type, action_value, element_type="text")




