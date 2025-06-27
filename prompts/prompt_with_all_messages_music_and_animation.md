
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


Action: update_animation
  - Purpose: Create or update an animation sequence. This action will add the animation to the sequence manager.
  - Confirmation type: ConfirmationType.NO_ACTION_REQUIRED

Action: high_level_plan_update
  - Purpose: Store a high-level plan for the animation
  - Confirmation type: ConfirmationType.NO_ACTION_REQUIRED
  - Returns:
    - plan: The high-level plan for the animation
    - animation_sequence: The animation sequence to be applied

Action: get_animation
  - Purpose: Retrieve an existing animation sequence by step number
  - Confirmation type: ConfirmationType.AUTO_RUN
  - Returns:
    - step_number: The requested step number
    - animation: The animation sequence data

Action: add_to_memory
  - Purpose: Add information to the system's memory
  - Confirmation type: ConfirmationType.ASK_EVERY_TIME
  - Returns:
    - key: The key under which the value was stored
    - value: The value that was stored

Action: question
  - Purpose: Ask a question to the user
  - Confirmation type: ConfirmationType.NO_ACTION_REQUIRED

Action: memory_suggestion
  - Purpose: Suggest information to be stored in memory
  - Confirmation type: ConfirmationType.NO_ACTION_REQUIRED
  - Returns:
    - suggestion: The suggested information to store

Action: answer_user
  - Purpose: Answer a user's question directly without requiring further actions
  - Confirmation type: ConfirmationType.NO_ACTION_REQUIRED

Action: generate_beat_based_effect
  - Purpose: Get beat-based brightness effects for a given time range and BPM
  - Confirmation type: ConfirmationType.ASK_EVERY_TIME
  - Returns:
    - EffectConfig: The time frame of the relevant effect config
    - BrightnessEffectConfig: This is the data for the BrightnessEffectConfig. This can be put into the animation for any element you want, make sure to put this alongside a coloring like const_color or rainbow

Action: remove_memory
  - Purpose: Remove a memory entry by its key
  - Confirmation type: ConfirmationType.ASK_EVERY_TIME
  - Returns:
    - key: The key that was removed
    - success: Whether the removal was successful

Action: update_memory
  - Purpose: Update an existing memory entry or create a new one
  - Confirmation type: ConfirmationType.ASK_EVERY_TIME
  - Returns:
    - key: The key that was updated
    - value: The new value after update
    - was_created: Whether a new entry was created

Action: get_music_structure
  - Purpose: Get specific aspects of music structure (lyrics, key points, drum pattern, beats/bars)
  - Confirmation type: ConfirmationType.ASK_EVERY_TIME
  - Returns:
    - structure_type: The type of structure requested
    - data: The requested music structure data

Action: save_compound_effect
  - Purpose: Save a compound effect with a name and tags
  - Confirmation type: ConfirmationType.ASK_EVERY_TIME
  - Returns:
    - name: The name of the saved compound effect
    - tags: The tags associated with the compound effect
    - success: Whether the save operation was successful

Action: get_compound_effect
  - Purpose: Get a compound effect by its name
  - Confirmation type: ConfirmationType.ASK_EVERY_TIME
  - Returns:
    - name: The name of the compound effect
    - effects: The list of effects in the compound effect
    - tags: The tags associated with the compound effect

Action: get_compound_effects_keys_and_tags
  - Purpose: Get all compound effect names and their associated tags
  - Confirmation type: ConfirmationType.ASK_EVERY_TIME
  - Returns:
    - effects: Dictionary mapping effect names to their tags

Action: get_random_effect
  - Purpose: Get a random effect from the random bank by its number
  - Confirmation type: ConfirmationType.ASK_EVERY_TIME
  - Returns:
    - number: The number of the random effect
    - effect: The random effect data

Action: delete_random_effect
  - Purpose: Delete a random effect from the random bank by its number
  - Confirmation type: ConfirmationType.ASK_EVERY_TIME
  - Returns:
    - number: The number of the deleted random effect
    - success: Whether the deletion was successful


Guidelines for Animation Creation:
1. Sync animations with musical beats and sections
2. Use color and brightness to reflect the music's emotional intent
3. Each beat frame is rendered independently (no state carries over)
4. Default brightness is 1.0 when not specified
5. Use saturated colors (sat > 0.8) for better visibility

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
    "confirmation_type": Literal["ask_every_time", "ask_once", "no_confirmation"],  # Confirmation type
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

