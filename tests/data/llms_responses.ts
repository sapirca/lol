// >>>>>> GPT | LOL
//  "instruction": "Generate animation for beats 0-4 that lit ring1 in const color HUE_PINK"

const testSequence = async () => {
    const testAnimation = new Animation("Pink Ring Animation", 128, 4); // 4 beats
    testAnimation.sync(() => {
        beats(0, 4, () => {
            elements([1], () => {  // Only target Ring 1
                constColor(0.9, 1.0, 1.0);  // HUE_PINK (approximately 0.9 in Hue)
            });
        });
    });

    await sendSequence("sandstorm", testAnimation.getSequence());
    await startSong("sandstorm");
};

(async () => {
    await testSequence();
})();

// >>>>>> Gemini | Web
//  "instruction": "Generate animation for beats 0-4 that lit ring1 in const color HUE_PINK"

{
    "animation": {
        "name": "Ring1_Pink_Animation",
            "duration": 4,
                "beats": [
                    {
                        "time_start": 0,
                        "time_end": 4,
                        "elements": {
                            "ring1": {
                                "coloring": {
                                    "type": "constColor",
                                    "hue": 300
                                },
                                "brightness": {
                                    "type": "fadeIn",
                                    "start": 0,
                                    "end": 1
                                },
                                "motion": {
                                    "type": "snake"
                                }
                            }
                        }
                    }
                ]
    }
}

// >>>>>> GPT | Web
//  "instruction": "Generate animation for beats 0-4 that lit ring1 in const color HUE_PINK"

{
    "animation": {
        "name": "<song_name_provided_by_user>",
            "duration": "<total_duration_of_song_in_seconds>",
                "beats": [
                    {
                        "time_start": 0,
                        "time_end": 4,
                        "elements": {
                            "ring1": {
                                "coloring": {
                                    "type": "constColor",
                                    "hue": "HUE_PINK"
                                }
                            }
                        }
                    }
                ]
    }
}

// >>>>>> GPT | LOL
// Generate animation for beats 0-4 that lit ring1 in const color HUE_PINK, song name is pink_const_color_ring1, duration 100 secs

const testSequence = async () => {
    const testAnimation = new Animation("pink_const_color_ring1", 126, 100); // 100 seconds duration
    testAnimation.sync(() => {
        beats(0, 4, () => { // Covering beats 0-4
            elements([1], () => { // Activating Ring 1
                constColor(0.9, 1.0, 1.0); // HUE_PINK (Hue: 0.9, Saturation: 1.0, Value: 1.0)
            });
        });
    });

    await sendSequence("pink_const_color_ring1", testAnimation.getSequence());
    await startSong("pink_const_color_ring1");
};

(async () => {
    await testSequence();
})();

// >>>>>> DeepSeek | LOL
// Generate animation for beats 0-4 that lit ring1 in const color HUE_PINK, song name is pink_const_color_ring1, duration 100 secs

const pinkConstColorRing1 = async () => {
    const animation = new Animation("pink_const_color_ring1", 128, 100);
    animation.sync(() => {
        beats(0, 4, () => {
            elements(1, () => {
                constColor(0.9167, 1.0, 1.0); // HUE_PINK (0.9167), full saturation (1.0), full brightness (1.0)
            });
        });
    });

    await sendSequence("pink_const_color_ring1", animation.getSequence());
    await startSong("pink_const_color_ring1");
};

(async () => {
    await pinkConstColorRing1();
})();



// >>>>>> Gemini | Web
// Generate animation that lit ALL elements in const color BLUE for the entire duration of the song, which is 10 seconds, BPM 120

{
    "animation": {
        "name": "All_Blue_Animation",
            "duration": 10,
                "beats": [
                    {
                        "time_start": 0,
                        "time_end": 10,
                        "elements": {
                            "element1": {
                                "coloring": {
                                    "type": "constColor",
                                    "hue": 240
                                },
                                "brightness": {
                                    "type": "fadeIn",
                                    "start": 0,
                                    "end": 1
                                },
                                "motion": {
                                    "type": "snake"
                                }
                            },
                            "element2": {
                                "coloring": {
                                    "type": "constColor",
                                    "hue": 240
                                },
                                "brightness": {
                                    "type": "fadeIn",
                                    "start": 0,
                                    "end": 1
                                },
                                "motion": {
                                    "type": "snake"
                                }
                            },
                            "element3": {
                                "coloring": {
                                    "type": "constColor",
                                    "hue": 240
                                },
                                "brightness": {
                                    "type": "fadeIn",
                                    "start": 0,
                                    "end": 1
                                },
                                "motion": {
                                    "type": "snake"
                                }
                            },
                            "element4": {
                                "coloring": {
                                    "type": "constColor",
                                    "hue": 240
                                },
                                "brightness": {
                                    "type": "fadeIn",
                                    "start": 0,
                                    "end": 1
                                },
                                "motion": {
                                    "type": "snake"
                                }
                            },
                            "element5": {
                                "coloring": {
                                    "type": "constColor",
                                    "hue": 240
                                },
                                "brightness": {
                                    "type": "fadeIn",
                                    "start": 0,
                                    "end": 1
                                },
                                "motion": {
                                    "type": "snake"
                                }
                            }
                        }
                    }
                ]
    }
}

