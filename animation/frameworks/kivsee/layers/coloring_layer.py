import json
from typing import List, Dict, Union, Optional


def create_alternate_effect(
        start_time_ms: int, end_time_ms: int, color_1: str,
        color_2: str) -> Dict[str, Union[str, List[str], Dict]]:

    effect_config = {{
        "effect_config": {
            "start_time": start_time_ms,
            "end_time": end_time_ms,
            "segments": "b1",
        },
        "const_color": {
            "color": {
                "hue": color_1,
                "sat": 1.0,
                "val": 1.0,
            }
        },
    }, {
        "effect_config": {
            "start_time": start_time_ms,
            "end_time": end_time_ms,
            "segments": "b2",
        },
        "const_color": {
            "color": {
                "hue": color_2,
                "sat": 1.0,
                "val": 1.0,
            }
        },
    }}
    return effect_config


def create_alternate_between_multiple_elements(
        elements: List[str], color_1: str,
        color_2: str) -> Dict[str, Union[str, List[str], Dict]]:

    effect_configs = {}
    for element in elements:
        effect_configs[element] = {
            "effect_config": {
                "segments": "all",
            },
            "const_color": {
                "color": {
                    "hue": color_1 if element % 2 == 0 else color_2,
                    "sat": 1.0,
                    "val": 1.0,
                }
            },
        }
    return effect_configs


def create_segmeneted_alternate_color_multiple_elements(
        elements: List[str], start_time_ms: int, end_time_ms: int,
        color_1: str, color_2: str) -> Dict[str, Union[str, List[str], Dict]]:

    effect_configs = {}
    for element in elements:
        if element % 2 == 0:
            effect_configs[element] = create_alternate_effect(
                start_time_ms, end_time_ms, color_1, color_2)
        else:
            effect_configs[element] = create_alternate_effect(
                start_time_ms, end_time_ms, color_2, color_1)
    return effect_configs
