# knowledge.py

# Sub-prompts for knowledge about music, colors

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

knowledge_prompts = [
    song_structure_prompt,
    timing_knowledge_prompt,
    color_knowledge_prompt
]
