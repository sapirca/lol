from pydantic import BaseModel
from animation.frameworks.framework import Framework
from animation.frameworks.xlights.xlights_scheme import XlightsScheme
from animation.frameworks.xlights.xlights_sequence import XlightsSequence
import os
import xml.etree.ElementTree as ET
from controller.constants import XLIGHTS_HOUSE_PATH, XLIGHTS_KNOWLEDGE_PATH, XLIGHTS_TEMP_ANIMATION_FILE, XLIGHTS_SEQUENCE_PATH


class XLightsFramework(Framework):

    def get_world_structure(self):
        try:
            tree = ET.parse(XLIGHTS_HOUSE_PATH)
            root = tree.getroot()
            return ET.tostring(root, encoding='unicode')
        except Exception as e:
            print(f"Logger: Error loading house configuration: {e}")
            return f"Xlights: Error loading house configuration: {e}"

    def get_domain_knowledge(self):
        try:
            with open(XLIGHTS_KNOWLEDGE_PATH, 'r') as file:
                content = file.read()
            return content
        except Exception as e:
            print(f"Logger: Error reading domain knowledge: {e}")
            return f"Xlights: Error reading domain knowledge: {e}"

    def get_response_scheme_obj(self) -> BaseModel:
        return XlightsScheme()
