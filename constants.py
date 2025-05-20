# Maximum tokens for LLM context
MAX_TOKENS = 2048

# API timeout settings (in seconds)
API_TIMEOUT = 10

# XML sequence tag
TIME_FORMAT = "%d-%m-%Y %H:%M:%S"
LOG_INTERVAL_IN_SECONDS = 60

# Snapshots
SNAPSHOTS_DIR = "ui/tkinter/snapshots"
MESSAGE_SNAPSHOT_FILE = "messages.json"
CONFIG_FILE = "config.json"

# Animations
ANIMATION_OUT_TEMP_DIR = "tmp_animation/"

# Kivsee
KIVSEE_HOUSE_PATH = "animation/frameworks/kivsee/world_structure.txt"
KIVSEE_LEARNING_PATH = "prompts/kivsee/learning.json"
KIVSEE_TEMP_ANIMATION_FILE = "kivsee_tmp.json"
KIVSEE_ANIMATION_SUFFIX = 'json'

# Xlights
# XLIGHTS_HOUSE_PATH = "animation/frameworks/xlights/world_structure.xml"
XLIGHTS_HOUSE_PATH = "animation/frameworks/xlights/simulator/shows/rings/sandstorm_rings.fseq"
# XLIGHTS_SEQUENCE_PATH = "animation/frameworks/xlights/sequence_skeleton.xsq"
XLIGHTS_SEQUENCE_PATH = "animation/frameworks/xlights/simulator/shows/rings/sandstorm_rings.xsq"
XLIGHTS_KNOWLEDGE_PATH = "animation/frameworks/xlights/knowledge.txt"
XLIGHTS_TEMP_ANIMATION_FILE = "xlights_tmp.xsq"
XLIGHTS_ANIMATION_SUFFIX = 'xsq'

# ConceptualFramework
CONCEPTUAL_HOUSE_PATH = "animation/frameworks/conceptual/conceptual_house.txt"
CONCEPTUAL_KNOWLEDGE_PATH = "animation/frameworks/conceptual/conceptual_knowledge.txt"
CONCEPTUAL_PROMPT = "animation/frameworks/conceptual/prompt.txt"
CONCEPTUAL_SEQUENCE_PATH = "animation/frameworks/conceptual/conceptual_sequence.json"
CONCEPTUAL_TEMP_ANIMATION_FILE = "conceptual_tmp.json"
CONCEPTUAL_ANIMATION_SUFFIX = "json"

# Model configurations for different backends
MODEL_CONFIGS = {
    # GPT Models
    "gpt-4": {
        "model_name": "gpt-4",
        "max_tokens": 16384,
    },
    "gpt-4-turbo": {
        "model_name": "gpt-4-turbo-preview",
        "max_tokens": 16384,
    },

    # Claude Models
    "claude-3-5-sonnet": {
        "model_name": "claude-3-5-sonnet-20240620",
        "max_tokens": 4096,
    },
    "claude-3-5-haiku": {
        "model_name": "claude-3-5-haiku-latest",
        "max_tokens": 8192,
    },
    "claude-3-7": {
        "model_name": "claude-3-7-sonnet-latest",
        "max_tokens": 64000,
    },

    # Gemini Models
    "gemini-1.5-flash": {
        "model_name": "models/gemini-1.5-flash-latest",
        "max_tokens": 4096,
    },
    "gemini-1.5-pro": {
        "model_name": "models/gemini-1.5-pro-latest",
        "max_tokens": 64000,
    },
    "gemini-2.5-preview": {
        "model_name": "models/gemini-2.5-preview-latest",
        "max_tokens": 64000,
    },

    # Default configurations for each provider
    "GPT": {
        "model_name": "gpt-4",
        "max_tokens": 16384,
    },
    "Claude": {
        "model_name": "claude-3-5-sonnet-20240620",
        "max_tokens": 4096,
    },
    "Gemini": {
        "model_name": "models/gemini-1.5-flash-latest",
        "max_tokens": 4096,
    }
}
