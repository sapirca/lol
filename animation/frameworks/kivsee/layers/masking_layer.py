import json
from typing import List, Dict, Union, Optional


def create_dot_masking(
        start_time_ms: int, end_time_ms: int, sparsity: float,
        elements: List[str]) -> Dict[str, Union[str, List[str], Dict]]:
    normalized_sparsity = sparsity * 1.5 + 0.05

    effect_config = [{
        "effect_config": {
            "start_time": start_time_ms,
            "end_time": end_time_ms,
            "segments": "rand",
        },
        "snake": {
            "head": {
                "const_value": {
                    "value": 1.0,
                }
            },
            "tail_length": {
                "const_value": {
                    "value": normalized_sparsity,
                }
            },
            # "cyclic": True
        }
    }]

    effect_configs = {}
    for element in elements:
        effect_configs[element] = effect_config
    return effect_configs


def create_round_masking(
        sparsity: float,
        elements: List[str]) -> Dict[str, Union[str, List[str], Dict]]:
    normalized_sparsity = sparsity * 1.5 + 0.05

    effect_config = [{
        "effect_config": {
            "segments": "arc",
        },
        "snake": {
            "head": {
                "const_value": {
                    "value": 1.0,
                }
            },
            "tail_length": {
                "const_value": {
                    "value": normalized_sparsity,
                }
            },
            # "cyclic": True
        }
    }]

    effect_configs = {}
    for element in elements:
        effect_configs[element] = effect_config
    return effect_configs
