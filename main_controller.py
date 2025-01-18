import random
from backends import GPTBackend, ClaudeBackend, GeminiBackend, StubBackend, LLMBackend
from prompts import get_full_prompt
import xml.etree.ElementTree as ET
from knowledge import knowledge_prompts
from chat_history import ChatHistory

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
            if "StubBackend" in self.backends:
                return self.backends["StubBackend"]
            else:
                raise ValueError("StubBackend is not registered.")

        if self.selected_backend and self.selected_backend in self.backends:
            return self.backends[self.selected_backend]
        
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
        prompt = get_full_prompt(self.house_config)

        if self.should_add_knowledge:
            prompt += "\n" + "\n".join(knowledge_prompts)

        prompt += f"\nUser input: {user_input}"

        return backend.generate_response(prompt)