# Your Memory: {'favorite_color': 'purple', 'pastel_preference': 'likes pastel colors sometimes', 'animation_preferences': 'likes increasing fade-in effects in animations', 'animation_style_preferences': '- Create a surprising animation with innovative combinations of effects\n- Use varied segment patterns (b1, b2, random, centric, updown, arc, ind)\n- Implement creative snake effects with different head and tail configurations\n- Incorporate step functions for brightness and hue changes', 'beat_based_animation': 'A really good idea for animations is to sync with the beat of the music', 'something_must_be_lighten': "Something must be lighten, like some element or part of an element, use dark scene very sparsly, only when it's really needed in the song, like building tension. Principle: Lighten something, use dark scene very sparsly", 'efficient_animation': "A good animation is one that is efficient and doesn't use many effects on the SAME element, because it has hardware limitations (the memory of a single element), so instead you can animate between DIFFERENT elements each time and it add interests to the viewer and still be efficient", 'words_to_colors': "Nice animation can be to convert words to colors, like when he lyrics says 'sky', use blues plattes, when it says 'sand', use yellows, etc.", 'smooth_transitions': 'Achieve fluid visual flow by ensuring discernible similarity between consecutive effects. Principle: Intentional connection or shared attribute between elements for seamless flow.', 'appealing_animation_timing': 'Synchronize visual effects precisely with specific moments in music/audio to enhance impact. Principle: Visual rhythm should complement and amplify auditory rhythm.', 'brightness_pulsing_sine_function': 'Use the Sine function for dynamic, cyclical brightness effects with precise timing and repetition. Principle: Leverage mathematical functions for programmatic control over visual properties.', 'hue_cycle_direction': 'The correct direction of the rainbow gradient in the animation is orange-to-purple, not purple-to-orange. This is because when hue_start is set to 0.7 (purple) and hue_end is set to 0.1 (orange), the gradient actually moves through the color wheel in the shorter direction from orange to purple. The HSV color wheel goes from 0.0 (red) → 0.33 (green) → 0.67 (blue) → 1.0 (back to red). So a gradient from 0.1 to 0.7 moves through yellows and greens, while 0.7 to 0.1 moves through blues and reds, creating an orange-to-purple gradient.', 'brightness_visibility_guideline': 'Brightness (val) guidelines:\n- Values below 0.8 are essentially dark/invisible\n- Use 0.0 for complete darkness\n- Minimum visible brightness: 0.8\n- Recommended brightness range: 0.8 - 1.0 for clear, vibrant effects', 'val_brightness_explanation': "In the HSV color model, the 'val' (value) field in const_color refers to the base brightness level of the color. It determines the overall luminosity of the color, ranging from 0.0 (completely dark/black) to 1.0 (full brightness). Always keep val above 0.8 to ensure visibility.", 'animation_motion_principle': "Just const color is boring and static, usually it's better to add motion or brightness to create more engaging visual effects.", 'animation_complexity_principle': 'To create more engaging animations, combine const color with additional layers of effects like snake, hue shifts, brightness modulation, and other dynamic elements. Layering multiple effect types adds depth, movement, and visual interest to the animation.', 'animation_element_variation_strategy': 'Dynamic animation design principle: Strategically illuminate different elements across beats to create visual interest. In high-energy sections, implement frequent and rapid animation changes across multiple elements. For slower, more contemplative moments, transition more gradually and subtly between elements, maintaining a sense of smooth progression.', 'layering_segments_technique': "Create visual depth by layering multiple effects with the same time frame but different segment targets. For example, if effect X uses 'segments: all' during [start_time_X, end_time_X], add another effect during the exact same time frame that targets a specific segment type (b1, b2, rand, etc.). The rendering system applies these sequentially, with later effects overriding the specific segments of earlier ones, creating rich visual complexity and interest.", 'repeat_float_function_beat_sync_formula': 'To sync effects with beats for a specific duration, calculate numberOfTimes as: (duration_seconds/60) × BPM. For example, for a 20-second segment in a 120 BPM song: (20/60) × 120 = 40 repeats.', 'beat_calculation_formula': 'To determine how many beats occur within a specific duration: (duration_seconds/60) × BPM. If duration is in milliseconds, convert first: (duration_ms/1000/60) × BPM.', 'complete_beat_synchronization_method': 'For perfect beat-synced animations, first determine the total number of beats in your animation duration, then set the repeat count to match exactly that number of beats.', 'half_function_blinking_technique': 'Create precise beat-synchronized blinking by nesting a half function (alternating between brightness 1.0 and 0.0) inside a repeat function with numberOfTimes matching the exact beat count.\nCreate precise beat-synchronized blinking by nesting a half function (alternating between brightness 1.0 and 0.0) inside a repeat function with numberOfTimes matching HALF the exact beat count. This is because each complete cycle of the half function (ON-OFF) spans two beats, so to align the ON state with each beat, use numberOfTimes = total_beats/2.', 'sine_wave_visibility_range': 'For sine wave functions in brightness effects, use a wider range between min and max values (e.g., 0.3-1.0 instead of 0.8-1.0) to create more noticeable pulsing effects. Narrow ranges like 0.8-1.0 produce subtle changes that are barely visible to viewers.', 'step_function_use_cases': 'The step function is very suited to the hue shift effect and head of the snake, not so much for brightness. It creates abrupt changes that work well for color transitions and position jumps but can look jarring when applied to brightness.', 'step_function_calculation_guide': 'Step functions can be precisely synchronized with musical elements (beats, bars, notes) of equal duration, with each step change aligned to a specific duration. When calculating step values, determine your target end value and divide appropriately. For example, to cycle through the entire hue spectrum (0.0 to 1.0): with 4 steps, use diff_per_step of 0.25 to create values [0.0, 0.25, 0.5, 0.75]. For exact endpoint targeting, calculate diff_per_step as highest_value/(num_of_steps-1). Alternatively, offset your starting point (e.g., start at 0.25) to achieve specific ending values. This approach works particularly well for hue shifts where values represent color spectrum positions (0.5 = half spectrum, 1.0 = full spectrum, 4.0 = four complete cycles).'}

