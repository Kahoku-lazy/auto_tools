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

class YandexPage:

    def __init__(self) -> None:

        self._ui = AndroidDeviceUiTools()

        self._elements = self._get_ui_elements(YANDEX_YAML_PATH)
        self._config = self._get_run_config(CONFIG_PATH)

        self.yandex_logs = LogDriver(file_path=self._config.get("Logging", "path"))


    def _get_ui_elements(self, yaml_path):
        return read_yaml_as_dict(yaml_path)
    
    def _get_run_config(self, config_path):
        return read_config(config_path)
    
    def get_audio_text_dict(self):
        values = read_csv_as_dict(self._config.get("Audio_Text", "path"))
        return values
    
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
        # UI操作压测 50次左右 yandex app 脚本会出问题
        elements = self.elements["yandex_app_info"]

        self._ui.airtest_init()

        self._ui.start_app(elements["app_package_name"])
        self._ui.wait_seconds(10)

        for key, value in elements["icon_path"].items():
            print(f">>> 点击 {key}; element: {value}")
            self._ui.click_icon_air(value)
            self._ui.wait_seconds(5)
        
        self._ui.keyevent_back_air()

        self._ui.wait_seconds(5)
        self._ui.close_app(elements["app_package_name"])
        

class TestIntegration(YandexPage):

    def test_input_audio_command(self):
        """  yandex Alice: 在指定界面测试: 在输入框发送文本指令(语音文本)控制设备。
        """
        self._ui.airtest_init()  # 初始化airtest

        # 准备测试数据
        audio_texts = self.get_audio_text_dict()
        elements = self._elements["yandex_app_info"]["alice_page_elements"]
        
        # 进入Alice页面
        self._ui.click_icon_air(self._elements["yandex_app_info"]["main_page_icon"]["alice_icon"])
        self._ui.wait_seconds(2)

        # 开始发送语音文本指令
        for i, value in enumerate(audio_texts):
            self.yandex_logs.info(f">>>[俄语指令]: {i+1} / {len(audio_texts)} send command: {value['俄语命令']}")
            self.yandex_logs.info(f">>>[中文翻译]: 中文翻译:  {value['中文命令']}")
            command = value['俄语命令']

            if not self._ui.input_text(elements["text_field_element"], command):
                self.yandex_logs.error(">>>[元素定位错误] 文本输入框定位元素找不到 !!!!")
                self.yandex_logs.error(">>>[执行结果] Fail.")
                self._ui.wait_seconds(0.5)

            self._ui.click_xpath_u2(elements["send_button_element"])
            self._ui.wait_seconds(6)
            self.yandex_logs.info(">>>[执行结果] Done.")
            
        self._ui.wait_seconds(4)
        self._ui.keyevent_back_u2()


if __name__ == "__main__":
    p = YandexPage()


    test = TestIntegration()

    test.test_input_audio_command()













# if __name__ == "__main__":


