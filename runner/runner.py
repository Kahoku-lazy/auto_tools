from app.ui_tools import UIModule
# from utils.log_modules import LogDriver
from utils.method import read_csv_as_dict

class Runner:

    def __init__(self):
        self._ui_tools = UIModule()

    def simulation_operation_running(self):

        test_case = read_csv_as_dict(self._ui_tools._config.get("case", "path"))
        for i in test_case:
            self._ui_tools.test_logs.info(f">>> 使用 {i['location_method']} 定位的方法实现 {i['action_type']} 元素 {i['action_value']}")
            self._ui_tools.simulation_operation(i["location_method"], i["action_type"], i["action_value"])
            self._ui_tools._u2.wait_seconds(2)

    def get_app_screenshot(self):
        """ 获取应用截图 """
        self._ui_tools._u2.get_screenshot(save_img=True)

    def run(self, count: int):
        for i in range(count):
            self.simulation_operation_running()