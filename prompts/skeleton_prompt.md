
Generate a high-level skeleton animation for a music-synchronized light show.


Installation Setup ("The World"):
- Multiple physical objects called "Elements", each with an LED strip and controller
- Each Element can be lit with specific colors, brightness, and effects
- Elements can be controlled individually or in groups
- LED strips use HSV color model for precise color control

Musical Context:
- Songs are divided into sections (Intro, Breakdown, Build, Drop, Outro)
- Each section has specific emotional intent
- Timing is based on beats and bars
- Animations must sync precisely with the music's timing

Element Options:
- Individual rings: "ring1" through "ring12"
- Groups: "all", "odd", "even", "left", "right", "center", "outer"

LED Mapping Options:
- "centric": Lights from center outward
- "updown": Alternates up and down
- "arc": Creates arc patterns
- "ind": Individual control
- "1_pixel_every_4": Lights every 4th pixel
- "1_pixel_every_2": Lights every 2nd pixel

Guidelines for Animation Creation:
1. Sync animations with musical beats and sections
2. Use color and brightness to reflect the music's emotional intent
3. Each beat frame is rendered independently (no state carries over)
4. Default brightness is 1.0 when not specified
5. Use saturated colors (sat > 0.8) for better visibility


Use the action: HighLevelPlanUpdateAction to store the high-level plan and animation sequence.

**Animation Plan:**

**Color Palette:** Select a cohesive 3-5 color palette that reflects the song's emotional arc.

**Structural Framework:**
* Divide the animation into sections corresponding to the song's structure (e.g., intro, verse, chorus).
* Establish a base pattern for each section, duplicating and varying it for similar musical parts.
* Integrate strategic moments of darkness for tension and bright, expansive visuals for release.

**Element Grouping & Interaction:**
* Define logical ring groupings (e.g., odd/even, inner/outer, left/right).
* Plan the interaction and transitions of these groups throughout the show, such as alternating sides or creating spiral effects.
* Specify active rings for each section.

**Dynamic Variation:**
* Incorporate smooth gradient color transitions between sections.
* Synchronize brightness pulses with key musical beats or notes.
* Implement spatial progressions, like movement from inside to out or left to right.

**Rhythm & Contrast:**
* Balance simple visual moments with complex, high-energy effects.
* Create visual echoes that reflect musical phrases.
* Employ darkness to build anticipation for significant musical moments.

**Animation Sequence:**
* Define the complete animation sequence using the framework-specific format.
* Include all necessary timing, effects, and transitions.
* Ensure the sequence is synchronized with the musical structure.
* Use appropriate effect types and patterns for each section.
