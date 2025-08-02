import json
import requests
from animation.frameworks.kivsee.kivsee_sequence import KivseeSequence
import os
from datetime import datetime
from pathlib import Path
import base64
from animation.frameworks.kivsee.renderer.proto.effects_pb2 import AnimationProto
from animation.frameworks.kivsee.renderer.proto.stats_request import RING_OBJECT_PROTO
from constants import ANIMATION_OUT_TEMP_DIR, SNAPSHOTS_DIR

from google.protobuf.json_format import ParseDict

# Kivsee-sapir IP 10.0.1.204
# VNC?
# 10.0.0.36
# pi@raspberrypi
# kivsee12

# RASPBERRY_PI_IP = "192.168.1.12"
# RASPBERRY_PI_IP = "192.168.1.27"
# RASPBERRY_PI_IP = "10.100.102.30"

# RASPBERRY_PI_IP = "10.0.1.204"
RASPBERRY_PI_IP = "10.100.102.30"
SEQUENCE_URL = f"http://{RASPBERRY_PI_IP}:8082"
TRIGGER_URL = f"http://{RASPBERRY_PI_IP}:8083"
SIMULATION_URL = f"http://{RASPBERRY_PI_IP}:8084"
OBJECT_URL = f"http://{RASPBERRY_PI_IP}:8081"


# Get and print the content of the specified URL
def get_url_content(url):
    try:
        print(f"Fetching content from URL: {url}")
        response = requests.get(url)
        print(f"Status code: {response.status_code}")
        print("Content:")
        print(response.text)
    except Exception as e:
        print(f"Error fetching URL content: {e}")

GET_OBJECT_URL = f"{OBJECT_URL}/thing/{{thing_name}}"
GET_ANIMATION_URL = f"{SEQUENCE_URL}/triggers/{{animation_name}}/objects/{{thing_name}}"
PUT_ANIMATION_URL_TEMPLATE = "{SEQUENCE_URL}/triggers/{animation_name}/objects/{element_name}"

# Define all possible elements. This list is used if an effect's 'elements' field is empty,
# implying it should apply to all configured elements.
# all_elements = [
#     "ring1", "ring2", "ring3", "ring4", "ring5", "ring6", "ring7", "ring8",
#     "ring9", "ring10", "ring11", "ring12"
# ]

# TODO(sapir): pull the offset from the song file
ADD_OFFSET = False
offset = 575

