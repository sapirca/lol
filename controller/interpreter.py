from controller.constants import XSEQUENCE_TAG
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
            result["animation_sequence"] = response[animation_start:animation_end]
            result["response_wo_animation"] = response[:animation_start - len("<animation>")] + response[animation_end + len("</animation>"):]
        else:
            result["response_wo_animation"] = response

        tags = re.findall(r"<([a-zA-Z0-9_]+)>(.*?)</\1>", result["response_wo_animation"], re.DOTALL)
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

        if result["animation_sequence"]:
            self.animation_manager.process_animation(result["animation_sequence"])

        return result
