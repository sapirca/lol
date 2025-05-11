import json

from animation.frameworks.kivsee.kivsee_sequence import KivseeSequence

import requests

# Kivsee-sapir IP 10.0.1.204
# VNC?
# 10.0.0.36
# pi@raspberrypi
# kivsee12

# SEQUENCE_URL = "http://10.0.0.49:8082"
# TRIGGER_URL = "http://10.0.0.49:8083"
# all_elements = [
#     "ring1", "ring2", "ring3", "ring4", "ring5", "ring6", "ring7", "ring8",
#     "ring9", "ring10", "ring11", "ring12"
# ]

RASPBERRY_PI_IP = "192.168.1.27"
SEQUENCE_URL = f"http://{RASPBERRY_PI_IP}:8082"
TRIGGER_URL = f"http://{RASPBERRY_PI_IP}:8083"
all_elements = ["ring0"]


class Render:

    def __init__(self):
        self.sequence_manager = KivseeSequence()

    def store_animation(self, animation_data: dict):
        # Stub method to send a POST request to store the animation
        # TOOD(sapir): update name
        # url = f"{SEQUENCE_URL}/triggers/{animation_data['name']}"
        # payload = {element_name: animation_data["animation"]}
        # response = self._put_request(url, payload)
        # # save guid
        # print(
        #     f"Store animation response: {response.status_code}, {response.text}"
        # )

        # try:
        #     animation_data = json.loads(animation_data)
        # except json.JSONDecodeError as e:
        #     raise(f"Error decoding JSON: {e}")

        animation_data['name'] = "aladdin"

        for element_name in all_elements:
            url = f"{SEQUENCE_URL}/triggers/{animation_data['name']}/objects/{element_name}"
            payload = animation_data["animation"]
            response = self._put_request(url, payload)
            # save guid
            print(
                f"Store animation response: {response.status_code}, {response.text}"
            )

    def trigger_animation(self, animation_data):
        # Stub method to send a POST request to trigger the song
        # TODO(sapir): ask amir how to send to more than one element
        url = f"{TRIGGER_URL}/trigger/{animation_data['name']}"
        print(f"url: {url}")
        # payload = {"sequence_guid": "{guid}",
        #            "start_offset_ms": 5000}
        response = self._post_request(url, {})
        print(
            f"Trigger song response: {response.status_code}, {response.text}")

    def trigger_song(self, animation_data):
        url = f"{TRIGGER_URL}/song/{animation_data['name']}/play"
        payload = {"animation_data": animation_data}
        response = self._post_request(url, payload)
        print(
            f"Trigger song response: {response.status_code}, {response.text}")

    def _put_request(self, url, payload):
        headers = {"Content-Type": "application/json"}
        response = requests.put(url, json=payload, headers=headers)
        return response

    def _post_request(self, url, payload):
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        return response

    def load_and_print_animation(self):
        animation_file_path = self.sequence_manager.get_animation_filename()
        with open(animation_file_path, 'r') as file:
            animation_data = json.load(file)
        self.render(animation_data)

    def render(self, animation_data):
        print("Rendering animation...")
        self.store_animation(animation_data)
        self.trigger_animation(animation_data)
        self.trigger_song(animation_data)

    def preprocess_animation(self, animation_data):
        effects = animation_data.get("effects", [])
        if effects.__len__() > 0:
            print(f"Effects len: {effects.__len__()}")
        else:
            print("No effects found in the animation data.")
