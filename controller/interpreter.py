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
            if backend.lower() in ["gpt", "deepseek"]:
                response_json = json.loads(rf'{response}')
                result["reasoning"] = response_json.get("reasoning", "")
                result["animation_sequence"] = response_json.get(
                    "animation", {})
            elif backend.lower() in ["gemini", "claude"]:
                json_start = response.find("```json")
                json_end = response.find("```", json_start + len("```json"))
                if json_start != -1 and json_end != -1:
                    json_scheme = response[json_start +
                                           len("```json"):json_end]
                    the_rest = response[:json_start] + response[json_end +
                                                                len("```"):]
                    result["additionals"] = the_rest

                    try:
                        response_json = json.loads(json_scheme)
                        result["reasoning"] = response_json.get(
                            "reasoning", "")
                        result["animation_sequence"] = response_json.get(
                            "animation", "")
                    except json.JSONDecodeError as e:
                        result["animation_sequence"] = json.loads(
                            rf"{json_scheme}")
                        result["reasoning"] = "fallback"
                else:
                    raise ValueError(
                        f"Could not find structured output in response for {backend}"
                    )
                    # response_json = json.loads(response)
            else:
                raise ValueError(f"Unsupported backend: {backend}")

        except json.JSONDecodeError as e:
            print(f"Error parsing structured response for {backend}: {e}")

        return result

    def parse_response(self, response, backend=None):
        result = {
            "reasoning": "",
            "animation_sequence": "",
        }

        if "<animation>" in response and "</animation>" in response:
            animation_start = response.find("<animation>") + len("<animation>")
            animation_end = response.find("</animation>")
            result["animation_sequence"] = response[
                animation_start:animation_end]
            result["reasoning"] = response[:animation_start -
                                           len("<animation>")] + response[
                                               animation_end +
                                               len("</animation>"):]
        elif "```json" in response and "```" in response:
            json_start = response.find("```json")
            json_end = response.find("```", json_start + len("```json"))
            if json_start != -1 and json_end != -1:
                result["animation_sequence"] = response[
                    json_start + len("```json"):json_end].strip()
                result["reasoning"] = response[:json_start] + response[
                    json_end + len("```"):]
        elif backend and self.config.get('with_structured_output', False):
            structured_result = self.parse_structured(response, backend)
            result["reasoning"] = structured_result["reasoning"]
            result["animation_sequence"] = structured_result[
                "animation_sequence"]
        else:
            result["reasoning"] = response

        return result
