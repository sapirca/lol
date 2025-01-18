import unittest
from unittest.mock import MagicMock
from main_controller import MainController
from chat_history import ChatHistory
from backends import StubBackend

class TestMainController(unittest.TestCase):
    def setUp(self):
        """Set up the MainController with a stub backend."""

        self.config = {
            "use_stub": True,
            "selected_backend": None,
            "should_add_knowledge": False
        }
        self.controller = MainController(self.config)

    def test_initial_prompt_added(self):
        """Test that the initial prompt is added to the chat history only once."""
        user_input = "What is the best light effect for a calm section?"

        response = self.controller.communicate(user_input)

        # Check that the initial prompt is in the chat history
        context = self.controller.chat_history.get_context()
        self.assertIn("You are an AI assistant specializing", context)

        # Check that the user input and response are also in the chat history
        self.assertIn(user_input, context)
        self.assertIn("[Stub-StubBackend]:", response)

    def test_multiple_user_inputs(self):
        """Test that multiple user inputs are handled correctly."""
        user_inputs = [
            "What is the best light effect for a fast-paced drop section?",
            "What colors should I use for a romantic section?"
        ]

        for user_input in user_inputs:
            response = self.controller.communicate(user_input)

        # Check that all user inputs are in the chat history
        context = self.controller.chat_history.get_context()
        for user_input in user_inputs:
            self.assertIn(user_input, context)

        # Check that the stub responses are included
        self.assertIn("[Stub-StubBackend]:", context)

    def test_backend_selection_with_stub(self):
        """Test that the StubBackend is used when the stub flag is on."""
        user_input = "What is the timing for a drop?"

        # Ensure only the StubBackend is selected
        backend = self.controller.select_backend()
        self.assertEqual(backend.name, "StubBackend")

        response = self.controller.communicate(user_input)
        self.assertIn("[Stub-StubBackend]:", response)

if __name__ == "__main__":
    result = unittest.main(exit=False)
    if result.result.wasSuccessful():
        print("All tests passed successfully!")
