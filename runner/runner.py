""" 
@ author: Kahoku
@ date: 2024/08
@ description:  运行器
@update: 2024/11
"""
from app.ui_action import UiAction
from utils.utils import read_csv_as_dict

from utils.utils import SerialModules, read_config

class Runner:

    def __init__(self, config):

        self.config = config
        self.action = UiAction(config)     #  UI 操作模块

    def simulation_operation_running(self):
        """ 执行测试用例中的步骤；点击、滑动、拖动等方式操作UI元素， 输入文本等"""
        test_case = read_csv_as_dict(self.action._config.get("case", "path"))
        
        for i in test_case:
            self.action.test_logs.info(f"{i['location_method']} 操作方法 {i['action_type']} {i['action_value']}")
            self.action.simulation_operation(i["location_method"], i["action_type"], i["action_value"])

    def run(self):
        """ 循环运行测试用例 """
        count = self.config.getint("case", "count")  # 循环次数；config配置文件中配置。
        for _ in range(count):
            self.simulation_operation_running()


# 读取配置文件； 串口配置 与 测试用例配置
CONFIG_PATH = "config.ini"
CONFIG = read_config(CONFIG_PATH)

def get_device_serial_logs():
    """ 获取设备串口日志 """
    SerialModules(CONFIG).main()

def run_case():
    """ 运行测试用例 """
    Runner(CONFIG).run()