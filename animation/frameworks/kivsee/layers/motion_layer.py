import json
from typing import List, Dict, Union, Optional


def create_snow_sparkle(
        start_time_ms: int,
        end_time_ms: int,
        bpm: int,
        phase: float = 0.0) -> Dict[str, Union[str, List[str], Dict]]:

    duration_ms = end_time_ms - start_time_ms
    beats_per_second = bpm / 60
    beats_per_duration_ms = 1000 / beats_per_second

    repeat_num = duration_ms / beats_per_duration_ms

    # Only keep 2 digits after the decimal point
    repeat_num_by_the_beat = round(repeat_num / 2, 3)

    effect_config = {
        "effect_config": {
            "segments": "b1",
        },
        "const_value": {
            "hue": 0.0,
            "sat": 0.0,
            "val": 1.0,
        },
        "brightness": {
            "sin": {
                "min": 0.0,
                "max": 1.0,
                "phase": phase,
                "repeats": repeat_num_by_the_beat,
            },
        }
    }
    return effect_config


def create_snow_sparkle_elements(
        elements: List[str], start_time_ms: int, end_time_ms: int,
        bpm: int) -> Dict[str, Union[str, List[str], Dict]]:

    effect_configs = {}
    phase_offset = 0.0
    for element in elements:
        effect_configs[element] = create_snow_sparkle(start_time_ms,
                                                      end_time_ms,
                                                      bpm,
                                                      phase=phase_offset)
        phase_offset += 1 / len(elements)
    return effect_configs
