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

    def test_initial_prompt_only_once(self):
        """Test that the initial prompt is added only once to the chat history."""
        first_input = "What is the best light effect for a calm section?"
        second_input = "What colors should I use for a romantic section?"

        # Communicate twice
        self.controller.communicate(first_input)
        self.controller.communicate(second_input)

        # Check that the initial prompt appears only once
        context = self.controller.chat_history.get_context()
        initial_prompt_count = context.count("You are an AI assistant specializing")
        self.assertEqual(initial_prompt_count, 1, "Initial prompt was added more than once.")

    def test_initial_prompt_order(self):
        """Test that the initial prompt is added at the beginning of the chat history."""
        user_input = "What is the best light effect for a calm section?"

        response = self.controller.communicate(user_input)

        # Get the chat history context
        context = self.controller.chat_history.get_context()

        # Check that the initial prompt is the first message
        lines = context.split("\n")
        
        self.assertTrue(
            lines[0] == "system: You are an AI assistant specializing in crafting light sequences that suit the played music. Your task is to generate a visually engaging light show for the provided song using the xLights software. You will analyze the provided EDM music and create an XSQ sequence file based on the given template.",
            "Initial prompt is not at the beginning of the chat history."
        )


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


    def test_user_input_and_responses_order(self):
        """Test that user inputs and responses are added to the chat history in the correct order."""
        user_inputs = [
            "What is the best light effect for a calm section?",
            "What colors should I use for a romantic section?"
        ]

        responses = []
        for user_input in user_inputs:
            responses.append(self.controller.communicate(user_input))

        # Get the chat history context
        context = self.controller.chat_history.get_context()
        lines = context.split("\n")

        # Debugging: Print the lines for inspection if needed
        # print("Chat History Lines:\n", lines)

        # Find the start index of user inputs and assistant responses
        for i, user_input in enumerate(user_inputs):
            user_index = len(lines) - len(user_inputs) * 2 + i * 2  # Dynamic index for user input
            response_index = user_index + 1  # Response immediately follows the user input

            self.assertEqual(lines[user_index], f"user: {user_input}", f"User input {i + 1} is not in the correct order.")
            self.assertEqual(lines[response_index], f"assistant: {responses[i]}", f"Response {i + 1} is not in the correct order.")

if __name__ == "__main__":
    result = unittest.main(exit=False)
    if result.result.wasSuccessful():
        print("All tests passed successfully!")
