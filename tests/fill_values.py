import json
import os
import random
from itertools import product

RELATIVE_DATA_PATH = "tests/data/"


def fill_template_values(
    setup_filename="setup.json",
    test_filename="data_template.json",
    template_filename="values.json",
    output_filename="data_filled.json",
):
    """
    Reads animation test data and template values from JSON files,
    fills in the template values in the test data, including beat_start and beat_end,
    and writes the filled test data to a new JSON file.
    Also fills in the song template values in the setup and creates the final prompt.

    Args:
        setup_filename (str): The name of the setup data JSON file.
        test_filename (str): The name of the test data JSON file.
        template_filename (str): The name of the template values JSON file.
        output_filename (str): The name of the output JSON file.
    """
    try:
        # Get the directory of the current script
        script_dir = os.getcwd()

        # Construct full file paths
        full_setup_path = os.path.join(script_dir, RELATIVE_DATA_PATH,
                                       setup_filename)
        full_test_path = os.path.join(script_dir, RELATIVE_DATA_PATH,
                                      test_filename)
        full_template_path = os.path.join(script_dir, RELATIVE_DATA_PATH,
                                          template_filename)
        full_output_path = os.path.join(script_dir, RELATIVE_DATA_PATH,
                                        output_filename)

        with open(full_setup_path, "r") as f:
            setup_data = json.load(f)

        with open(full_test_path, "r") as f:
            test_data = json.load(f)

        with open(full_template_path, "r") as f:
            template_values = json.load(f)

        # Fill in song template values
        song = random.choice(template_values["songs"])
        setup_data["song"]["name"] = song["name"]
        setup_data["song"]["duration"] = song["duration"]
        setup_data["song"]["structure"] = song["structure"]

        # Choose one random combination of template values
        template_keys = [
            key for key in template_values.keys()
            if key not in ["time_frame", "songs"]
        ]

        for test in test_data["tests"]:
            instruction = test["instruction"]
            expected_output = test["expected_output"]

            # Extract time frame
            time_frame = random.choice(template_values["time_frame"])
            if "beats" in time_frame:
                beat_start, beat_end = map(int,
                                           time_frame.split(" ")[1].split("-"))
            elif "bars" in time_frame:
                bar_start, bar_end = map(int,
                                         time_frame.split(" ")[1].split("-"))
                beat_start = bar_start * 4
                beat_end = bar_end * 4
            else:
                beat_start, beat_end = 0, 4  # Default values

            # Fill in beat_start and beat_end
            for beat in expected_output["animation"]["beats"]:
                beat["beat_start"] = beat_start
                beat["beat_end"] = beat_end

            if "{time_frame}" in instruction:
                instruction = instruction.replace("{time_frame}", time_frame)

            # Scan and replace template values in expected_output
            def replace_template_values(obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if isinstance(
                                v,
                                str) and v.startswith("{") and v.endswith("}"):
                            key = v[1:-1]
                            if key in template_keys:
                                obj[k] = random.choice(template_values[key])
                        else:
                            replace_template_values(v)
                elif isinstance(obj, list):
                    for item in obj:
                        replace_template_values(item)

            replace_template_values(expected_output)

            # Fill in beat_start and beat_end in expected_output
            for beat in expected_output["animation"]["beats"]:
                if beat["beat_start"] == "{beat_start}":
                    beat["beat_start"] = beat_start
                if beat["beat_end"] == "{beat_end}":
                    beat["beat_end"] = beat_end

            # Create the final prompt
            final_prompt = (f"{setup_data['prompt']}\n\n"
                            f"Song: {setup_data['song']['name']}\n"
                            f"Duration: {setup_data['song']['duration']}\n"
                            f"Structure: {setup_data['song']['structure']}\n\n"
                            f"You Task: {instruction}")
            test["prompt"] = final_prompt
            test["instruction"] = instruction
            test["expected_output"] = expected_output

        # Write the filled test data to a new file
        with open(full_output_path, "w") as f:
            json.dump(test_data, f, indent=4)

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    fill_template_values()
