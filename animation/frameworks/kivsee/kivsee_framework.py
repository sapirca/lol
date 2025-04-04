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
        content = ""
        try:
            with open(KIVSEE_PROMPT, 'r') as file:
                content += "##Here's a memory of what you learnt and remembered in previous conversations with the user: \n"    
                content += file.read()
            content += "##Aladdin song details "
            "\nYou are generating the animation to the song named aladdin. The song is 79 seconds long and has a BPM of 64.725."
            with open(
                    '/Users/sapir/repos/lol/animation/frameworks/kivsee/songs/aladdin_bars.txt',
                    'r') as file:
                content += "## Bars"
                content += "\n A list of Aladdin bars their corresponding start time in miliseconds:\n" 
                content += file.read()
            with open(
                    '/Users/sapir/repos/lol/animation/frameworks/kivsee/songs/aladdin_beats.txt',
                    'r') as file:
                content += "## Beats"
                content += "\n A list of aladdin beats and their corresponding start time in miliseconds:\n" 
                content += file.read()
            with open(
                    '/Users/sapir/repos/lol/animation/frameworks/kivsee/songs/aladdin_info.txt',
                    'r') as file:
                content += "These are important parts in the song you should make animation changes\n" 
                content += file.read()

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
