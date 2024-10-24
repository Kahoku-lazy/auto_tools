import requests
import time
import json
import os

from pathlib import Path

from utils.loger import LogDriver
from utils.config import Config

from utils.utils import capture_single_frame, write_csv_values,read_txt_values
from utils.confyui_workflow import CfUIWorkflow

class TestImgLE:

    def __init__(self):
        self.config = Config()

    def ai_sqs_request(self, image_url):

        config = self.config.get_ai_sqs_request_api_values()

        config["data"]["image_url"]  = image_url
        response = requests.post(config["url"], headers=config["headers"], data=json.dumps(config["data"]))
        return response

    def upload_image_to_url(self, image_path):

        config = self.config.get_upload_image_to_url_api_values()

        with open(image_path, 'rb') as file:
            config["files"]['file'] = file
            response = requests.post(config["url"], data=config["data"], files=config["files"])
            if response.status_code == 200:
                im_url = response.json().get("url", {})
                return im_url
            else:
                return None

    def image_classification(self, image_url):

        config = self.config.get_image_classify_api_values()
        config["data"]["text"] = image_url
        response = requests.post(config["url"], headers=config["headers"], data=json.dumps(config["data"]))
        if response.status_code == 200:
            return response.json().get("result", {}).get("complexity_level", {})
        else:
            return None
        
    def test_image_to_light_url(self, config, test_datasets_values):
        """ input image urls """
        # logging init
        log  = LogDriver(file_path=config["log_path"], logger_name="testing_logger")
        
        # test image url
        image_urls = test_datasets_values["image_url"].to_list()
        write_csv_values(config["csv_path"], ["image_url", "response_data", "result_save_path"])
        
        log.info("Start test")
        for i, im_url in enumerate(image_urls):
            log.info(f"[{i+1}/{len(image_urls)}] image url: {im_url}")
            response = self.ai_sqs_request(im_url)
            if response.status_code == 200:
                response_data = response.json().get('data', {})
                log.info(f"pixel map url: {response_data}")
                
                time.sleep(3)
                image_name = Path(im_url).with_suffix(".jpg").name
                output_path = os.path.join(config["img_result_path"], image_name)
                capture_single_frame(self.config.get_resp_img_url_values(), output_path, 350)
                log.info(f"camera image save path: {output_path}")
            
            else:
                log.error(f"response text {response.text}")
                response_data = None
                save_path = None
            
            write_csv_values(config["csv_path"], [im_url, response_data, image_name])

    def test_workflow_text_to_light(self):

        config = self.config.get_workflow_config_values()
        w = CfUIWorkflow(config["server_address"])
        prompts = read_txt_values(config["prompts_path"])
        for prompt in prompts:
            for i in range(5):
                w.run(config["workflow_json_path"], prompt)
                time.sleep(5)
                image_name = f"{i}_{prompt.rstrip()}.jpg"
                output_path = os.path.join(config["img_result_path"], image_name)
                if not Path(config["img_result_path"]).exists():
                    print(f'{config["img_result_path"]} not found')
                    return -1
                capture_single_frame(self.config.get_resp_img_url_values(), output_path, 350)

    def main(self):
        
        # test Dateset and run config
        test_datasets_values, config = self.config.test_image_to_light_config()

        if not Path(config["img_result_path"]).exists():
            os.mkdir(config["img_result_path"])

        self.test_image_to_light_url(config=config, test_datasets_values=test_datasets_values)



if __name__ == "__main__":
    tester = TestImgLE()
    tester.main()
    # tester.test_workflow_text_to_light()

