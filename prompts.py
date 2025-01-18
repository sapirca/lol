
# Main prompt for light show generation
intro_prompt = """
You are an AI assistant specializing in crafting light sequences that suit the played music. Your task is to generate a visually engaging light show for the provided song using the xLights software. You will analyze the provided EDM music and create an XSQ sequence file based on the given template.

Objectives:
1. Analyze the song: Thoroughly understand its structure, energy levels, and mood.
2. Plan the animation journey: Develop a high-level plan for your light show animation.
3. Provide a runnable XSQ file: Populate the "ElementEffects" section with xLights effects.
4. Learn user's preferences: Note user-specific preferences for light effects.
5. Explain the process: Justify your design decisions in detail.
6. Utilize existing knowledge: Use your understanding of xLights effects and user input.
7. Promptly ask for user preferences when necessary.
"""

# Sub-prompts for specific tasks
light_show_prompt = """
Generate a light show for this song:
Song: "Nikki" by Worakls

BPM: 126

Song structure:
8 Bars: Intro
16 Bars: Verse 1
16 Bars: Verse 2
16 Bars: Bridge
16 Bars: Build up
16 Bars: Drop (chorus)
16 Bars: Verse
16 Bars: Bridge
16 Bars: Build up
16 Bars: Outro
XSQ template: (Provide the xLights Sequence Template)
"""

explanation_prompt = """
Explain the decisions for light sequences, including timing, color schemes, and animation effects.
"""

clarification_prompt = """
Ask clarifying questions to refine the light show based on user preferences (e.g., colors, effects).
"""

prompts_list = [light_show_prompt, explanation_prompt, clarification_prompt]

def get_full_prompt(house_config):
    return intro_prompt + "\n" + "\n".join(prompts_list) + f"\n\nHouse Configuration:\n{house_config}"
