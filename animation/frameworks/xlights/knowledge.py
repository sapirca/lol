"""
XLights Knowledge Base

This module contains information about the colors in XLights, the structure of the animation file (.xsq), and the allowed effects.
"""


# Colors in XLights
def colors_in_xlights():
    """
    Colors in XLights:
    - Colors can be specified using RGB values.
    - The format for specifying colors is a tuple of three integers, each ranging from 0 to 255.
    - Example: (255, 0, 0) represents the color red.
    - Hexadecimal color codes are also supported. Example: #FF0000 for red.
    - Named colors are supported as well. Example: "red", "green", "blue".
    """
    pass


# Structure of the animation file (.xsq)
def structure_of_xsq_file():
    """
    Structure of the animation file (.xsq):
    - The .xsq file is an XML-based format used by XLights to store animation sequences.
    - The root element is <xsequence>.
    - The <head> element contains metadata such as version and author.
    - The <steps> element contains a list of <step> elements, each representing a frame in the animation.
    - Each <step> element contains:
        - <number>: The frame number.
        - <animation>: The name of the animation effect.
        - <color>: The color used in the animation.
        - <timing>: The duration of the frame.
    """
    pass


# Allowed effects in XLights
def allowed_effects_in_xlights():
    """
    Allowed effects in XLights:
    - XLights supports a variety of effects that can be applied to animations.
    - Some of the allowed effects include:
        - "On": Turns the lights on.
        - "Off": Turns the lights off.
        - "Twinkle": Creates a twinkling effect.
        - "Chase": Creates a chasing light effect.
        - "Fade": Gradually changes the brightness of the lights.
        - "Sparkle": Creates a sparkling effect.
        - "Rainbow": Displays a rainbow effect.
        - "Wave": Creates a wave-like motion.
    """
    pass
