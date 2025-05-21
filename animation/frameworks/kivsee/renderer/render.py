import json
import requests
from animation.frameworks.kivsee.kivsee_sequence import KivseeSequence
import os
from datetime import datetime
from pathlib import Path
from constants import ANIMATION_OUT_TEMP_DIR, SNAPSHOTS_DIR

from schemes.kivsee_scheme.effects_scheme import AnimationProto

# Kivsee-sapir IP 10.0.1.204
# VNC?
# 10.0.0.36
# pi@raspberrypi
# kivsee12

RASPBERRY_PI_IP = "192.168.1.12"
SEQUENCE_URL = f"http://{RASPBERRY_PI_IP}:8082"
TRIGGER_URL = f"http://{RASPBERRY_PI_IP}:8083"

# Define all possible elements. This list is used if an effect's 'elements' field is empty,
# implying it should apply to all configured elements.
all_elements = [
    "ring1", "ring2", "ring3", "ring4", "ring5", "ring6", "ring7", "ring8",
    "ring9", "ring10", "ring11", "ring12"
]

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
        # current_log_path = self.log_dir / f"{self.timestamp}"
        current_log_path = self.log_dir
        current_log_path.mkdir(exist_ok=True)
        # Iterate through each element and its specific animation payload
        for element_name, animation_payload in animations_per_element.items():
            try:
                # Create AnimationProto for this element
                # animation_proto = AnimationProto(**animation_payload)

                # Store the animation using the same URL structure as before
                url = f"{SEQUENCE_URL}/triggers/{animation_name}/objects/{element_name}"
                print(
                    f"Storing animation for element: {element_name} at URL: {url}"
                )
                # print(
                #     f"Payload for {element_name}: {json.dumps(animation_payload, indent=2)}"
                # )

                response = self._put_request(url, animation_payload)

                response_text = f"Store animation for {element_name} response: {response.status_code}, {response.text}"
                print(response_text)
                # Save animation response to files
                self._save_animation_log(current_log_path, element_name,
                                         animation_payload, response_text)

                print(
                    f"Successfully stored animation for element: {element_name}"
                )
            except Exception as e:
                print(f"Error storing animation for {element_name}: {str(e)}")
                continue

    def trigger_animation(self,
                          animation_data: dict,
                          playback_offest: int = 0):
        """
        Triggers the animation by sending a POST request.
        Requires only the animation name.
        """
        animation_name = animation_data.get("name", "default_animation")
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

    def load_and_print_animation(self, playback_offest: int = 0):
        """
        Loads animation data from the default animation file, preprocesses it, and then renders it.
        """
        animation_file_path = self.sequence_manager.get_animation_filename()
        try:
            with open(animation_file_path, 'r') as file:
                animation_data = json.load(file)

            self.render(animation_data, playback_offest)
        except FileNotFoundError:
            print(f"Error: Animation file not found at {animation_file_path}.")
            print(
                "Please ensure the animation file exists at the specified path."
            )
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {animation_file_path}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while loading animation: {e}")

    def load_from_snapshot(self, snapshot_dir: str, playback_offest: int = 0):
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

        self.render(animation_data, playback_offest)

    def render(self, animation_data: dict, playback_offest: int):
        """
        Orchestrates the preprocessing, storing, and triggering of the animation.
        """
        # Hardcode the animation name to 'aladdin'
        animation_data['name'] = 'aladdin'
        print(f"Hardcoded animation name to: {animation_data['name']}")

        print("Rendering animation...")
        # Preprocess the animation data to group effects by element
        preprocessed_animation_data = self.preprocess_animation(animation_data)
        self.store_animation(preprocessed_animation_data)
        # self.trigger_animation(preprocessed_animation_data, playback_offest)
        # animation_name = animation_data.get("name", "default_animation")
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
                # If the 'elements' list is empty, apply this effect to all elements defined globally.
                print(
                    f"Effect {effect.get('effect_number', 'N/A')} has no specific elements, applying to all: {all_elements}"
                )
                effect_elements = all_elements

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
    render.load_and_print_animation(playback_offest=14406)


if __name__ == "__main__":
    main()
