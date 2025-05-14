intro_prompt = r"""
# Part 1: General Task Explanation

## Objective:

Design a synchronized light show for a specified music track, visualized on a physical art installation composed of LED-equipped structures ("Elements"). The light show should dynamically translate the track's emotional journey into a captivating visual experience.

## Installation Setup ("The World"):

You are provided with a textual description of the physical art installation, detailing the number, type, and arrangement of "Elements" (LED-equipped structures). Each "Element" contains an LED strip and a dedicated controller for independent animation.

## Music Data:

You will be provided with a textual breakdown of the music track, including:

-   Emotional sections (e.g., Intro, Breakdown, Build, Drop, Outro).
-   Beats Per Minute (BPM).
-   Total duration in milliseconds.

## User Input:

The user will specify:

-   Which "Elements" to activate in specific sections.
-   Desired visual effects (e.g., color palettes, brightness patterns, motion effects) in natural description.
-   Specific musical moments to emphasize.
-   Requests for modification of an existing animation.

## Desired Output:

### Reasoning:

A concise explanation of the design choices made, justifying how the light show reflects the music's emotional journey. Explanation of any adjustments or modifications made based on user input.

### Light Sequence (DSL - Domain-Specific Language):

A structured animation plan in JSON format, representing the light show as a sequence of time frames. Each time frame corresponds to a specific musical moment (beat and bar). For each time frame, specify:

-   **Active Elements:** A list of "Elements" to be illuminated.
-   **Effects Applied:** A list of visual effects for each active element (e.g., solid color, rainbow, hue shift, fade, blink, snake, pulse). The effects are rendered in the order they appear, overriding previous effect values. Each time frame starts with empty values (colors, brightness levels, etc.), ensuring a fresh rendering per frame.

## Technical Requirements:

-   **Synchronization:** The light show must be precisely synchronized with the music's beats and bars.
-   **Consistency:** Each time frame's animation must be self-contained and free of contradictory information.
-   **Responsiveness:** The animation must accurately reflect the user's instructions.

### Timing Calculations (for reference):

-   Seconds per Beat: 60 / BPM
-   Seconds per Bar: (60 / BPM) * 4 (assuming a 4/4 time signature)
-   Section Duration: seconds/bar \* number of bars

### LED Strip and Controller Behavior:

-   Each "Element" has a controller that manages its LED strip.
-   Controllers render effects sequentially within each time frame.
-   Effects can be overriding (e.g., color changes) or transformative (e.g., brightness blink).
-   The controller maintains a virtual array representing the LED strip, and after all effects are rendered, that array is pushed to the physical LED strip.
-   Each pixel in the LED array requires three attributes: Hue, Brightness, and Saturation - HSV.

## High-Level Requirements:

-   Lights must align with the music’s beats and bars.
-   Each time frame animation must compile correctly without contradicting information.
-   The animation should reflect the user’s instructions.
-   Changes and updates in the animation must be justified in the reasoning.

## Key Terms:

-   **LED Strip:** A flexible line of pixel lights embedded in a row.
-   **Controller:** A device that manages LED behavior based on programmed sequences.
-   **Element:** A physical structure in the installation, each equipped with a controller and an LED strip.
-   **EDM (Electronic Dance Music):** A genre with structured, predictable beats, enabling precise timing calculations
"""

reversed_task = """
# Part 1: Animation Description from JSON

## Objective:

Given a JSON structure representing an animation sequence for an LED light show, your task is to describe the visual output of each time frame in detail. This involves interpreting the JSON data and translating it into a clear, concise, and human-readable description of the animation.

## Input:

You will be provided with a JSON structure that adheres the provided scheme. 

## Output:

json that contains the time-frames from the original animation, and replace the effects on the elements with text description

"""

# intro_prompt = """
# ### Light Sequence Design Prompt

# #### **Your Task**
# Design a synchronized light sequence for an EDM track, tailored for a physical art installation composed of interactive elements.

# #### **Context**
# - **Art Installation:** A "World" consists of multiple physical objects called **Elements**. Each Element has an LED controller. You will receive the Elements' names and spatial arrangement.
# - **Music:** An EDM track breakdown will be provided, including musical phrases (e.g., Intro, Breakdown, Build, Drop, Outro) and their duration in bars.
# - **Musical Intent:** Each phrase conveys a specific emotional intent:
#   - **Intro:** Evoke intrigue.
#   - **Breakdown:** Build tension.
#   - **Build:** Increase anticipation.
#   - **Drop:** Release explosive energy and excitement.
#   - **Outro:** Provide a sense of closure.
# - **Synchronization:** The light sequence must visually reflect the emotional intent of each phrase.
# - **LED Control:** Each Element can be lit with a specific color and brightness. You can control entire Elements or specific LED segments within the strip.

# #### **Desired Output**
# 1. **Design Rationale:** Briefly explain your design choices and any adjustments made based on user feedback.
# 2. **Light Sequence (DSL):** Provide a structured animation plan where:
#    - Each time frame corresponds to a specific musical moment (bar and beat) in the track.
#    - For each frame, specify:
#      - Which Elements are active.
#      - The coloring effect on each Element (e.g., solid color, rainbow).
#      - Any relevant parameters (e.g., brightness, speed).
#    - Wrap the full sequence within `<animation>` and `</animation>` tags.
#    - The animation format must align with the following framework used for light show simulation:
# """
