song_structure_prompt = """
Song Structure: Possible sections include:
- Intro: Beginning, sets tone. Often instrumental, gradually increasing intensity. Evokes curiosity, anticipation.
- Verse: Tells story, lyrics change. Builds anticipation for chorus. Evokes intrigue, connection.
- Chorus: Most memorable part, repeating lyrics/melody. Highest energy. Evokes excitement, joy.
- Bridge: Contrasting section, different melody/feel. Often quieter. Evokes reflection, anticipation of change.
- Build-up: Gradually increases tension, anticipation. Increasing energy, leading to drop. Evokes excitement, suspense. Often ends with silence/pause before drop.
- Drop: Explosive section after build-up, energy peaks. Climax, most intense. Heavy bass, strong rhythms. Evokes euphoria, release.
- Outro: Ending, provides closure. Often fades out or mirrors intro. Evokes reflection, nostalgia.

Build-ups and drops are crucial in EDM, creating dynamic shifts. Animation should reflect this.
"""

timing_knowledge_prompt = """
Timing Knowledge:
To calculate effect timings:

1. BPM to seconds/beat: 60 / BPM (e.g., 140 BPM => 60 / 140 = 0.42857 seconds/beat).
2. Beats/bar: Assume 4 (4/4 time).
3. Seconds/bar: seconds/beat * 4 (e.g., 0.42857 * 4 = 1.71428 seconds/bar).
4. Section duration: seconds/bar * number of bars (e.g., 8 bars * 1.71428 = 13.71428 seconds).

Accurate timing ensures effects align seamlessly with music.
"""

color_knowledge_prompt = """
Color Knowledge:

Color Harmony:
- Complementary: Opposite on color wheel (e.g., red/green).
- Analogous: Adjacent on color wheel (e.g., blue, blue-green, green).
- Triadic: Three colors equally spaced (e.g., red, yellow, blue).

Color Temperature:
- Warm (red, orange, yellow): Energy, excitement, warmth, comfort.
- Cool (blue, green, purple): Calmness, relaxation, serenity.
- Neutral (white, gray, beige): Balance, neutrality, modern, minimalist.

Colors and Moods:
- Warm: Energy, excitement.
- Cool: Calmness, serenity.
- Bright/playful (pink, turquoise, lime): Fun, quirky atmospheres.

Use colors to evoke emotions and match music's mood.
"""

knowledge_prompts = [
    song_structure_prompt, timing_knowledge_prompt, color_knowledge_prompt
]
