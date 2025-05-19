
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
    "action": Union,  # The single action to be executed in this turn. This field now supports both direct JSON objects and stringified JSON objects. If a string is provided, it will be parsed as JSON.
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

### Key Points
A list of aladdin key points and their corresponding start time in milliseconds:
Aligning animation changes to the keypoints begining and ending can enhance the visual experience and create higher quality animations.
User the labels as a guide to create the animation.
1.933399	2.428998	Cymbals
5.652287	6.136993	Cymbals
7.990991	9.844988	increasing violin sound
9.844988	11.698986	up and down violin sound
11.698986	13.552984	decreasing violin sound
13.552984	14.905589	vanishing sound
14.905589	15.404051	intro sound
15.404051	20.938236	mellow begining of storytelling
20.928037	21.432456	decreasing sound
21.432456	22.309214	silent
22.309214	22.822972	intro fading in sound
22.836037	28.413341	verse2- gradually increasing intensity of storytelling 
28.413341	28.832397	peak sound
28.832397	29.598225	fadeout
29.739884	30.216514	intro-wind
30.216514	31.602378	 winds sounds - right
31.602378	32.128100	intro-wind-2
32.107818	33.019959	wind sounds - left
33.421675	33.946958	1- talking about sand
34.313762	34.873957	2 - talking about glass
35.191801	35.864204	3- is right
36.727955	37.630987	fading in lyrics
37.630987	38.602346	part 1
38.602346	39.508951	part 2
39.508951	40.453426	part 3
40.471753	41.362949	part 4
41.362949	45.098458	increasing animation before the drop
45.499565	45.987536	crazy boom
45.987536	46.949428	pre
46.932420	49.243783	Chorus
49.243783	50.650109	 tiny part
50.650109	52.495342	Chorus - same
53.413959	54.340933	part 1
54.340933	55.267932	part 2
55.267932	56.206693	part - hotter than hot - colors
56.206693	57.121929	part 4
57.117889	59.846032	pre chorus - increasing again
59.886577	60.407253	crazy ecstatic boom, must animate
60.407253	64.537920	Chorus - s2nd
72.885285	75.968913	singing slowly fading out 
75.968913	76.657781	stupid sound like licking
76.959571	77.405695	stupid sound 2 - lik yo yo decreasing


### Lyrics
The lyrics of the song, with the first number indicating the start time in milliseconds and the second number indicating the end time:
Aligning animation changes to the lyrics begining and ending can enhance the visual experience and create higher quality animations.
15.140220	15.140220	Oh I
15.427265	15.427265	Come
15.849390	15.849390	from
16.333980	16.333980	a land
16.761181	16.761181	from
17.183306	17.183306	a
17.329642	17.774281	far
17.774281	18.157008	away
18.187978	18.187978	place
18.888691	18.888691	where a
19.198250	19.198250	caravan
19.963703	19.963703	camels
20.968975	21.680345	roam
22.280310	22.280310	where it's
22.822972	22.822972	flat
23.310614	23.310614	and
23.749971	23.749971	immense
24.319452	24.319452	and
24.676970	24.676970	the heat
25.167306	25.167306	is
25.603969	25.603969	intenese
26.154680	26.154680	it's
26.530968	26.530968	barbbaric
27.457966	27.457966	but hey..
28.107964	28.107964	it's
28.347868	29.295478	home
29.719863	30.238963	when the
30.238963	30.625999	wind
30.625999	31.553208	from the east
31.553208	32.092961	and the sun 
32.297785	33.019959	from the west
33.421675	33.946958	and the sand
34.313762	35.191801	in the glass
35.191801	35.859622	is right
36.727955	37.649315	come on
37.649315	38.011283	down
38.011283	38.606928	stop on 
38.602346	39.115516	by
39.124680	39.508951	hop a
39.508951	40.022729	carpet
40.018147	40.432664	and
40.435950	40.940908	fly
40.940908	41.362949	to
41.362949	42.302277	another
42.302277	43.216947	arabian
43.216947	45.070394	nights
45.424350	46.921857	arbian
46.921857	49.109123	nights
49.199881	49.675020	like
49.704481	50.632937	arabian
50.632937	52.487006	days
52.866559	53.392345	more
53.404206	53.803579	often
53.803579	54.293782	than
54.293782	54.791945	not
54.987651	55.254524	are
55.254524	55.767955	hotter
55.767955	56.184441	than
56.184441	56.674156	hot
56.671915	57.959926	in a lot of good
57.959926	59.902926	ways
59.902926	60.423602	boom
60.423602	61.756924	arabian
61.763624	63.674323	nights
63.674323	64.179102	'neat
64.357718	65.204072	arabian
65.464919	67.318917	moons
67.783204	69.165008	a fool off his
69.165008	69.804092	gaurd
69.804092	71.047715	could fall and fall
71.026912	71.953911	hard
71.953911	72.901634	out there on
72.901634	75.688270	the dunes


### Drums Pattern
The drum pattern of the song repeats cyclically throughout its duration. It is represented using relative beats as labels, such as 0.5, 1.5, etc., which correspond to fractions of a beat based on the BPM (beats per minute). For instance, if a beat lasts 2 seconds, 0.25 beats would equal 0.5 seconds.
The pattern spans 0 to 3.75 beats (4 beats in total) and aligns with every 4th beat. Two cycles of the pattern are provided as an example. Aligning animation changes to the drum pattern can enhance the visual experience and create higher quality animations.
0.575871	0.575871	0 
1.038852	1.038852	0.5
1.263821	1.263821	0.75
1.501822	1.501822	1
1.965498	2.196760	1.5
2.428998	2.428998	2
2.892464	2.892464	2.5
3.124996	3.124996	2.75
3.355637	3.355637	3
3.590058	3.590058	3.25
3.818809	3.818809	3.5
4.051340	4.051340	3.75
4.282995	4.282995	0
4.745154	4.745154	0.5
4.975795	4.975795	0.75
5.208946	5.208946	1
5.669608	5.905920	1.5
6.136122	6.136122	2
6.601624	6.601624	2.5
6.832265	6.832265	2.75
7.064797	7.064797	3
7.295437	7.295437	3.25
7.527969	7.527969	3.5
7.758610	7.758610	3.75



