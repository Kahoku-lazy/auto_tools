import sys
from pathlib import Path
ROOT = Path(__file__).parents
FILE = str(ROOT[1])
sys.path.append(FILE)

from utils.ui_controller import AirtestTools, UiAutomationTools
from utils.method import play_audio, read_yaml_as_dict, Utils

YANDEX_YAML_PATH = "config/yandex_element.yaml"
CONFIG_PATH = "config/yandex_config.ini"


class TestIntegration:

    def __init__(self) -> None:

        self.utils = Utils()
        # self.device = AirtestTools()
        

        self.elements = self.get_ui_elements(YANDEX_YAML_PATH)
        self.config = self.get_run_config(CONFIG_PATH)


    def get_ui_elements(self, yaml_path):
        return read_yaml_as_dict(yaml_path)
    

    def get_run_config(self, config_path):
        return self.utils.read_config(config_path)
    

    def xiaomi_home_login(self):
        u = UiAutomationTools()

        elements = self.elements["xiaomi_app_info"]

        u.start_app(elements["app_package_name"])
        u.wait_seconds(4)

        for key, value in elements["elements_zh"].items():

            print(f">>> 点击 {key}; element: {value}")
            if key == "输入账号":
                print(f'>>> 输入账号 {elements["userinfo"]["username"]}')
                u.input_text(value, elements["userinfo"]["username"])
                continue
            elif key == "输入密码":
                print(f'>>> 输入密码 {elements["userinfo"]["password"]}')
                u.input_text(value, elements["userinfo"]["password"])
                continue
            u.click_xpath(value)
            print(f">>> {key} Done")
            u.wait_seconds(2)
        
        u.wait_seconds(3)
        if u.element_wait_exist('//*[@text="登录"]', timeout=2):
            print("登陆失败")
        else:
            print("登陆成功")

        u.close_app("com.xiaomi.smarthome")


    def yandex_mijia_app(self):
        
        elements = self.elements["yandex_app_info"]
        u = AirtestTools()

        u.start_app(elements["app_package_name"])
        u.wait_seconds(10)

        for key, value in elements["icon_path"].items():
            print(f">>> 点击 {key}; element: {value}")
            u.click_icon(value)
            u.wait_seconds(5)
        
        u.keyevent_back()

        u.wait_seconds(5)
        u.close_app(elements["app_package_name"])
        

if __name__ == "__main__":

    # UI操作压测 50次左右 yandex app 脚本会出问题

    test = TestIntegration()
    for i in range(100):
        print(f">>>[{i+1}/100] 第{i+1}次测试 ")
        test.yandex_mijia_app()
