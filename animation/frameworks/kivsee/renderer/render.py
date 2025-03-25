import json

from animation.frameworks.kivsee.kivsee_sequence import KivseeSequence
from animation.frameworks.kivsee.scheme.effects_scheme import KivseeSchema
import requests

BASE_URL = "http://10.45.0.0"


class Render:

    def __init__(self):
        self.sequence_manager = KivseeSequence()

    def store_animation(self, animation_data):
        # Stub method to send a POST request to store the animation
        url = f"{BASE_URL}/store-animation"
        payload = {"animation_data": animation_data}
        response = self._post_request(url, payload)
        print(
            f"Store animation response: {response.status_code}, {response.text}"
        )

    def trigger_song(self, animation_data):
        # Stub method to send a POST request to trigger the song
        url = f"{BASE_URL}/trigger-song"
        payload = {"animation_data": animation_data}
        response = self._post_request(url, payload)
        print(
            f"Trigger song response: {response.status_code}, {response.text}")

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

        # Convert the animation data to proto
        response_proto = KivseeSchema(response=animation_data)

        # Store the animation data
        self.store_animation(response_proto)

        # Trigger the song
        self.trigger_song(response_proto)


def main():
    render = Render()
    render.load_and_print_animation()


if __name__ == "__main__":
    main()
