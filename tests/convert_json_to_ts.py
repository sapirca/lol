import json
import os

RELATIVE_DATA_PATH = os.getcwd()

def json_to_typescript(json_data, output_file=f"{RELATIVE_DATA_PATH}/animation.ts"):
    """
    Converts a JSON object to a TypeScript file representing an animation sequence.

    Args:
        json_data (dict): The JSON object representing the animation.
        output_file (str): The name of the output TypeScript file.
    """

    try:
        # Extract animation data from the new schema
        animation_data = json_data.get("animation", {})
        song_name = animation_data.get("name", "").replace(" ", "_").replace("/", "_").replace("\\", "_")
        duration = animation_data.get("duration", 0)
        # BPM isn't in the new schema, so we'll set a default value or calculate it
        # based on duration and beats if needed
        song_bpm = animation_data.get("bpm", 120)  # Default value
        beats_data = animation_data.get("beats", [])

        typescript_code = """
import { Effect } from "./effects/types";
import { sendSequence, SequencePerThing } from "./services/sequence";
import { startSong, trigger } from "./services/trigger";
import { Animation } from "./animation/animation";
import { NUMBER_OF_RINGS } from "./sys-config/sys-config";
import { beats, cycleBeats } from "./time/time";
import { constColor, rainbow } from "./effects/coloring";
import { blink, fadeIn, fadeOut, fadeInOut, fadeOutIn, constant as constantBrightness } from "./effects/brightness";
import { elements, segment } from "./objects/elements";
import {
    all,
    segment_arc,
    segment_b1,
    segment_b2,
    segment_centric,
    segment_ind,
    segment_updown,
} from "./objects/ring-elements";
import { snake, snakeInOut } from "./effects/motion";
import { phase } from "./phase/phase";

const animationSequence = async () => {
"""

        typescript_code += """
    const animation = new Animation("{song_name}", {duration}, {bpm}); // Assuming 50 is a default phase value
    animation.sync(() => {{
""".format(song_name=song_name, duration=duration, bpm=song_bpm)

        for beat in beats_data:
            # Update to use beat_start and beat_end instead of time_start and time_end
            beat_start = beat.get("beat_start", 0)
            beat_end = beat.get("beat_end", 0)
            elements_list = beat.get("elements", [])
            mapping = beat.get("mapping", None)

            typescript_code += f"""        beats({beat_start}, {beat_end}, () => {{\n"""

            elements_array = "[" + ",".join(elements_list) + "]"

            # Process each element in the elements list
            # for element_name in elements_list:

            typescript_code += f"            elements({elements_array}, () => {{\n"

            # Handle mapping if present
            if mapping:
                for map_type in mapping:
                    if map_type == "centric":
                        typescript_code += "                segment_centric();\n"
                    elif map_type == "updown":
                        typescript_code += "                segment_updown();\n"
                    elif map_type == "arc":
                        typescript_code += "                segment_arc();\n"
                    elif map_type == "ind":
                        typescript_code += "                segment_ind();\n"
                    elif map_type == "1_pixel_every_4":
                        typescript_code += "                segment_b1();\n"
                    elif map_type == "1_pixel_every_2":
                        typescript_code += "                segment_b2();\n"

            # Process coloring
            coloring = beat.get("coloring")
            if coloring:
                coloring_type = coloring.get("type")
                if coloring_type == "constant":
                    hue = coloring.get("hue")
                    # Handle named colors
                    if isinstance(hue, str):
                        color_map = {
                            "RED": 0.0,
                            "ORANGE": 0.125,
                            "YELLOW": 0.250,
                            "GREEN": 0.376,
                            "AQUA": 0.502,
                            "BLUE": 0.627,
                            "PURPLE": 0.752,
                            "PINK": 0.878
                        }
                        hue = color_map.get(hue, 0.0)

                    typescript_code += f"                constColor({{ hue: {hue}, saturation: 1.0, value: 1.0 }});\n"
                elif coloring_type == "rainbow":
                    typescript_code += "                rainbow();\n"

            # Process brightness
            brightness = beat.get("brightness")
            if brightness:
                brightness_type = brightness.get("type")
                if brightness_type == "constant":
                    factor_value = brightness.get("factor_value", 1.0)
                    typescript_code += f"                brightness({{ factor: {factor_value} }});\n"
                elif brightness_type == "fadeIn":
                    typescript_code += "                fadeIn();\n"
                elif brightness_type == "fadeOut":
                    typescript_code += "                fadeOut();\n"
                elif brightness_type == "blink":
                    typescript_code += "                blink();\n"
                elif brightness_type == "fadeInOut":
                    typescript_code += "                fadeInOut();\n"
                elif brightness_type == "fadeOutIn":
                    typescript_code += "                fadeOutIn();\n"

            # Process motion
            motion = beat.get("motion")
            if motion:
                motion_type = motion.get("type")
                if motion_type == "snake":
                    typescript_code += "                snake();\n"
                elif motion_type == "snakeInOut":
                    typescript_code += "                snakeInOut();\n"

            typescript_code += "            });\n"
        typescript_code += "        });\n"

        typescript_code += "    });"
        addition = f"""
    await sendSequence("{song_name}", animation.getSequence());
    await trigger("{song_name}");
""".format(song_name=song_name)

        # await trigger();
        addition += """
};


(async () => {
    await animationSequence();
})();
"""

        typescript_code += addition

        with open(output_file, "w") as f:
            f.write(typescript_code)

        print(f"TypeScript file '{output_file}' generated successfully.")

    except (KeyError, TypeError, FileNotFoundError) as e:
        print(f"Error processing JSON data: {e}")


# Example Usage based on the new schema:
json_data = {
    "animation": {
        "name": "Custom Animation 01",
        "duration": 2.0,
        "beats": [
            {
                "beat_start": 0,
                "beat_end": 4,
                "elements": [
                    "ring1"
                ],
                "coloring": {
                    "type": "constant",
                    "hue": "PINK"
                }
            }
        ]
    }
}

json_to_typescript(json_data)
