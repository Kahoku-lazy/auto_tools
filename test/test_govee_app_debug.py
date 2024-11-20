import sys
from pathlib import Path
ROOT = Path(__file__).parents
FILE = str(ROOT[1])
sys.path.append(FILE)

from utils.ui_controller import AndroidDeviceUiTools
from utils.method import play_audio, read_yaml_as_dict, read_config, read_csv_as_dict
from utils.log_modules import LogDriver

YANDEX_YAML_PATH = "config/yandex_element.yaml"
CONFIG_PATH = "config/yandex_config.ini"
# module_names = ['颜色', '场景', '照明', '音乐', '用户分享', 'DIY', "涂鸦", "AI", '更多']
# "com.govee.home"

class PageModules:

    def __init__(self):
        
        self._u2 = AndroidDeviceUiTools(ocr_language='ch')
        self.test_logs = LogDriver("runner/logs/test_logs.log")

        self._u2.airtest_init()

    def open_govee_app(self):
        self._u2.start_app()
        self._u2.wait_seconds(5)

    def icon_action(self, action_type, action_value):

        # 操作方式
        action = ["click", "is_exists", "swipe", "find", "点击", "是否存在", "滑动", "查找"]
        if action_type not in action:
            raise ValueError("请输入正确的操作方式")
        
        if action_type  == "click" or action_type == "点击":
            self._u2.click_icon_air(action_value)
        elif action_type  == "is_exists" or action_type == "是否存在":
            self._u2.is_icon_exist_air(action_value)
        elif action_type  == "swipe" or action_type == "滑动":
            pass
        elif action_type  == "find"  or action_type == "查找":
            pass

    def text_action(self, action_type, action_value):

        # 操作方式
        action = ["click", "is_exists", "swipe", "find", "点击", "是否存在", "滑动", "查找"]
        if action_type not in action:
            raise ValueError("请输入正确的操作方式")
        
        if action_type  == "click" or action_type == "点击":
            self._u2.click_text_ocr(action_value)
        elif action_type  == "is_exists" or action_type == "是否存在":
            # self._u2.is_icon_exist_air(action_value)
            pass
        elif action_type  == "swipe" or action_type == "滑动":
            pass
        elif action_type  == "find"  or action_type == "查找":
            pass

    def element_action(self, action_type, action_value):
        # 操作方式
        action_ch = ["点击", "是否存在", "滑动", "查找", "等待"] 
        action_en = ["click", "is_exists", "swipe", "find", "wait"]   
        action = action_ch + action_en
        if action_type not in action:
            raise ValueError("请输入正确的操作方式")
        
        if action_type  == "click" or action_type == "点击":
            self._u2.click_xpath_u2(action_value)
        elif action_type  == "is_exists" or action_type == "是否存在":
            # self._u2.is_icon_exist_air(action_value)
            pass
        elif action_type  == "swipe" or action_type == "滑动":
            pass
        elif action_type  == "find"  or action_type == "查找":
            pass
        elif action_type  == "wait"  or action_type == "等待":
            self._u2.wait_seconds(int(action_value))


    def simulation_operation(self, location_method, action_type, action_value):

        # 元素定位方式
        location_methods = ["icon", "element", "text", "图片", "元素", "文本"]      # []
        if location_method not in location_methods:
            raise ValueError("请输入正确的定位方式")
        
        # 检测方式
        if location_method  == "icon" or location_method == "图片":
            self.icon_action(action_type, action_value)
        elif location_method  == "element" or location_method == "元素":
            self.element_action(action_type, action_value)
        elif location_method  == "text" or location_method == "文本":
            self.text_action(action_type, action_value)

class TestCaseModules(PageModules):

    def test_simulation_operation(self):

        case = read_csv_as_dict("config/debug_case.csv")
        for i in case:
            self.test_logs.info(f">>> 使用 {i['location_method']} 定位的方法实现 {i['action_type']} 元素 {i['action_value']}")
            self.simulation_operation(i["location_method"], i["action_type"], i["action_value"])
            self._u2.wait_seconds(2)


if __name__ == '__main__':

    t = TestCaseModules()

    from time import sleep
    while True:
        t.test_simulation_operation()
        sleep(3)