class Render:

    def __init__(self,
                 sequence_service_url: str = None,
                 snapshot_dir: str = None):
        self.sequence_service_url = sequence_service_url if sequence_service_url else SEQUENCE_URL
        self.log_dir = Path("animation_logs")
        self.log_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"animation_log_{self.timestamp}.txt"
        # Initialize sequence manager with snapshot directory if provided
        self.sequence_manager = KivseeSequence()

    def _save_animation_log(self, current_log_path, element_name: str,
                            animation_payload: dict, response_text: str):
        """Save animation response to both individual and combined log files."""
        # Save individual element animation
        element_file = current_log_path / f"{element_name}.json"
        with open(element_file, 'w') as f:
            # f.write(f"\n=== {element_name} Animation ===\n")
            # f.write(response_text)
            # f.write("\n")
            f.write(json.dumps(animation_payload, indent=2))
            # f.write("\n" + "=" * 50 + "\n")

        # Append to combined log file
        all_elements_file = current_log_path / f"all_elements.json"
        with open(all_elements_file, 'a') as f:
            f.write(f"\n=== {element_name} Animation ===\n")
            f.write(response_text)
            f.write("\n")
            f.write(json.dumps(animation_payload, indent=2))
            f.write("\n" + "=" * 50 + "\n")

    def store_single_animation(self, animation_name: str, element_name: str,
                               animation_payload: dict) -> bool:
        try:
            url = PUT_ANIMATION_URL_TEMPLATE.format(
                SEQUENCE_URL=SEQUENCE_URL,
                animation_name=animation_name,
                element_name=element_name)
            print(
                f"Storing animation for element: {element_name} at URL: {url}")

            response = self._put_request(url, animation_payload)

            response_text = f"Store animation for {element_name} response: {response.status_code}, {response.text}"
            print(response_text)
            # Save animation response to files
            self._save_animation_log(self.log_dir, element_name,
                                     animation_payload, response_text)

            print(f"Successfully stored animation for element: {element_name}")
            return True
        except Exception as e:
            print(f"Error storing animation for {element_name}: {str(e)}")
            return False

    def _convert_animation_to_proto(self, element_name: str,
                                    animation_payload: dict) -> dict:

        message = ParseDict(animation_payload, AnimationProto())
        serialized_message = message.SerializeToString()
        return serialized_message

    def get_animation_proto(self, element_name: str,
                            animation_payload: dict) -> dict:

        animation_name = "conversion_path"
        url = PUT_ANIMATION_URL_TEMPLATE.format(SEQUENCE_URL=SEQUENCE_URL,
                                                animation_name=animation_name,
                                                element_name=element_name)

        try:
            response = self._put_request(url, animation_payload)
            response = requests.get(
                url, headers={"accept": "application/x-protobuf"})
            if response.status_code == 200:
                return response.content
            else:
                print(
                    f"Failed to get animation proto: {response.status_code}, {response.text}"
                )
                return None
        except Exception as e:
            print(f"Error getting animation proto: {str(e)}")
            return None

    CONVERSION_NAME = "name_json_to_proto"

    def _get_animation_stats(self, animations_per_element: dict,
                             start_time: int, end_time: int) -> dict:
        all_protos = []
        for element_name, animation_data in animations_per_element.items():
            # proto = self.get_animation_proto(element_name, animation_data)
            proto = self._convert_animation_to_proto(element_name,
                                                     animation_data)
            if proto:
                # Create the thing entry using the template structure with hardcoded object_proto
                thing_entry = {
                    "thingName": element_name,
                    "sequenceProto": base64.b64encode(proto).decode('utf-8'),
                    "objectProto": RING_OBJECT_PROTO,
                }
                all_protos.append(thing_entry)

        if not all_protos:
            print("No valid protos found to analyze")
            return None

        try:
            url = f"{SIMULATION_URL}/sequence/stats"
            # Create the request payload using the template structure
            request_payload = {
                "things": all_protos,
                "startTimeMs": start_time,
                "endTimeMs": end_time
            }

            response = requests.post(url, json=request_payload)
            if response.status_code == 200:
                stats = response.json()
                print("Animation stats:", json.dumps(stats, indent=2))
                return stats
            else:
                print(
                    f"Failed to get animation stats: {response.status_code}, {response.text}"
                )
                return None
        except Exception as e:
            print(f"Error getting animation stats: {str(e)}")
            return None

    def get_animation_stats(self,
                            lol_animation_data: dict,
                            start_time: int = 0,
                            end_time: int = 100000) -> dict:
        """
        Wrapper method that preprocesses the animation data before getting stats.
        
        Args:
            lol_animation_data (dict): The raw animation data to analyze
            start_time (int): Start time in milliseconds for the stats analysis
            end_time (int): End time in milliseconds for the stats analysis
            
        Returns:
            dict: The animation stats or None if there was an error
        """
        preprocessed_animation_data = self.preprocess_animation(
            lol_animation_data)
        return self._get_animation_stats(
            preprocessed_animation_data["animation_data_per_element"],
            start_time, end_time)

    def store_animation(self, preprocessed_animation_data: dict):
        """
        Sends POST requests to store the animation data for each element.
        The animation data is now preprocessed to be specific to each element.
        """
        animation_name = preprocessed_animation_data.get(
            "name", "default_animation")
        # 'animation_data_per_element' holds the animation payload for each element
        animations_per_element = preprocessed_animation_data.get(
            "animation_data_per_element", {})

        if not animations_per_element:
            print(
                "No animation data generated for any element. Skipping storage."
            )
            return

        # current_log_path = self.log_dir
        # current_log_path.mkdir(exist_ok=True)

        # Iterate through each element and its specific animation payload
        for element_name, animation_payload in animations_per_element.items():
            self.store_single_animation(animation_name, element_name,
                                        animation_payload)

    def trigger_animation(self, animation_name: str, playback_offest: int = 0):
        """
        Triggers the animation by sending a POST request.
        Requires only the animation name.
        """
        url = f"{TRIGGER_URL}/trigger/{animation_name}"
        print(f"Trigger animation URL: {url}")
        response = self._post_request(url,
                                      {"start_offset_ms": playback_offest})
        print(
            f"Trigger animation response: {response.status_code}, {response.text}"
        )

    def trigger_song(self, animation_name: str, playback_offest: int):
        """
        Triggers the song playback associated with the animation.
        """
        url = f"{TRIGGER_URL}/song/{animation_name}/play"
        print(f"Trigger song URL: {url}")
        # The payload here should match what the /song/{name}/play endpoint expects.
        response = self._post_request(url,
                                      {"start_offset_ms": playback_offest})
        print(
            f"Trigger song response: {response.status_code}, {response.text}")

    def stop(self):
        """
        Stops all current animations and song playback.
        """
        url = f"{TRIGGER_URL}/stop"
        response = self._post_request(url, {})
        print(f"Stop response: {response.status_code}, {response.text}")

    def _put_request(self, url: str, payload: dict):
        """Helper method to send a PUT request."""
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.put(url, json=payload, headers=headers)
            return response
        except requests.exceptions.ConnectionError as e:
            print(
                f"Connection Error: Could not connect to {url}. Is the server running? Error: {e}"
            )

            # Return a mock response to allow the program to continue
            class MockResponse:
                status_code = 503
                text = "Service Unavailable - Connection Error"

            return MockResponse()
        except Exception as e:
            print(
                f"An unexpected error occurred during PUT request to {url}: {e}"
            )

            class MockResponse:
                status_code = 500
                text = f"Internal Server Error - {e}"

            return MockResponse()

    def _post_request(self, url: str, payload: dict):
        """Helper method to send a POST request."""
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, json=payload, headers=headers)
            return response
        except requests.exceptions.ConnectionError as e:
            print(
                f"Connection Error: Could not connect to {url}. Is the server running? Error: {e}"
            )

            class MockResponse:
                status_code = 503
                text = "Service Unavailable - Connection Error"

            return MockResponse()
        except Exception as e:
            print(
                f"An unexpected error occurred during POST request to {url}: {e}"
            )

            class MockResponse:
                status_code = 500
                text = f"Internal Server Error - {e}"

            return MockResponse()

    def get_animation_data(self) -> dict:
        try:
            animation_file_path = self.sequence_manager.get_animation_filename(
            )
            with open(animation_file_path, 'r') as file:
                animation_data = json.load(file)

            return animation_data
        except FileNotFoundError:
            print(f"Error: Animation file not found at {animation_file_path}.")
            print(
                "Please ensure the animation file exists at the specified path."
            )
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {animation_file_path}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while loading animation: {e}")

    def load_and_get_stats(self, start_time: int, end_time: int) -> dict:
        animation_data = self.get_animation_data()
        return self.get_animation_stats(animation_data, start_time, end_time)

    def load_and_print_animation(self,
                                 animation_name: str,
                                 playback_offest: int = 0):
        """
        Loads animation data from the default animation file, preprocesses it, and then renders it.
        """
        animation_data = self.get_animation_data()
        self.render(animation_data, animation_name, playback_offest)

    def load_from_snapshot(self,
                           snapshot_dir: str,
                           animation_name: str,
                           playback_offest: int = 0):
        """
        Loads animation data from a snapshot directory's animations folder, preprocesses it, and then renders it.
        
        Args:
            snapshot_dir (str): Path to the snapshot directory containing an 'animations' subdirectory
            playback_offest (int): Offset in milliseconds for playback timing
        """
        # Check for animations directory in snapshot
        animations_dir = os.path.join(SNAPSHOTS_DIR, snapshot_dir,
                                      "animations")
        if not os.path.exists(animations_dir):
            raise FileNotFoundError(
                "Animations directory is missing in the snapshot directory.")

        # Load all animation files from the directory
        animations = []
        for file in os.listdir(animations_dir):
            if file.endswith(self.sequence_manager.get_suffix()):
                with open(os.path.join(animations_dir, file), 'r') as f:
                    animations.append(json.load(f))

        # Load the sequences into the manager
        self.sequence_manager.load_sequences(animations)

        # Use the latest animation for rendering
        animation_data = self.sequence_manager.get_latest_sequence()
        if not animation_data:
            raise ValueError("No animations found in the snapshot directory.")

        self.render(animation_data, animation_name, playback_offest)

    def render_unpacked_animation(self, preprocessed_animation_data: dict):
        self.store_animation(preprocessed_animation_data)
        self.trigger_animation(preprocessed_animation_data['name'])

    def render(self,
               animation_data: dict,
               animation_name: str,
               playback_offest: int = 0,
               store_animation: bool = False):
        """
        Orchestrates the preprocessing, storing, and triggering of the animation.
        """
        animation_data['name'] = animation_name
        print(f"Hardcoded animation name to: {animation_data['name']}")

        print("Rendering animation...")
        # Preprocess the animation data to group effects by element
        preprocessed_animation_data = self.preprocess_animation(animation_data)

        if store_animation:
            self.store_animation(preprocessed_animation_data)

        # Trigger the song immediately
        self.trigger_song(preprocessed_animation_data['name'], playback_offest)

    def preprocess_animation(self, input_data: dict) -> dict:
        """
        Preprocesses the raw animation data, extracting effects and grouping them
        by the elements they apply to.
        This method generates a 'slim' version of each effect by removing
        metadata fields not needed by the rendering engine and then organizing
        these slim effects into a dictionary where keys are element names.
        Each EffectProto will have exactly one effect type (either color or other effect).
        """
        animation_details = input_data.get("animation", {})
        effects = animation_details.get("effects", [])

        # Dictionary to hold effects grouped by element.
        # Each element will have its own list of effects along with global animation properties.
        animations_per_element = {}

        # Get global animation properties that apply to all elements
        duration_ms = animation_details.get("duration_ms", 0)
        num_repeats = animation_details.get("num_repeats", 1)
        animation_name = input_data.get("name", "default_animation")

        if not effects:
            print(
                "No effects found in the animation data. Returning empty per-element animations."
            )
            return {"name": animation_name, "animation_data_per_element": {}}

        print(f"Preprocessing {len(effects)} effects...")

        for effect in effects:
            # Create base slim effect with common fields
            base_slim_effect = {
                key: value
                for key, value in effect.items() if key not in {
                    "effect_number",
                    "title",
                    "beat_and_bar",
                    "effect_summary",
                    "reasoning",
                    "elements",
                }
            }

            # Add offset to the start_time and end_time of the effect if enabled
            if ADD_OFFSET:
                slim_config = base_slim_effect.get("effect_config", {})
                slim_config["start_time"] = slim_config.get("start_time",
                                                            0) + offset
                slim_config["end_time"] = slim_config.get("end_time",
                                                          0) + offset

            # Determine which elements this effect applies to
            effect_elements = effect.get("elements", [])
            if not effect_elements:
                # If the 'elements' list is empty, apply this effect to the special "all" element.
                print(
                    f"Effect {effect.get('effect_number', 'N/A')} has no specific elements, applying to element: 'all'"
                )
                effect_elements = ["all"]

            # Create separate EffectProtos for each effect type
            split_effects = []

            # Handle all effects in the same way
            for effect_type in [
                    "const_color", "rainbow", "brightness", "hue",
                    "saturation", "snake"
            ]:
                if effect.get(effect_type):
                    split_effect = {
                        "effect_config": base_slim_effect["effect_config"],
                        effect_type: effect[effect_type]
                    }
                    split_effects.append(split_effect)

            # Add effects to each element
            for element in effect_elements:
                if element not in animations_per_element:
                    animations_per_element[element] = {
                        "duration_ms": duration_ms,
                        "num_repeats": num_repeats,
                        "effects": []
                    }

                # Add all split effects
                animations_per_element[element]["effects"].extend(
                    split_effects)

        return {
            "name": animation_name,
            "animation_data_per_element": animations_per_element
        }


def main():
    render = Render()
    # render.load_and_print_animation(playback_offest=14406)

    render.load_and_get_stats(0, 1501)
    # Example of getting animation stats
    # test_stats(render)


if __name__ == "__main__":
    main()