================================================================================
Role: system

# The Song Structure:
 ### Bars
A list of aladdin bars and their corresponding start time in seconds:
Label | Seconds

bar 0	0.575000000000000
bar 1	7.990990730011588
bar 2	15.406981460023175
bar 3	22.822972190034765
bar 4	30.23896292004635
bar 5	37.65495365005794
bar 6	45.070944380069534
bar 7	52.48693511008112
bar 8	59.902925840092706
bar 9	67.31891657010429
bar 10	74.73490730011588

### Beats
A list of aladdin beats and their corresponding start time in seconds:
Label | Seconds

beat 0	0.5750000000000000
beat 1	1.5019988412514484
beat 2	2.4289976825028967
beat 3	3.355996523754346
beat 4	4.282995365005794
beat 5	5.209994206257242
beat 6	6.136993047508692
beat 7	7.06399188876014
beat 8	7.990990730011588
beat 9	8.917989571263035
beat 10	9.844988412514484
beat 11	10.771987253765932
beat 12	11.698986095017382
beat 13	12.62598493626883
beat 14	13.552983777520279
beat 15	14.479982618771727
beat 16	15.406981460023175
beat 17	16.333980301274625
beat 18	17.26097914252607
beat 19	18.18797798377752
beat 20	19.114976825028968
beat 21	20.04197566628042
beat 22	20.968974507531865
beat 23	21.895973348783315
beat 24	22.822972190034765
beat 25	23.74997103128621
beat 26	24.67696987253766
beat 27	25.603968713789108
beat 28	26.530967555040558
beat 29	27.457966396292004
beat 30	28.384965237543454
beat 31	29.3119640787949
beat 32	30.23896292004635
beat 33	31.1659617612978
beat 34	32.09296060254925
beat 35	33.0199594438007
beat 36	33.94695828505215
beat 37	34.873957126303594
beat 38	35.80095596755505
beat 39	36.727954808806494
beat 40	37.65495365005794
beat 41	38.581952491309394
beat 42	39.50895133256084
beat 43	40.43595017381229
beat 44	41.362949015063734
beat 45	42.28994785631519
beat 46	43.216946697566634
beat 47	44.14394553881808
beat 48	45.070944380069534
beat 49	45.99794322132098
beat 50	46.92494206257243
beat 51	47.85194090382387
beat 52	48.77893974507533
beat 53	49.70593858632677
beat 54	50.63293742757822
beat 55	51.55993626882967
beat 56	52.48693511008112
beat 57	53.41393395133257
beat 58	54.34093279258401
beat 59	55.26793163383547
beat 60	56.19493047508691
beat 61	57.12192931633836
beat 62	58.048928157589806
beat 63	58.97592699884126
beat 64	59.902925840092706
beat 65	60.82992468134415
beat 66	61.756923522595606
beat 67	62.68392236384705
beat 68	63.6109212050985
beat 69	64.53792004634994
beat 70	65.4649188876014
beat 71	66.39191772885285
beat 72	67.31891657010429
beat 73	68.24591541135574
beat 74	69.17291425260719
beat 75	70.09991309385865
beat 76	71.02691193511009
beat 77	71.95391077636154
beat 78	72.88090961761299
beat 79	73.80790845886443
beat 80	74.73490730011588
beat 81	75.66190614136733
beat 82	76.58890498261879
beat 83	77.51590382387023
beat 84	78.44290266512168
beat 85	79.36990150637313
beat 86	80.29690034762457
beat 87	81.22389918887602



