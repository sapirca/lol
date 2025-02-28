import json
import re
from animation.animation_manager import AnimationManager

animation_sequence = "animation_sequence"


class Interpreter:

    def __init__(self, animation_manager, config=None):
        self.animation_manager = animation_manager
        self.config = config or {}

    def parse_structured(self, response, backend):
        result = {
            "reasoning": None,
            "animation_sequence": None,
        }

        try:
            if backend.lower() == "gpt" or backend.lower() == "deepseek":
                response_json = json.loads(response)
                result["reasoning"] = response_json.get("reasoning", "")
                result["animation_sequence"] = response_json.get(
                    "animation", {})
                return result
            elif backend.lower() == "gemini" or backend.lower() == "claude":
                json_start = response.find("```json")
                json_end = response.find("```", json_start + len("```json"))
                if json_start != -1 and json_end != -1:
                    response_json = json.loads(
                        response[json_start + len("```json"):json_end].strip())

                    the_rest = response[:json_start] + response[json_end +
                                                                len("```"):]
                    if the_rest == None:
                        result["additionals"] = ""
                    else:
                        result["additionals"] = the_rest
                    result["reasoning"] = response_json.get("reasoning", "")
                    result["animation_sequence"] = response_json.get(
                        "animation", {})
                    return result

        except json.JSONDecodeError as e:
            print(f"Error parsing structured response for {backend}: {e}")
        return result

    def parse_response(self, response, backend=None):
        result = {
            "response_wo_animation": None,
            "animation_sequence": None,
        }

        if "<animation>" in response and "</animation>" in response:
            animation_start = response.find("<animation>") + len("<animation>")
            animation_end = response.find("</animation>")
            result["animation_sequence"] = response[
                animation_start:animation_end]
            result["response_wo_animation"] = response[:animation_start - len(
                "<animation>")] + response[animation_end +
                                           len("</animation>"):]
        elif "```json" in response and "```" in response:
            json_start = response.find("```json")
            json_end = response.find("```", json_start + len("```json"))
            if json_start != -1 and json_end != -1:
                result["animation_sequence"] = response[
                    json_start + len("```json"):json_end].strip()
                result[
                    "response_wo_animation"] = response[:json_start] + response[
                        json_end + len("```"):]
        else:
            result["response_wo_animation"] = response

        return result
