import random
from backends import GPTBackend, ClaudeBackend, GeminiBackend, StubBackend, LLMBackend
from prompts import get_full_prompt
import xml.etree.ElementTree as ET
from knowledge import knowledge_prompts
from chat_history import ChatHistory
from sequence_manager import SequenceManager
from constants import XSEQUENCE_TAG

class MainController:
    """
    MainController that interacts with a human and selects responses from multiple LLM backends.
    """
    def __init__(self, config):
        self.backends = {}
        self.use_stub = config.get("use_stub", False)
        self.selected_backend = config.get("selected_backend", None)
        self.chat_history = ChatHistory()
        self.initial_prompt_added = False
        self.house_config = self._load_house_config()
        self.should_add_knowledge = config.get("should_add_knowledge", False)
        self.sequence_manager = SequenceManager("sequence_skeleton.xml")
        self._initialize_backends()

    def _initialize_backends(self):
        """Initialize backends manually using mapping."""
        backend_mapping = {
            "GPTBackend": GPTBackend,
            "ClaudeBackend": ClaudeBackend,
            "GeminiBackend": GeminiBackend,
            "StubBackend": StubBackend
        }
        for backend_name, backend_class in backend_mapping.items():
            self.register_backend(backend_class(backend_name))

    def register_backend(self, backend):
        """Register a new LLM backend."""
        if not isinstance(backend, LLMBackend):
            raise TypeError("backend must be an instance of LLMBackend.")
        self.backends[backend.name] = backend

    def select_backend(self):
        """Select a backend based on the configuration or random selection."""
        if not self.backends:
            raise ValueError("No backends available.")

        if self.use_stub:
            # Ensure only the StubBackend is used if the stub flag is on
            stub_backend = self.backends.get("StubBackend")
            if not stub_backend:
                raise ValueError("StubBackend is not registered.")
            return stub_backend

        if self.selected_backend:
            selected_backend = self.backends.get(self.selected_backend)
            if selected_backend:
                return selected_backend

            print(f"Warning: Selected backend '{self.selected_backend}' not found, choosing randomly.")

        # Randomly select a backend if no valid selection is specified
        return random.choice(list(self.backends.values()))

    def _load_house_config(self):
        """Load house configuration from an XML file."""
        try:
            tree = ET.parse('house_config.xml')
            root = tree.getroot()
            return ET.tostring(root, encoding='unicode')
        except Exception as e:
            return f"Error loading house configuration: {e}"


    def communicate(self, user_input):
            """Generate a response to the user's input."""
            backend = self.select_backend()

            latest_sequence = self.sequence_manager.get_latest_sequence()

            if not self.initial_prompt_added:
                # Add the initial prompt to the chat history
                initial_prompt = get_full_prompt(self.house_config)
                self.chat_history.add_message("system", initial_prompt)
                self.initial_prompt_added = True
            
            # Add user input to chat history
            self.chat_history.add_message("user", user_input)

            # Prepare the prompt with the latest sequence
            prompt = self.chat_history.get_context() + f"\n\nAnimation Sequence ({XSEQUENCE_TAG}):\n{latest_sequence}"

            response = backend.generate_response(prompt)

            # Add AI response to chat history
            self.chat_history.add_message("assistant", response)

            # Check if the response contains a sequence to add
            if "<?xml" in response and f"</{XSEQUENCE_TAG}>" in response:
                sequence_xml = response[response.find("<?xml") : response.find(f"</{XSEQUENCE_TAG}>") + len(f"</{XSEQUENCE_TAG}>")]
                step_number = len(self.sequence_manager.steps) + 1
                self.sequence_manager.add_sequence(step_number, sequence_xml)

            return response

