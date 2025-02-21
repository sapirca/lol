import re
from animation.animation_manager import AnimationManager


class Interpreter:

    def __init__(self, animation_manager):
        self.animation_manager = animation_manager

    def parse_response(self, response):
        result = {
            "response_wo_animation": None,
            "reasoning": None,
            "consistency_justification": None,
            "requested_actions": [],
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
        # TODO try all possible tags for different models
        if "```json" in response and "```" in response:
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

        tags = re.findall(r"<([a-zA-Z0-9_]+)>(.*?)</\1>",
                          result["response_wo_animation"], re.DOTALL)
        for tag, content in tags:
            if tag == "reasoning":
                result["reasoning"] = content.strip()
            elif tag == "consistency_justification":
                result["consistency_justification"] = content.strip()
            else:
                result["requested_actions"].append({
                    "action": tag,
                    "content": content.strip()
                })

        return result
