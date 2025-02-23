import json

def json_to_typescript(json_data, output_file="tests/output/animation.ts"):
    """
    Converts a JSON object to a TypeScript file representing an animation sequence.

    Args:
        json_data (dict): The JSON object representing the animation.
        output_file (str): The name of the output TypeScript file.
    """

    try:
        animation_data = json_data["animation"]
        song_name = animation_data["name"]
        duration = animation_data["duration"]
        song_bpm = animation_data["bpm"]
        beats_data = animation_data["beats"]

        typescript_code = """
import { Effect } from "./effects/types";
import { sendSequence, SequencePerThing } from "./services/sequence";
import { startSong, trigger } from "./services/trigger";
import { Animation } from "./animation/animation";
import { NUMBER_OF_RINGS } from "./sys-config/sys-config";
import { beats, cycleBeats } from "./time/time";
import { constColor, rainbow } from "./effects/coloring";
import { blink, fadeIn, fadeInOut, fadeOutIn } from "./effects/brightness";
import { elements, segment } from "./objects/elements";
import {
    all,
    segment_arc,
    segment_b1,
    segment_b2,
    segment_centric,
    segment_ind,
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
            time_start = beat["time_start"]
            time_end = beat["time_end"]
            elements = beat["elements"]

            typescript_code += f"""        beats({time_start}, {time_end}, () => {{\n"""

            for element in elements:
                element_group = element.get("element_group")
                element_name = element.get("element")
                coloring = element.get("coloring")
                brightness = element.get("brightness")
                motion = element.get("motion")

                if element_group:
                    if isinstance(element_group, str):
                        typescript_code += f"            elements({element_group}, () => {{\n"
                    elif isinstance(element_group, list):
                        typescript_code += f"            elements([{', '.join([f'{e}' for e in element_group])}], () => {{\n"

                elif element_name:
                    typescript_code += f"            elements({element_name}, () => {{\n"

                if coloring:
                    coloring_type = coloring.get("type")
                    if coloring_type == "constColor":
                        hue = coloring.get("hue")
                        saturation = coloring.get("saturation")
                        value = coloring.get("value")
                        if saturation is not None and value is not None:
                            if value > 0.5:
                                value = 0.5
                            typescript_code += f"                constColor({{ hue: {hue}, saturation: {saturation}, value: {value} }});\n"
                        else:
                            typescript_code += f"                constColor({{ hue: {hue}, saturation: 1.0, value: 0.3 }});\n"

                    elif coloring_type == "rainbow":
                        typescript_code += "                rainbow();\n"

                if brightness:
                    brightness_type = brightness.get("type")
                    if brightness_type == "fadeIn":
                        start = brightness.get("start")
                        end = brightness.get("end")
                        typescript_code += f"                fadeIn({{ start: {start}, end: {end} }});\n"
                    elif brightness_type == "fadeOut":
                        start = brightness.get("start")
                        end = brightness.get("end")
                        typescript_code += f"                fadeOut({{ start: {start}, end: {end} }});\n"
                    elif brightness_type == "fadeInOut":
                        min_val = brightness.get("min")
                        max_val = brightness.get("max")
                        typescript_code += f"                fadeInOut({{ min: {min_val}, max: {max_val} }});\n"
                    elif brightness_type == "fadeOutIn":
                        min_val = brightness.get("min")
                        max_val = brightness.get("max")
                        typescript_code += f"                fadeOutIn({{ min: {min_val}, max: {max_val} }});\n"
                    elif brightness_type == "blink":
                        low = brightness.get("low")
                        high = brightness.get("high")
                        typescript_code += f"                blink({{ low: {low}, high: {high} }});\n"

                if motion:
                    motion_type = motion.get("type")
                    if motion_type == "snake":
                        typescript_code += "                snake();\n"
                    elif motion_type == "snakeInOut":
                        start = motion.get("start")
                        end = motion.get("end")
                        typescript_code += f"                snakeInOut({{ start: {start}, end: {end} }});\n"

            typescript_code += "            });\n"
            typescript_code += "        });\n"
        typescript_code += "    });"
        addition = f"""
    await sendSequence("{song_name}", animation.getSequence());
    await startSong("{song_name}");
""".format(song_name=song_name)
        
        addition += """
    await trigger();
};


(async () => {{
    await animationSequence();
}})();
"""
        
        typescript_code += addition

        with open(output_file, "w") as f:
            f.write(typescript_code)

        print(f"TypeScript file '{output_file}' generated successfully.")

    except (KeyError, TypeError, FileNotFoundError) as e:
        print(f"Error processing JSON data: {e}")

# Example Usage:
json_data = {
    "animation": {
        "name": "sandstorm",
        "duration": 180,
        "bpm": 126,
        "beats": [
            {
                "time_start": 0,
                "time_end": 10,
                "elements": [
                    {
                        "element_group": "all",
                        "coloring": {
                            "type": "constColor",
                            "hue": 0.9
                        },
                        "brightness": {
                            "type": "fadeIn",
                            "start": 0,
                            "end": 1
                        },
                        "motion": {
                            "type": "snake"
                        }
                    },
                    {
                        "element": "even",
                        "coloring": {
                            "type": "rainbow"
                        },
                        "brightness": {
                            "type": "blink",
                            "low": 0.5,
                            "high": 1
                        },
                        "motion": {
                            "type": "snakeInOut",
                            "start": 0.2,
                            "end": 0.8
                        }
                    }
                ]
            }
        ]
    }
}

json_to_typescript(json_data)
