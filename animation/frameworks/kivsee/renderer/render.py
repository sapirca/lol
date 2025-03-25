import json

from animation.frameworks.kivsee.kivsee_sequence import KivseeSequence
from animation.frameworks.kivsee.scheme.effects_scheme import KivseeSchema


class Render:

    def __init__(self):
        self.sequence_manager = KivseeSequence()

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

        # >>> duplicate it for all things names and do http post to the trigger service
        # request = {
        #     "trigger": "animation",
        #     "animation": animation_data
        # }
        # >>> duplicate it for all things names and do http post to the trigger service
        # request = {
        #     "trigger": "animation",
        #     "animation": animation_data
        # }
        # send request to trigger service
        # response = requests.post("http://trigger-service:5000/trigger", json=request)
        # print
        # print(response.json())
        # except requests.exceptions.RequestException as e:
        #     print(f"Error sending request to trigger service: {e}")


def main():
    render = Render()
    render.load_and_print_animation()


if __name__ == "__main__":
    main()
