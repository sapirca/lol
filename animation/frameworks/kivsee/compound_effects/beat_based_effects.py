import json
from typing import List, Dict, Union, Optional


def create_breath_effect_by_the_beat(
        start_time_ms: int, end_time_ms: int,
        bpm: int) -> Dict[str, Union[str, List[str], Dict]]:
    duration_ms = end_time_ms - start_time_ms
    beats_per_second = bpm / 60
    beats_per_duration_ms = 1000 / beats_per_second

    repeat_num = duration_ms / beats_per_duration_ms

    repeat_num_by_the_beat = repeat_num / 2

    effect_config = {
        "brightness": {
            "mult_factor": {
                "sin": {
                    "min": 0.0,
                    "max": 1.0,
                    "phase": 0.25,
                    "repeats": repeat_num_by_the_beat,
                }
            },
        },
    }
    return effect_config


def create_blink_effect_by_the_beat(
        start_time_ms: int, end_time_ms: int,
        bpm: int) -> Dict[str, Union[str, List[str], Dict]]:
    duration_ms = end_time_ms - start_time_ms
    beats_per_second = bpm / 60
    beats_per_duration_ms = 1000 / beats_per_second

    repeat_num = duration_ms / beats_per_duration_ms

    effect_config = {
        "brightness": {
            "mult_factor": {
                "repeat": {
                    "numberOfTimes": repeat_num,
                    "funcToRepeat": {
                        "half": {
                            "f1": {
                                "const_value": {
                                    "value": 1.0,
                                }
                            },
                            "f2": {
                                "const_value": {
                                    "value": 0.0,
                                }
                            }
                        }
                    },
                }
            },
        },
    }
    return effect_config


def create_blink_and_fade_out_effect_by_the_beat(
        start_time_ms: int, end_time_ms: int,
        bpm: int) -> Dict[str, Union[str, List[str], Dict]]:
    duration_ms = end_time_ms - start_time_ms
    beats_per_second = bpm / 60
    beats_per_duration_ms = 1000 / beats_per_second

    repeat_num = duration_ms / beats_per_duration_ms

    effect_config = {
        "brightness": {
            "mult_factor": {
                "repeat": {
                    "numberOfTimes": repeat_num,
                    "funcToRepeat": {
                        "linear": {
                            "start": 1.0,
                            "end": 0.0,
                        }
                    },
                },
            },
        },
    }
    return effect_config


def create_fade_in_and_disappear_effect_by_the_beat(
        start_time_ms: int, end_time_ms: int,
        bpm: int) -> Dict[str, Union[str, List[str], Dict]]:
    duration_ms = end_time_ms - start_time_ms
    beats_per_second = bpm / 60
    beats_per_duration_ms = 1000 / beats_per_second

    repeat_num = duration_ms / beats_per_duration_ms

    effect_config = {
        "brightness": {
            "mult_factor": {
                "repeat": {
                    "numberOfTimes": repeat_num,
                    "funcToRepeat": {
                        "linear": {
                            "start": 0.0,
                            "end": 1.0,
                        }
                    },
                },
            },
        },
    }
    return effect_config


def create_soft_pulse_effect(
        start_time_ms: int, end_time_ms: int, intensity: float,
        bpm: int) -> Dict[str, Union[str, List[str], Dict]]:
    duration_ms = end_time_ms - start_time_ms
    beats_per_second = bpm / 60
    beats_per_duration_ms = 1000 / beats_per_second

    repeat_num = duration_ms / beats_per_duration_ms
    intensity_normalized = max(min(intensity, 0.0), 1.0)
    min_intensity = 1.0 - intensity_normalized
    repeat_num_by_the_beat = repeat_num / 2
    effect_config = {
        "brightness": {
            "mult_factor": {
                "sin": {
                    "min": min_intensity,
                    "max": 1.0,
                    "phase": 0.0,
                    "repeats": repeat_num_by_the_beat
                }
            }
        }
    }
    return effect_config


def create_strobe_effect(start_time_ms: int, end_time_ms: int,
                         bpm: int) -> Dict[str, Union[str, List[str], Dict]]:
    duration_ms = end_time_ms - start_time_ms
    beats_per_second = bpm / 60
    beats_per_duration_ms = 1000 / beats_per_second

    repeat_num = duration_ms / beats_per_duration_ms

    effect_config = {
        "brightness": {
            "mult_factor": {
                "repeat": {
                    "numberOfTimes": repeat_num,
                    "funcToRepeat": {
                        "half": {
                            "f1": {
                                "half": {
                                    "f1": {
                                        "half": {
                                            "f1": {
                                                "const_value": {
                                                    "value": 1.0
                                                }
                                            },
                                            "f2": {
                                                "const_value": {
                                                    "value": 0.0
                                                }
                                            },
                                        }
                                    },
                                    "f2": {
                                        "const_value": {
                                            "value": 0.0
                                        }
                                    },
                                }
                            },
                            "f2": {
                                "const_value": {
                                    "value": 0.0
                                }
                            },
                        }
                    }
                }
            }
        }
    }
    return effect_config


def create_fade_in_out_effect(
        start_time_ms: int, end_time_ms: int,
        bpm: int) -> Dict[str, Union[str, List[str], Dict]]:
    duration_ms = end_time_ms - start_time_ms
    beats_per_second = bpm / 60
    beats_per_duration_ms = 1000 / beats_per_second

    repeat_num = duration_ms / beats_per_duration_ms

    effect_config = {
        "brightness": {
            "mult_factor": {
                "repeat": {
                    "numberOfTimes": repeat_num,
                    "funcToRepeat": {
                        "half": {
                            "f1": {
                                "linear": {
                                    "start": 0.0,
                                    "end": 1.0
                                }
                            },
                            "f2": {
                                "linear": {
                                    "start": 1.0,
                                    "end": 0.0
                                }
                            },
                        }
                    }
                }
            }
        }
    }
    return effect_config
