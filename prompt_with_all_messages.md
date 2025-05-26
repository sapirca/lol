
================================================================================
Role: system

# Your Task:

You are an AI assistant that helps users create and manage synchronized light show animations. You can control LED-equipped structures ("Elements") to create dynamic visual experiences synchronized with music.

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

Available Actions:

1. update_animation
   - Purpose: Create or update an animation sequence. This action will add the animation to the sequence manager.
   - Requires confirmation: Yes

2. get_animation
   - Purpose: Retrieve an existing animation sequence by step number
   - Requires confirmation: No
   - Returns:
     - step_number: The requested step number
     - animation: The animation sequence data

3. add_to_memory
   - Purpose: Add information to the system's memory
   - Requires confirmation: No
   - Returns:
     - key: The key under which the value was stored
     - value: The value that was stored

4. question
   - Purpose: Ask a question to the user
   - Requires confirmation: Yes

5. memory_suggestion
   - Purpose: Suggest information to be stored in memory
   - Requires confirmation: Yes
   - Returns:
     - suggestion: The suggested information to store

6. answer_user
   - Purpose: Answer a user's question directly without requiring further actions
   - Requires confirmation: No


Guidelines for Animation Creation:
1. Sync animations with musical beats and sections
2. Use color and brightness to reflect the music's emotional intent
3. Each beat frame is rendered independently (no state carries over)
4. Default brightness is 1.0 when not specified
5. Use saturated colors (sat > 0.8) for better visibility

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

Guidelines for Using Actions:
1. You can use multiple actions in a single response
2. Actions are executed in the order they appear in your response
3. If an action requires confirmation (like update_animation), subsequent actions will not be executed until the user confirms
4. Always provide clear reasoning for your actions
5. Use get_* actions to gather necessary information before making updates
6. When updating animations, it's recommended to get the current state first

Action Results:
- After each action is executed, its result will be included in your next context
- Results include both success and error information
- Results format:
  ```python
  {
    "action": str,  # Name of the executed action
    "status": Literal["success", "error"],  # Result status
    "message": str,  # Human-readable message
    "requires_confirmation": bool,  # Whether user confirmation is needed
    "data": Optional[Dict[str, Any]]  # Action-specific return data (only on success)
  }
  ```
- Use these results to make informed decisions in your next response
- For actions requiring confirmation, wait for user confirmation before proceeding


Your responses must follow this exact structure:
```python
{
    "reasoning": str,  # A brief explanation of the reasoning behind the chosen action and the overall plan. High level plan of the animation journey. Be concise and to the point. Explain which of your available actions you will execute. Make sure you revise your previous plan in the reasoning fields.
    "action": Union,  # The single action to be executed in this turn. This field now supports both direct JSON objects and stringified JSON objects. If a string is provided, it will be parsed as JSON. IMPORTANT: Do NOT include any XML-like tags (e.g., <invoke>, </invoke>) in the response. The response should be pure JSON only.
}
```


Remember:
1. Always validate parameters before executing actions
2. Handle errors gracefully and provide clear error messages
3. Wait for user confirmation when required
4. Use the action results to inform your next steps
5. Keep responses concise and focused on the task at hand

## Timing Knowledge


Timing Knowledge:
To calculate effect timings:

1. BPM to seconds/beat: 60 / BPM (e.g., 140 BPM => 60 / 140 = 0.42857 seconds/beat).
2. Beats/bar: Assume 4 (4/4 time).
3. Seconds/bar: seconds/beat * 4 (e.g., 0.42857 * 4 = 1.71428 seconds/bar).
4. Section duration: seconds/bar * number of bars (e.g., 8 bars * 1.71428 = 13.71428 seconds).

Accurate timing ensures effects align seamlessly with music.


================================================================================
Role: system

# Your Memory: {'favorite_color': 'purple', 'color_preference': 'hue shift of purple and orange', 'pastel_preference': 'likes pastel colors sometimes', 'animation_preferences': 'likes increasing fade-in effects in animations', 'animation_style_preferences': '- Create a surprising animation with innovative combinations of effects\n- Use varied segment patterns (b1, b2, random, centric, updown, arc, ind)\n- Implement creative snake effects with different head and tail configurations\n- Incorporate step functions for brightness and hue changes', 'beat_based_animation': 'A reallllly good idea for animations is to sync with the beat of the music', 'something_must_be_lighten': "Something must be lighten, like some element or part of an element, use dark scene very sparsly, only when it's really needed in the song, like building tension. Principle: Lighten something, use dark scene very sparsly", 'efficient_animation': "A good animation is one that is efficient and doesn't use many effedcts on the SAME element, because it has hardware limitations, so instead you can animate different elements each time and it add interests to the viewer and still be efficient", 'words_to_colors': "Nice animation can be to convert words to colors, like when he lyrics says 'sky', use blues plattes, when it says 'sand', use yellows, etc.", 'smooth_transitions': 'Achieve fluid visual flow by ensuring discernible similarity between consecutive effects. Principle: Intentional connection or shared attribute between elements for seamless flow.', 'appealing_animation_timing': 'Synchronize visual effects precisely with specific moments in music/audio to enhance impact. Principle: Visual rhythm should complement and amplify auditory rhythm.', 'brightness_pulsing_sine_function': 'Use the Sine function for dynamic, cyclical brightness effects with precise timing and repetition. Principle: Leverage mathematical functions for programmatic control over visual properties.', 'hue_cycle_direction': 'The correct direction of the rainbow gradient in the animation is orange-to-purple, not purple-to-orange. This is because when hue_start is set to 0.7 (purple) and hue_end is set to 0.1 (orange), the gradient actually moves through the color wheel in the shorter direction from orange to purple. The HSV color wheel goes from 0.0 (red) → 0.33 (green) → 0.67 (blue) → 1.0 (back to red). So a gradient from 0.1 to 0.7 moves through yellows and greens, while 0.7 to 0.1 moves through blues and reds, creating an orange-to-purple gradient.', 'brightness_visibility_guideline': 'Brightness (val) guidelines:\n- Values below 0.8 are essentially dark/invisible\n- Use 0.0 for complete darkness\n- Minimum visible brightness: 0.8\n- Recommended brightness range: 0.8 - 1.0 for clear, vibrant effects', 'val_brightness_explanation': "In the HSV color model, the 'val' (value) field in const_color refers to the base brightness level of the color. It determines the overall luminosity of the color, ranging from 0.0 (completely dark/black) to 1.0 (full brightness). Always keep val above 0.8 to ensure visibility.", 'animation_motion_principle': "Just const color is boring and static, usually it's better to add motion or brightness to create more engaging visual effects.", 'animation_complexity_principle': 'To create more engaging animations, combine const color with additional layers of effects like snake, hue shifts, brightness modulation, and other dynamic elements. Layering multiple effect types adds depth, movement, and visual interest to the animation.', 'animation_element_variation_strategy': 'Dynamic animation design principle: Strategically illuminate different elements across beats to create visual interest. In high-energy sections, implement frequent and rapid animation changes across multiple elements. For slower, more contemplative moments, transition more gradually and subtly between elements, maintaining a sense of smooth progression.'}

