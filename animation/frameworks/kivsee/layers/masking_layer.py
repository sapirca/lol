import json
from typing import List, Dict, Union, Optional


def create_dot_masking(
        sparsity: float) -> Dict[str, Union[str, List[str], Dict]]:
    normalized_sparsity = sparsity * 1.5 + 0.05

    effect_config = {
        "effect_config": {
            "segments": "rand",
        },
        "snake": {
            "head": {
                "const_value": {
                    "value": 1.0,
                }
            },
            "tail": {
                "const_value": {
                    "value": normalized_sparsity,
                }
            }
        }
    }
    return effect_config


def create_round_masking(
        sparsity: float) -> Dict[str, Union[str, List[str], Dict]]:
    normalized_sparsity = sparsity * 1.5 + 0.05

    effect_config = {
        "effect_config": {
            "segments": "arc",
        },
        "snake": {
            "head": {
                "const_value": {
                    "value": 1.0,
                }
            },
            "tail": {
                "const_value": {
                    "value": normalized_sparsity,
                }
            }
        }
    }
    return effect_config