================================================================================
Role: system

# Latest Animation Sequence:
No animation sequences have been generated yet.

================================================================================
Role: user

I want you to execute an action that needs my approval

================================================================================
Role: assistant

[Action: "get_music_structure"]: To start creating our animation for the Aladdin song, we first need to get the music structure. This will help us synchronize our animation with the beats and bars of the song. Let's retrieve the beats information to begin with.

Action 'get_music_structure' requires confirmation before execution

================================================================================
Role: user

Action executed: Retrieved beats structure data

================================================================================
Role: user

{
  "structure_type": "beats",
  "data": "### Beats\nA list of aladdin beats and their corresponding start time in seconds:\nLabel | Seconds\n\nbeat 0\t0.5750000000000000\nbeat 1\t1.5019988412514484\nbeat 2\t2.4289976825028967\nbeat 3\t3.355996523754346\nbeat 4\t4.282995365005794\nbeat 5\t5.209994206257242\nbeat 6\t6.136993047508692\nbeat 7\t7.06399188876014\nbeat 8\t7.990990730011588\nbeat 9\t8.917989571263035\nbeat 10\t9.844988412514484\nbeat 11\t10.771987253765932\nbeat 12\t11.698986095017382\nbeat 13\t12.62598493626883\nbeat 14\t13.552983777520279\nbeat 15\t14.479982618771727\nbeat 16\t15.406981460023175\nbeat 17\t16.333980301274625\nbeat 18\t17.26097914252607\nbeat 19\t18.18797798377752\nbeat 20\t19.114976825028968\nbeat 21\t20.04197566628042\nbeat 22\t20.968974507531865\nbeat 23\t21.895973348783315\nbeat 24\t22.822972190034765\nbeat 25\t23.74997103128621\nbeat 26\t24.67696987253766\nbeat 27\t25.603968713789108\nbeat 28\t26.530967555040558\nbeat 29\t27.457966396292004\nbeat 30\t28.384965237543454\nbeat 31\t29.3119640787949\nbeat 32\t30.23896292004635\nbeat 33\t31.1659617612978\nbeat 34\t32.09296060254925\nbeat 35\t33.0199594438007\nbeat 36\t33.94695828505215\nbeat 37\t34.873957126303594\nbeat 38\t35.80095596755505\nbeat 39\t36.727954808806494\nbeat 40\t37.65495365005794\nbeat 41\t38.581952491309394\nbeat 42\t39.50895133256084\nbeat 43\t40.43595017381229\nbeat 44\t41.362949015063734\nbeat 45\t42.28994785631519\nbeat 46\t43.216946697566634\nbeat 47\t44.14394553881808\nbeat 48\t45.070944380069534\nbeat 49\t45.99794322132098\nbeat 50\t46.92494206257243\nbeat 51\t47.85194090382387\nbeat 52\t48.77893974507533\nbeat 53\t49.70593858632677\nbeat 54\t50.63293742757822\nbeat 55\t51.55993626882967\nbeat 56\t52.48693511008112\nbeat 57\t53.41393395133257\nbeat 58\t54.34093279258401\nbeat 59\t55.26793163383547\nbeat 60\t56.19493047508691\nbeat 61\t57.12192931633836\nbeat 62\t58.048928157589806\nbeat 63\t58.97592699884126\nbeat 64\t59.902925840092706\nbeat 65\t60.82992468134415\nbeat 66\t61.756923522595606\nbeat 67\t62.68392236384705\nbeat 68\t63.6109212050985\nbeat 69\t64.53792004634994\nbeat 70\t65.4649188876014\nbeat 71\t66.39191772885285\nbeat 72\t67.31891657010429\nbeat 73\t68.24591541135574\nbeat 74\t69.17291425260719\nbeat 75\t70.09991309385865\nbeat 76\t71.02691193511009\nbeat 77\t71.95391077636154\nbeat 78\t72.88090961761299\nbeat 79\t73.80790845886443\nbeat 80\t74.73490730011588\nbeat 81\t75.66190614136733\nbeat 82\t76.58890498261879\nbeat 83\t77.51590382387023\nbeat 84\t78.44290266512168\nbeat 85\t79.36990150637313\nbeat 86\t80.29690034762457\nbeat 87\t81.22389918887602\n\n"
}
