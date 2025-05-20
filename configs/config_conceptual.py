from constants import MODEL_CONFIGS

config = {
    "with_structured_output": True,  #True #False
    "framework": "conceptual",  #kivsee #xlights #conceptual
    "selected_backend": "Claude",  # "GPT",  # "DeepSeek",
    "model_config":
    MODEL_CONFIGS["Claude"],  # Use the model config from constants
}
