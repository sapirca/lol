# song_structure_prompt = """
# Song Structure: Possible sections include:
# - Intro: Beginning, sets tone. Often instrumental, gradually increasing intensity. Evokes curiosity, anticipation.
# - Verse: Tells story, lyrics change. Builds anticipation for chorus. Evokes intrigue, connection.
# - Chorus: Most memorable part, repeating lyrics/melody. Highest energy. Evokes excitement, joy.
# - Bridge: Contrasting section, different melody/feel. Often quieter. Evokes reflection, anticipation of change.
# - Build-up: Gradually increases tension, anticipation. Increasing energy, leading to drop. Evokes excitement, suspense. Often ends with silence/pause before drop.
# - Drop: Explosive section after build-up, energy peaks. Climax, most intense. Heavy bass, strong rhythms. Evokes euphoria, release.
# - Outro: Ending, provides closure. Often fades out or mirrors intro. Evokes reflection, nostalgia.

# Build-ups and drops are crucial in EDM, creating dynamic shifts. Animation should reflect this.
# """

music_knowledge_prompt = """
General Music Knowledge:
Intro
Purpose: The introduction sets the tone, mood, and often the tempo and key of the song. It grabs the listener's attention and prepares them for what's to come.
Characteristics: Intros can be instrumental, feature a vocal ad-lib, or a stripped-down version of the main melody or chords. They might foreshadow elements from later in the song or be completely unique to build interest.
Typical Length: Usually short, around 4 to 8 bars, though they can vary.
Verse
Purpose: The verse tells the story of the song, developing the narrative or presenting different aspects of the song's theme.
Characteristics: Verses typically have the same melody and musical structure, but different lyrics each time they appear. They build towards the chorus.
Typical Length: Commonly 8 to 16 bars.
Pre-Chorus (or Lift/Build-up)
Purpose: An optional section that creates tension and builds anticipation for the chorus. It acts as a bridge between the verse and the chorus, often raising the energy level.
Characteristics: The pre-chorus often has a different melody or chord progression from the verse, designed to lead smoothly into the chorus. It might increase in rhythmic intensity or dynamics.
Typical Length: Usually shorter than a verse or chorus, often 4 to 8 bars.
Chorus
Purpose: The core message and most memorable part of the song. It's the "hook" that listeners will remember and sing along to.
Characteristics: The chorus typically has the same lyrics and melody each time it appears. It's often the most energetic and musically "full" section, summing up the main idea or emotion of the song. The song's title is frequently found in the chorus.
Typical Length: Commonly 8 to 16 bars.
Breakdown
Purpose: A section where the music becomes sparser, often stripping back elements to create a sense of release or to build anticipation for a new section, particularly in electronic music.
Characteristics: Drums might drop out, or the instrumentation might be significantly reduced. It can provide a moment of calm or a shift in focus before a re-energized section. It might feature a prominent melodic idea or vocal solo.
Usage: Very common in EDM (Electronic Dance Music) and pop, where it leads into a "build" and then a "drop."
Build (or Build-up)
Purpose: To gradually increase energy and tension, leading towards a climactic moment, usually the "drop" or another chorus.
Characteristics: Characterized by increasing rhythmic complexity (e.g., faster hi-hats, snare rolls), rising synth sounds (risers), intensifying harmonies, and increasing volume.
Usage: Predominant in EDM, but also found in pop and rock to create impactful transitions.
Drop
Purpose: The energetic peak of the song, particularly in EDM. It's the "payoff" after the build-up, where the main beat, bassline, and lead melodies hit hard.
Characteristics: Often features a heavy bass, strong drums, and a prominent, catchy synth or instrumental hook. It's designed to be the part that makes people want to dance or feel the most excitement. In pop music, this can be less of a distinct "drop" and more just the most impactful part of the chorus.
Usage: Central to EDM, often serving as the equivalent of a pop chorus in terms of memorability and impact.
Bridge
Purpose: The bridge provides a contrast to the repeating verse and chorus sections. It offers a new musical and lyrical perspective, preventing the song from becoming monotonous.
Characteristics: The bridge typically has different lyrics, melody, and often a different chord progression or even a key change. It often builds emotion or offers a new angle on the song's theme before returning to the familiar chorus. It may also feature an instrumental solo.
Typical Length: Often 4 to 8 bars, sometimes referred to as the "middle eight."
Outro
Purpose: The outro brings the song to a satisfying conclusion, signaling that the song is ending.
Characteristics: It can be a fade-out of the chorus, a repetition of a lyrical or instrumental hook, a slowing down of the tempo, or a distinct new musical passage. It should leave a lasting impression.
Typical Length: Varies widely, from a few seconds to a minute or more depending on the song and genre.
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

# color_knowledge_prompt = """
# Color Knowledge:

# Color Harmony:
# - Complementary: Opposite on color wheel (e.g., red/green).
# - Analogous: Adjacent on color wheel (e.g., blue, blue-green, green).
# - Triadic: Three colors equally spaced (e.g., red, yellow, blue).

# Color Temperature:
# - Warm (red, orange, yellow): Energy, excitement, warmth, comfort.
# - Cool (blue, green, purple): Calmness, relaxation, serenity.
# - Neutral (white, gray, beige): Balance, neutrality, modern, minimalist.

# Colors and Moods:
# - Warm: Energy, excitement.
# - Cool: Calmness, serenity.
# - Bright/playful (pink, turquoise, lime): Fun, quirky atmospheres.

# Use colors to evoke emotions and match music's mood.
# """

# knowledge_prompts = [
#     song_structure_prompt, timing_knowledge_prompt, color_knowledge_prompt
# ]

knowledge_prompts = [timing_knowledge_prompt]
