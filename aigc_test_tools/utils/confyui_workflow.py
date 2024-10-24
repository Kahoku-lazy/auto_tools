import websocket
import uuid
import json
import urllib.request
import urllib.parse
import random

class CfUIWorkflow:

    def __init__(self, server_address):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())

        # connect server
        self.ws = websocket.WebSocket()
        self.ws.connect(f"ws://{self.server_address}/ws?clientId={self.client_id}")

    def _queue_prompt(self, prompt):
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def _get_image(self, filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen(f"http://{self.server_address}/view?{url_values}") as response:
            return response.read()

    def _get_history(self, prompt_id):
        with urllib.request.urlopen(f"http://{self.server_address}/history/{prompt_id}") as response:
            return json.loads(response.read())

    def _get_images(self, ws, prompt):
        prompt_id = self._queue_prompt(prompt)['prompt_id']
        output_images = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break
        history = self._get_history(prompt_id)[prompt_id]
        for o in history['outputs']:
            for node_id in history['outputs']:
                node_output = history['outputs'][node_id]
                images_output = []
                if 'images' in node_output:
                    for image in node_output['images']:
                        image_data = self._get_image(image['filename'], image['subfolder'], image['type'])
                        images_output.append(image_data)
                output_images[node_id] = images_output
        return output_images
    
    def _read_workflow_json_values(self, workflow_json):
        with open(workflow_json) as f:
            return json.load(f)

    def run(self, workflow_json, prompts_txt):

        prompt = self._read_workflow_json_values(workflow_json)
        prompt["6"]["inputs"]["text"] = f'{prompts_txt.strip()}, {prompt["6"]["inputs"]["text"]}'
        random_number = random.randint(1000, 9999)
        prompt["25"]["inputs"]["noise_seed"] = random_number
        self._get_images(self.ws, prompt)

