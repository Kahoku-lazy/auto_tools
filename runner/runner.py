""" 
@ author: Kahoku
@ date: 2024/08
@ description:  运行器
@update: 2024/11
"""

from app.android_tools import AndroidUiAction
# from utils.log_modules import LogDriver
from utils.method import read_csv_as_dict

class Runner:

    def __init__(self):
        
        self.action = AndroidUiAction()

    def simulation_operation_running(self):
        test_case = read_csv_as_dict(self.action._config.get("case", "path"))
        for i in test_case:
            self.action.test_logs.info(f">>> 使用 {i['location_method']} 实现 {i['action_type']} 元素 {i['action_value']}")
            self.action.simulation_operation(i["location_method"], i["action_type"], i["action_value"])
            self.action.wait_action(1)

    def run(self, count: int):
        for i in range(count):
            self.simulation_operation_running()