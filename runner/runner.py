""" 
@ author: Kahoku
@ date: 2024/08
@ description:  运行器
@update: 2024/11
"""
from app.android_tools import AndroidUiAction
from utils.utils import read_csv_as_dict

class Runner:

    def __init__(self, config):

        self.config = config
        self.action = AndroidUiAction(config)

    def simulation_operation_running(self):

        test_case = read_csv_as_dict(self.action._config.get("case", "path"))
        
        for i in test_case:
            self.action.test_logs.info(f"{i['location_method']} 操作方法 {i['action_type']} {i['action_value']}")
            self.action.simulation_operation(i["location_method"], i["action_type"], i["action_value"])

    def run(self):

        count = self.config.getint("case", "count")
        for i in range(count):
            self.simulation_operation_running()