# Maximum tokens for LLM context
MAX_TOKENS = 2048

# API timeout settings (in seconds)
API_TIMEOUT = 10

# XML sequence tag
TIME_FORMAT = "%d-%m-%Y %H:%M:%S"
LOG_INTERVAL_IN_SECONDS = 60

OUTPUT_DIR = "outputs"

# Snapshots
SNAPSHOTS_DIR = "outputs/snapshots"
MESSAGE_SNAPSHOT_FILE = "messages.json"
CONFIG_FILE = "config.json"

# Animations
ANIMATION_OUT_TEMP_DIR = "outputs/tmp"

# Kivsee
KIVSEE_HOUSE_PATH = "animation/frameworks/kivsee/world_structure.txt"
KIVSEE_TEMP_ANIMATION_FILE = "kivsee_tmp.ts"
KIVSEE_SEQUENCE_PATH = "animation/frameworks/kivsee/sequence_skeleton.ts"
KIVSEE_KNOWLEDGE_PATH = "animation/frameworks/kivsee/knowledge_api.ts"
KIVSEE_PROMPT = "animation/frameworks/kivsee/prompt.txt"
KIVSEE_ADD_ONS_PATH = "animation/frameworks/kivsee/knowledge_rules.txt"
KIVSEE_ANIMATION_SUFFIX = 'ts'
KIVSEE_ANIMATION_EXAMPLE = "animation/frameworks/kivsee/knowledge_example"
# Xlights
# XLIGHTS_HOUSE_PATH = "animation/frameworks/xlights/world_structure.xml"
XLIGHTS_HOUSE_PATH = "animation/frameworks/xlights/simulator/shows/rings/sandstorm_rings.fseq"
# XLIGHTS_SEQUENCE_PATH = "animation/frameworks/xlights/sequence_skeleton.xsq"
XLIGHTS_SEQUENCE_PATH = "animation/frameworks/xlights/simulator/shows/rings/sandstorm_rings.xsq"
XLIGHTS_KNOWLEDGE_PATH = "animation/frameworks/xlights/knowledge.txt"
XLIGHTS_TEMP_ANIMATION_FILE = "xlights_tmp.xsq"
XSEQUENCE_TAG = "xsequence"
XLIGHTS_ANIMATION_SUFFIX = 'xsq'
