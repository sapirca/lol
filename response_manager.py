# /Users/sapir/repos/lol/response_manager.py
from constants import XSEQUENCE_TAG
import re


class ResponseManager:

    def __init__(self, sequence_manager):
        self.sequence_manager = sequence_manager

    def parse_response(self, response):
        result = {
            "response_wo_animation": None,
            "reasoning": None,
            "consistency_justification": None,
            "requested_actions": [],
            "animation_sequence": None,
        }

        if "<?xml" in response and f"</{XSEQUENCE_TAG}>" in response:
            sequence_start = response.find("<?xml")
            sequence_end = response.find(f"</{XSEQUENCE_TAG}>") + len(
                f"</{XSEQUENCE_TAG}>")
            sequence_xml = response[sequence_start:sequence_end]
            result["animation_sequence"] = sequence_xml

            # Save the response without the animation
            result[
                "response_wo_animation"] = response[:sequence_start] + response[
                    sequence_end:]
            response = result["response_wo_animation"]
        else:
            result["response_wo_animation"] = response

        tags = re.findall(r"<([a-zA-Z0-9_]+)>(.*?)</\1>", response, re.DOTALL)
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
