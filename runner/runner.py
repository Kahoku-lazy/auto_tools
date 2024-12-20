""" 
@ author: Kahoku
@ date: 2024/08
@ description:  运行器
@update: 2024/11
"""
from runner.config import Config

from utils.ui_action_driver import AndroidDriver, WindowsDriver, UiActionDriver
from utils.utils import LogDriver, SerialModules

class Runner(Config):
    def __init__(self):
        super().__init__()
        """
        @ param: drive: UI控件操作驱动
        @ param: ocr_language: OCR 识别语言
        @ param: icon_crops: icon 截图路径路径路径
        @ param: logdriver: 日志驱动
        """
        # UI 控件操作方法
        driver = AndroidDriver()   # Android UI 操作方法
        self._action = UiActionDriver(driver, ocr_language=self.ocr_language)

        # 运行日志
        self.logs = LogDriver(self.test_case_log_path,  # 测试用例保存日志 
                                logger_name="runner", console_printing=True)   
        
    def get_action_value(self, element, type):
        if type == "image":
            value = self.icon_crops[element]
        elif type == "text":
            value= element
        
        return value
    
    def execute_action(self, action_method, value, value_type):
        """ 执行指定的操作，包括点击、滑动、查找等 
        args:
            action_moethod: 操作方法
                |-- 点击、滑动、查找等 
            value:  元素
                |-- 点击的元素、滑动的距离等
            value_type: 元素类型
                |-- 图片、文本、坐标等
        """

        # 适配操作的值; 例如 文本是字符串， 图片是图片路径，控件是定位元素
        element = self.get_action_value(value, value_type)  

        # UI操作方法    
        args = {"element": element, "element_type": value_type}           
        add_to_dict = lambda d, k, v: {**d, k: v}
        action_methods = {
            "点击": ["click_action", args],
            "向上滑动": ["swipe_action", add_to_dict(args, "direction", "up")],
            "向下滑动": ["swipe_action", add_to_dict(args, "direction", "down")],
            "等待": ["wait_seconds", {"seconds": element}],
            "输入文本": ["input_text", {"text": element}],
            "文本断言": ["assert_text_action", {"text": element}]
        }

        # 执行操作
        method = getattr(self._action, action_methods[action_method][0], lambda x, y: "None")
        result = method(**action_methods[action_method][1])

        return result

    def simulation_operation(self, location_method_name, action_type, action_value):
        """ 执行测试用例  """

        # 支持的操作类型
        location_method = {"图片": "image", "文本": "text", "元素": "xpath"}
        
        self.execute_action(action_type, action_value, location_method[location_method_name])
        self._action.wait_seconds(1)

        # |******  待优化 *******|
        if location_method == "启动":
            self._android.start_app(action_value)
        elif location_method == "关闭":
            self._android.close_app(action_value)
    
    def run(self):
        """ 循环运行测试用例 """
        test_set, count = self.get_test_case_config()
        for _ in range(count):
            for test_case in test_set:
                for i in test_case:
                    self.logs.info(f"{i['location_method']} 操作方法 {i['action_type']} {i['action_value']}")
                    self.simulation_operation(i["location_method"], i["action_type"], i["action_value"])

def get_device_serial_logs():
    """ 获取设备串口日志 """
    # SerialModules(CONFIG).main()
    pass

def run_case():
    """ 运行测试用例 """
    Runner().run()
    pass