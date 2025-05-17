
================================================================================
Role: system

# Your Task

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
   - Purpose: Create or update an animation sequence
   - Parameters (UpdateAnimationParams):
     ```python
     {
       "animation_sequence": {
         "name": str,              # Song title
         "duration": float,        # Total length in seconds
         "beats": [
           {
             "beat_start": int,    # Starting beat number
             "beat_end": int,      # Ending beat number
             "elements": List[str], # Elements to animate
             "mapping": Optional[List[str]],  # LED mapping
             "coloring": {
               "type": Literal["constant", "rainbow"],
               "hue": Optional[Union[float, Literal["RED", "ORANGE", "YELLOW", "GREEN", "AQUA", "BLUE", "PURPLE", "PINK"]]],
               "sat": Optional[float]  # 0.0-1.0
             },
             "brightness": Optional[{
               "type": Literal["constant", "fadeIn", "fadeOut", "blink", "fadeInOut", "fadeOutIn"],
               "factor_value": Optional[float]  # 0.0-1.0
             }],
             "motion": Optional[{
               "type": Literal["snake", "snakeInOut"]
             }]
           }
         ]
       }
     }
     ```
   - Requires confirmation: Yes
   - Returns:
     - next_step_number: The step number that will be assigned if confirmed
     - current_steps_count: Total number of existing steps

2. get_animation
   - Purpose: Retrieve an existing animation sequence by step number
   - Parameters (GetAnimationParams):
     ```python
     {
       "step_number": int  # >= 0
     }
     ```
   - Requires confirmation: No
   - Returns:
     - step_number: The requested step number
     - animation: The animation sequence data

3. get_memory
   - Purpose: Retrieve stored memory information about previous animations
   - Parameters (GetMemoryParams): None required
   - Requires confirmation: No
   - Returns:
     - memory: The current memory content or "No memory available"

4. get_music_structure
   - Purpose: Retrieve the structure of a specific song for animation synchronization
   - Parameters (GetMusicStructureParams):
     ```python
     {
       "song_name": str
     }
     ```
   - Requires confirmation: No
   - Returns:
     - song_name: The requested song name
     - structure: The song's structure information (timing, sections, etc.)

5. response_to_user
   - Purpose: Send a message to the user for communication, clarification, or information
   - Parameters (ResponseToUserParams):
     ```python
     {
       "message": str,            # The message to send to the user
       "requires_response": bool, # Whether a response is expected (default: False)
       "message_type": Literal["clarification", "information", "question", "error"]  # Type of message (default: "information")
     }
     ```
   - Requires confirmation: No
   - Returns:
     - message_id: Unique identifier for the message
     - status: Delivery status of the message

Guidelines for Animation Creation:
1. Sync animations with musical beats and sections
2. Use color and brightness to reflect the music's emotional intent
3. Each beat frame is rendered independently (no state carries over)
4. Effects are applied in order: coloring → brightness → motion
5. Default brightness is 1.0 when not specified
6. Use saturated colors (sat > 0.8) for better visibility

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
  [
    {
      "action": "action_name",
      "status": "success",
      "data": {
        # action-specific return data
      }
    },
    {
      "action": "another_action",
      "status": "error",
      "error": "Error message"
    }
  ]
  ```
- Use these results to make informed decisions in your next response
- For actions requiring confirmation, wait for user confirmation before proceeding

Your responses must follow this exact structure:
```python
{
    "reasoning": str,  # Explain why you chose these actions
    "actions": [
        {
            "name": Literal["update_animation", "get_animation", "get_memory", "get_music_structure"],
            "params": Union[UpdateAnimationParams, GetAnimationParams, GetMemoryParams, GetMusicStructureParams]
        }
    ],
    "user_instruction": str  # The original user instruction
}
```

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

# Your Memory: {'favorite_color': 'purple', 'color_preference': 'hue shift of purple and orange', 'pastel_preference': 'likes pastel colors sometimes'}

================================================================================
Role: system

# The Song Structure:
 ## Aladdin Song
### Bars
A list of aladdin bars and their corresponding start time in milliseconds:
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
A list of aladdin beats and their corresponding start time in milliseconds:
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

### Lyrics
These are the lyrics of the song:
<<<<<<< HEAD
Here is a list of all the comments in the file, along with the relevant beats they appear above:

1. ** Comment:** `// 31.5 - 33.5 when the wind's from the east`
  ** Beats:** 31.5 - 33.5

2. ** Comment:** `// 33.5 - 35.5 and the sun's from the west`
  ** Beats:** 33.5 - 35.5

3. ** Comment:** `// 35.5 - 37.5 and the sand in the glass is right`
  ** Beats:** 35.5 - 37.5

4. ** Comment:** `// glass`
  ** Beats:** 36.5 - 38.5