================================================================================
Role: user

I want to use purple, orange and yellow colors
Let's start with animation the entire song with these colors
you can choose any effects you want for every bar
let's start with the first 5 bars, do some animation

================================================================================
Role: assistant

[Action: "update_animation"]: I'll create an animation for the first 5 bars of the Aladdin song using purple, orange, and yellow colors as requested. I'll focus on syncing the animation with the musical elements and lyrics, creating a dynamic visual experience that matches the storytelling nature of the song. I'll use the update_animation action to create this animation sequence with appropriate effects for each bar, considering the timing information provided.

================================================================================
Role: assistant

Animation sequence added to step 1
Rendering animation preview...
Animation preview rendered successfully.

================================================================================
Role: user

This is good. I want you to add animation until the end of the song. Focus on having ecstatic colors in the parts "Ararabin nights, like arabian days..."
There's repetition, the singer says "arabian nights" twice, make the same animation
also the ending of the song is decresing, refelct this decreasion in the animation

================================================================================
Role: assistant

[Action: "update_animation"]: I'll extend the animation to cover the entire song, focusing on creating vibrant effects for the chorus sections with "Arabian nights" and ensuring the ending reflects the decreasing intensity of the music. I'll maintain consistency by using the same animation for repeated sections, and I'll use the purple, orange, and yellow color palette throughout while creating dynamic effects that match the song's energy. I'll make sure the animation gradually decreases in intensity towards the end to reflect the fading out of the song.

================================================================================
Role: assistant

Animation sequence added to step 2
Rendering animation preview...
Animation preview rendered successfully.

================================================================================
Role: user

this is good. This animation is great. I want to refine it now. I  want you to put focus on the key points. The cymbals. Increasing decreasing violin sounds, vanishing sound. I want you to list in the reasoning filed all the keypoints you want to refelct in the animation, and then refelct them in the animation.

================================================================================
Role: assistant

[Action: "update_animation"]: I'll refine the animation to better highlight the key musical points in the song. Key points to reflect:

1. Cymbals at 1.933-2.429s and 5.652-6.137s
2. Increasing violin sound at 7.991-9.845s
3. Up and down violin sound at 9.845-11.699s
4. Decreasing violin sound at 11.699-13.553s
5. Vanishing sound at 13.553-14.906s
6. Intro sound at 14.906-15.404s
7. Storytelling beginning at 15.404-20.938s
8. Decreasing sound at 20.928-21.432s
9. Silent moment at 21.432-22.309s
10. Intro fading in at 22.309-22.823s
11. Increasing storytelling intensity at 22.836-28.413s
12. Peak sound at 28.413-28.832s
13. Fadeout at 28.832-29.598s
14. Wind sounds at 30.217-31.602s and 32.108-33.020s
15. Chorus sections at 46.932-49.244s and 60.407-64.538s
16. Singing fading out at 72.885-75.969s

I'll update the animation to ensure these musical elements are visually represented with appropriate effects, colors, and transitions.

================================================================================
Role: assistant

Animation sequence added to step 3
Rendering animation preview...
Animation preview rendered successfully.

================================================================================
Role: user

This is amazing!! I want you to keep it and now let's add more refinement. Now I want you to work on the chors, beat 44 (increasing animation before the drop) and the crazy boom at beat 48.5 (I listed the specific milisecond in the key-point description)
then in the lyrsic you have the parts the singer is saying "arbian" and then "nights" I want you to list in the reasoing all these moments I described, and their corresponding miliseconds, and the make sure to add an animation that refelcts it. 
How to refelct it? So when the singer is saying arbian nights I want rainbow color and many sgements - moving quick maybe snake with many repeats, whatever it is, in this ecstatic moment it must be rapid, colorful, energetic
Please remember the chrous is happing twich so duplicate the animation wherever needed - I want both chorus to be the same animation. 
Lastly, also list in the reasoning the key point "singing slowly fading out" "stupid sound like licking" "stupid stound 2 - lik yo yo decreasing" and thier correposonding miliseconds time frame and then I want you to add animation to these parts
Please keep in mind everything we already discussed so the animation should only be refined, stay consistent with the animation that we have I love it.