// >>>>>> GPT | Web
// Generate animation that lit ALL elements in const color BLUE for the entire duration of the song, which is 10 seconds, BPM 120
{
    "animation": {
        "name": "all_blue_constant",
            "duration": 10,
                "beats": [
                    {
                        "time_start": 0,
                        "time_end": 20,
                        "elements": {
                            "ALL": {
                                "coloring": {
                                    "type": "constColor",
                                    "hue": "HUE_BLUE"
                                }
                            }
                        }
                    }
                ]
    }
}


// >>>>>> GPT | LOL
// Generate animation that lit ALL elements in const color BLUE for the entire duration of the song, which is 10 seconds, BPM 120

const blueConstantColorAnimation = async () => {
    const durationInSeconds = 10; // Total duration of the song in seconds
    const bpm = 120; // BPM of the song
    const totalBeats = (durationInSeconds * bpm) / 60; // Calculate total beats based on duration

    const animation = new Animation("blue_constant_color_all_elements", bpm, durationInSeconds);
    animation.sync(() => {
        beats(0, totalBeats, () => {
            elements(all, () => {
                constColor(0.6, 1.0, 1.0); // Constant color BLUE (using Hue value for blue)
                // Optional parameters for brightness or fading can be added here if needed
            });
        });
    });

    await sendSequence("blue_constant_color_all_elements", animation.getSequence());
};

(async () => {
    await blueConstantColorAnimation();
})();


// >>>>>> DeepSeek | LOL
// Generate animation that lit ALL elements in const color BLUE for the entire duration of the song, which is 10 seconds, BPM 120

const blueConstColorAnimation = async () => {
    const animation = new Animation("blue_const_color_all", 120, 10);
    animation.sync(() => {
        beats(0, 10, () => {
            elements(all, () => {
                constColor(0.6667, 1.0, 1.0); // HUE_BLUE = 0.6667, full saturation and brightness
            });
        });
    });

    await sendSequence("blue_const_color_all", animation.getSequence());
    await startSong("blue_const_color_all");
};

(async () => {
    await blueConstColorAnimation();
})();

// generate one color for each element
{
    "animation": {
        "name": "Sandstorm (Extended Mix)",
            "duration": 304,
                "beats": [
                    {
                        "time_start": 0,
                        "time_end": 64,
                        "elements": [
                            {
                                "element_group": "all",
                                "coloring": {
                                    "type": "constColor",
                                    "hue": "blue"
                                },
                                "brightness": {
                                    "type": "fadeIn",
                                    "start": 0,
                                    "end": 100
                                },
                                "motion": {
                                    "type": "snake",
                                    "start": 0,
                                    "end": 5
                                }
                            }
                        ]
                    },
                    {
                        "time_start": 64,
                        "time_end": 128,
                        "elements": [
                            {
                                "element_group": "all",
                                "coloring": {
                                    "type": "constColor",
                                    "hue": "green"
                                },
                                "brightness": {
                                    "type": "fadeIn",
                                    "start": 0,
                                    "end": 100
                                },
                                "motion": {
                                    "type": "snake",
                                    "start": 0,
                                    "end": 5
                                }
                            }
                        ]
                    },
                    {
                        "time_start": 128,
                        "time_end": 192,
                        "elements": [
                            {
                                "element_group": "all",
                                "coloring": {
                                    "type": "constColor",
                                    "hue": "yellow"
                                },
                                "brightness": {
                                    "type": "fadeInOut",
                                    "start": 100,
                                    "end": 0,
                                    "min": 10,
                                    "max": 100
                                },
                                "motion": {
                                    "type": "snake",
                                    "start": 0,
                                    "end": 5
                                }
                            }
                        ]
                    },
                    {
                        "time_start": 192,
                        "time_end": 256,
                        "elements": [
                            {
                                "element_group": "all",
                                "coloring": {
                                    "type": "constColor",
                                    "hue": "orange"
                                },
                                "brightness": {
                                    "type": "fadeIn",
                                    "start": 0,
                                    "end": 100
                                },
                                "motion": {
                                    "type": "snake",
                                    "start": 0,
                                    "end": 5
                                }
                            }
                        ]
                    },
                    {
                        "time_start": 256,
                        "time_end": 272,
                        "elements": [
                            {
                                "element_group": "all",
                                "coloring": {
                                    "type": "constColor",
                                    "hue": "purple"
                                },
                                "brightness": {
                                    "type": "blink",
                                    "low": 0,
                                    "high": 100
                                },
                                "motion": {
                                    "type": "snakeInOut",
                                    "start": 0,
                                    "end": 5
                                }
                            }
                        ]
                    },
                    {
                        "time_start": 272,
                        "time_end": 304,
                        "elements": [
                            {
                                "element_group": "all",
                                "coloring": {
                                    "type": "constColor",
                                    "hue": "red"
                                },
                                "brightness": {
                                    "type": "fadeOut",
                                    "start": 100,
                                    "end": 0
                                },
                                "motion": {
                                    "type": "snake",
                                    "start": 0,
                                    "end": 5
                                }
                            }
                        ]
                    }
                ]
    }
}