5. ** Comment:** `// is right`
  ** Beats:** 37.5 - 38.5

6. ** Comment:** `// 39 - 40 come on`
  ** Beats:** 39 - 40

7. ** Comment:** `// 40 - 40.5 down`
  ** Beats:** 40 - 40.5

8. ** Comment:** `// 40.5 - 41.5 stop on by`
  ** Beats:** 40.5 - 41.5

9. ** Comment:** `// 41.5 - 42.5 hop a carpet`
  ** Beats:** 41.5 - 42.5

10. ** Comment:** `// 42.5 - 43 and fly`
  ** Beats:** 42.5 - 43

11. ** Comment:** `// 43.5 - 46 to another Arabian night`
  ** Beats:** 43.5 - 46

12. ** Comment:** `// 46 - 48 Ahuuuuuuuu`
  ** Beats:** 46 - 48

13. ** Comment:** `// boom`
  ** Beats:** 48.5 - 50

14. ** Comment:** `// boom fade out and psychedelic`
  ** Beats:** 49 - 50

15. ** Comment:** `// 50 - 53 - Arabian nights`
  ** Beats:** 50 - 53

16. ** Comment:** `// 53 - 57 - like Arabian days`
  ** Beats:** 53 - 57

17. ** Comment:** `// more often than not`
  ** Beats:** 57 - 59

18. ** Comment:** `// are hotter than hot`
  ** Beats:** 59 - 64

19. ** Comment:** `// in a lot of good ways`
  ** Beats:** 60 - 64

20. ** Comment:** `// boom`
  ** Beats:** 64 - 66

21. ** Comment:** `// boom fade out and psychedelic`
  ** Beats:** 64.5 - 66

22. ** Comment:** `// Arabian nights`
  ** Beats:** 66 - 69

23. ** Comment:** `// 'neath Arabian moons`
  ** Beats:** 70 - 73

24. ** Comment:** `// A fool off his guard`
  ** Beats:** 73 - 75

25. ** Comment:** `// could fall and fall hard`
  ** Beats:** 75 - 87

26. ** Comment:** `// out there on the dunes`
  ** Beats:** 81 - 85
=======
Okay, here is the list with the numbers removed from the `//` preceding each lyrics line:

1. ** Lyrics:** `// when the wind's from the east`
  ** Beats:** 31.5 - 33.5

2. ** Lyrics:** `// and the sun's from the west`
  ** Beats:** 33.5 - 35.5

3. ** Lyrics:** `// and the sand in the glass is right`
  ** Beats:** 35.5 - 37.5

4. ** Lyrics:** `// glass`
  ** Beats:** 36.5 - 38.5

5. ** Lyrics:** `// is right`
  ** Beats:** 37.5 - 38.5

6. ** Lyrics:** `// come on`
  ** Beats:** 39 - 40

7. ** Lyrics:** `// down`
  ** Beats:** 40 - 40.5

8. ** Lyrics:** `// stop on by`
  ** Beats:** 40.5 - 41.5

9. ** Lyrics:** `// hop a carpet`
  ** Beats:** 41.5 - 42.5

10. ** Lyrics:** `// and fly`
  ** Beats:** 42.5 - 43

11. ** Lyrics:** `// to another Arabian night`
  ** Beats:** 43.5 - 46

12. ** Lyrics:** `// Ahuuuuuuuu`
  ** Beats:** 46 - 48

13. ** Lyrics:** `// boom`
  ** Beats:** 48.5 - 50

14. ** Lyrics:** `// boom fade out and psychedelic`
  ** Beats:** 49 - 50

15. ** Lyrics:** `// - Arabian nights`
  ** Beats:** 50 - 53

16. ** Lyrics:** `// - like Arabian days`
  ** Beats:** 53 - 57

17. ** Lyrics:** `// more often than not`
  ** Beats:** 57 - 59

18. ** Lyrics:** `// are hotter than hot`
  ** Beats:** 59 - 64

19. ** Lyrics:** `// in a lot of good ways`
  ** Beats:** 60 - 64

20. ** Lyrics:** `// boom`
  ** Beats:** 64 - 66

21. ** Lyrics:** `// boom fade out and psychedelic`
  ** Beats:** 64.5 - 66

22. ** Lyrics:** `// Arabian nights`
  ** Beats:** 66 - 69

23. ** Lyrics:** `// 'neath Arabian moons`
  ** Beats:** 70 - 73

24. ** Lyrics:** `// A fool off his guard`
  ** Beats:** 73 - 75

25. ** Lyrics:** `// could fall and fall hard`
  ** Beats:** 75 - 87

26. ** Lyrics:** `// out there on the dunes`
  ** Beats:** 81 - 85
>>>>>>> 7dab0ae63abdc3309bba0690d06acf3536958550


