from pydantic import BaseModel
from animation.frameworks.framework import Framework
from animation.frameworks.kivsee.scheme.effects_scheme import KivseeSchema
from constants import KIVSEE_HOUSE_PATH, KIVSEE_PROMPT


class KivseeFramework(Framework):

    def __init__(self):
        pass

    def get_world_structure(self):
        try:
            with open(KIVSEE_HOUSE_PATH, 'r') as file:
                house_structure = file.read()
            return house_structure
        except Exception as e:
            print(f"Logger: Error loading house configuration: {e}")
            raise RuntimeError(
                "Kivsee: Failed to load the house configuration") from e

    def get_domain_knowledge(self):
        try:
            with open(KIVSEE_PROMPT, 'r') as file:
                content = file.read()


# with open(KIVSEE_KNOWLEDGE_PATH, 'r') as file:
#     content = file.read()
# with open(KIVSEE_ADD_ONS_PATH, 'r') as file:
#     content += file.read()
# for i in range(1, 2):
#     with open(KIVSEE_ANIMATION_EXAMPLE+f"_{i}.ts", 'r') as file:
#         content += file.read()
            return content
        except Exception as e:
            print(f"Logger: Error reading domain knowledge: {e}")
            return "Kivsee domain knowledge"

    def get_response_scheme_obj(self) -> BaseModel:
        # /Users/sapir/repos/lol/animation/frameworks/kivsee/scheme/effects_p2p.py
        return KivseeSchema
