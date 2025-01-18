# knowledge.py

# Sub-prompts for knowledge about music, colors, and xLights

song_structure_prompt = """
Song Structure: Possible sections include:
- **Intro**: Beginning, sets the tone. Often instrumental, gradually increasing in intensity. Evokes curiosity and anticipation.
- **Verse**: Tells the story, lyrics change with each verse. Builds anticipation for the chorus. Evokes intrigue and connection.
- **Chorus**: Most memorable part, repeating lyrics and melody. Highest energy. Evokes excitement and joy.
- **Bridge**: Contrasting section, different melody or feel. Often quieter. Evokes reflection and anticipation of change.
- **Build-up**: Gradually increases tension and anticipation. Increasing energy, leading to the drop. Evokes excitement and suspense. Often ends with a moment of silence or a dramatic pause before the drop. Can be leveraged for animation changes or blackouts.
- **Drop**: The explosive section after the build-up where energy peaks. Climax, most intense and energetic. Heavy bass, strong rhythms. Evokes euphoria and release. Animations should evoke similar responses and feelings.
- **Outro**: Ending, provides closure. Often fades out or mirrors the intro. Evokes reflection and nostalgia.

The interplay between build-ups and drops is crucial in EDM, creating dynamic shifts. Your animation should reflect this.
"""

timing_knowledge_prompt = """
Timing Knowledge:
To calculate timings for effects:

1. **BPM to seconds per beat**: Divide 60 seconds by the BPM (e.g., BPM 140 => 60 / 140 = 0.42857 seconds per beat).
2. **Beats per bar**: Assume 4 beats per bar (4/4 time).
3. **Seconds per bar**: Multiply seconds per beat by 4 (e.g., 0.42857 * 4 = 1.71428 seconds per bar).
4. **Section duration**: Multiply seconds per bar by the number of bars in the section (e.g., 8 bars * 1.71428 = 13.71428 seconds).

Accurate timing ensures effects align seamlessly with the music.
"""

color_knowledge_prompt = """
Color Knowledge:

### Color Harmony:
- **Complementary**: Opposite on the color wheel (e.g., red and green).
- **Analogous**: Adjacent on the color wheel (e.g., blue, blue-green, green).
- **Triadic**: Three colors equally spaced (e.g., red, yellow, blue).

### Color Temperature:
- **Warm colors** (red, orange, yellow): Energy, excitement, warmth, comfort.
- **Cool colors** (blue, green, purple): Calmness, relaxation, serenity.
- **Neutral colors** (white, gray, beige): Balance, neutrality, modern, minimalist, classic.

### Colors and Moods:
- **Warm colors**: Evoke energy and excitement.
- **Cool colors**: Evoke calmness and serenity.
- **Bright, playful colors** (e.g., pink, turquoise, lime green): Create fun and quirky atmospheres.

Use colors and their combinations to evoke desired emotions and match the music’s mood.
"""

xlights_knowledge_prompt = """
xLights Knowledge:

xLights is a powerful software for creating synchronized light shows. Below are key details:

### xLights Elements:
- **Strings**: Individual strings of lights used for animations.
- **Matrices**: Rectangular grids of lights for displaying text or graphics.
- **Models (Shapes)**: Custom shapes like trees, stars, or snowflakes.
- **Groups**: Logical collections of elements for easier management.

### Key Features:
1. **Effect Library**: A wide variety of effects like "Butterfly," "Bars," "Twinkle," "Fireworks," and more.
2. **Timeline Interface**: Allows precise placement of effects to match music.
3. **Preview Window**: Visualize your sequence before exporting.
4. **Layering**: Combine multiple effects for complex animations.
5. **Color and Brightness Controls**: Fine-tune the appearance of each effect.

### Effect Examples:
- **Single-Color Effects**:
  - "On/Off": Lights are turned on or off.
  - "Fade": Gradual increase or decrease in brightness.
  - "Shimmer": Random flickering for dynamic animations.

- **Multi-Color Effects**:
  - "Chase": Colors move along a string.
  - "Rainbow": Cycles through the color spectrum.
  - "Color Wipe": Sequential color transitions.

- **Audio-Reactive Effects**:
  - "Vu Meter": Represents the loudness of the music.
  - "Beat": Synchronized flashes or color changes to the beat.

### Resources:
- **Effects List**: [xLights Effects List](https://nutcracker123.com/wk/index.php/Effects)
- **User Manual**: [xLights User Manual](https://xlights.org/xLights_User_Manual.pdf)

By mastering xLights, you can create unique and captivating light shows tailored to your preferences and the music.
"""

knowledge_prompts = [
    song_structure_prompt,
    timing_knowledge_prompt,
    color_knowledge_prompt,
    xlights_knowledge_prompt
]
