from constants import MODEL_CONFIGS

config = {
    "selected_backend": "Claude",
    "framework": "kivsee",  #kivsee #xlights #conceptual
    "song_name": "aladdin",  #  "nikki", "sandstorm", "req", "overthinker"
    "auto_render": True,
    "print_internal_messages": False,
    "show_all_animations": False,
    "model_config":
    MODEL_CONFIGS["claude-3-7"],  # Use the model config from constants
}

# "selected_backend": "GPT",  # "DeepSeek",  #DeepSeek #GPT #Gemini #Claude
# config = {
#     "selected_backend": "GPT",  # "DeepSeek",  #DeepSeek #GPT #Gemini #Claude
#     "framework": "conceptual",  #kivsee #xlights #conceptual
# }

#     'song_name': 'sandstorm',  #  "nikki", "sandstorm", "req", "overthinker"
