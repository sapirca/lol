import json

from animation.frameworks.kivsee.kivsee_sequence import KivseeSequence
from animation.frameworks.kivsee.scheme.effects_scheme import KivseeSchema
import requests

# Kivsee-sapir IP 10.0.1.204
# VNC Viewer, host 10.0.1.204, username pi, password kivsee12
# pi@raspberrypi
# kivsee12

# 10.0.0.36

# SEQUENCE_URL = "http://10.0.0.49:8082"
# TRIGGER_URL = "http://10.0.0.49:8083"
# all_elements = [
#     "ring1", "ring2", "ring3", "ring4", "ring5", "ring6", "ring7", "ring8",
#     "ring9", "ring10", "ring11", "ring12"
# ]

SEQUENCE_URL = "http://10.0.0.36:8082"
TRIGGER_URL = "http://10.0.0.36:8083"
all_elements = ["ring0"]


class Render:

    def __init__(self):
        self.sequence_manager = KivseeSequence()

    def store_animation(self, animation_data):
        # Stub method to send a POST request to store the animation
        # TOOD(sapir): update name
        # url = f"{SEQUENCE_URL}/triggers/{animation_data['name']}"
        # payload = {element_name: animation_data["animation"]}
        # response = self._put_request(url, payload)
        # # save guid
        # print(
        #     f"Store animation response: {response.status_code}, {response.text}"
        # )

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
        # Stub method to send a POST request to trigger the song
        url = f"{TRIGGER_URL}/song/{animation_data['name']}/play"
        payload = {"animation_data": animation_data}
        response = self._post_request(url, payload)
        print(
            f"Trigger song response: {response.status_code}, {response.text}")

    def _put_request(self, url, payload):
        # Helper method to send a PUT request
        headers = {"Content-Type": "application/json"}
        response = requests.put(url, json=payload, headers=headers)
        return response

    def _post_request(self, url, payload):
        # Helper method to send a POST request
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        return response

    def load_and_print_animation(self):
        # Get the path to the animation file
        animation_file_path = self.sequence_manager.get_animation_filename()

        # Open and load the JSON file
        with open(animation_file_path, 'r') as file:
            animation_data = json.load(file)

        # Print all fields in the JSON
        for key, value in animation_data.items():
            print(f"{key}: {value}")

        self.preprocess_animation(animation_data)
        # Convert the animation data to proto using model_validate
        # response_proto = KivseeSchema.model_validate(animation_data)

        # Store the animation data
        self.store_animation(animation_data)

        # Trigger the song
        animation_data['name'] = "aladdin"
        self.trigger_song(animation_data)

        # animation_data['name'] = "test_123"
        # self.trigger_animation(animation_data)

    def preprocess_animation(self, animation_data):
        for effect in animation_data.get("effects", []):
            print(f"Effect: {effect}")


def main():
    render = Render()
    render.load_and_print_animation()


if __name__ == "__main__":
    main()

# Speaker
# 1. Understand aladdin notes
# 2. synchronize with the right miliseconds
# 3. beats - millis
# 4. add offset

# Proto not readable?
# Make animation beautiful
# Surpises - in the right part of song
# what is the line that connects the story
# Either have the same color between the two parts or have a line that connects them
# Need to have animation of the song
