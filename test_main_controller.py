import unittest
from unittest.mock import MagicMock
from main_controller import MainController
from chat_history import ChatHistory
from backends import StubBackend
from constants import XSEQUENCE_TAG
import xml.etree.ElementTree as ET

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

    # TODO(SAPIR): Get context as array
    # def test_user_input_and_responses_order(self):
    #     """Test that user inputs and responses are added to the chat history in the correct order."""
    #     user_inputs = [
    #         "What is the best light effect for a calm section?",
    #         "What colors should I use for a romantic section?"
    #     ]

    #     responses = []
    #     for user_input in user_inputs:
    #         responses.append(self.controller.communicate(user_input))

    #     # Get the chat history context
    #     context = self.controller.chat_history.get_context()
    #     lines = context.split("\n")

    #     # Verify the order: initial prompt, user inputs, and responses
    #     self.assertTrue(
    #         lines[0] == "system: You are an AI assistant specializing in crafting light sequences that suit the played music. Your task is to generate a visually engaging light show for the provided song using the xLights software. You will analyze the provided EDM music and create an XSQ sequence file based on the given template.",
    #         "Initial prompt is not at the beginning of the chat history."
    #     )

    #     for i, user_input in enumerate(user_inputs):
    #         user_index = len(lines) - len(user_inputs) * 2 + i * 2  # Dynamic index for user input
    #         response_index = user_index + 1  # Response immediately follows the user input

    #         self.assertEqual(lines[user_index], f"user: {user_input}", f"User input {i + 1} is not in the correct order.")
    #         self.assertEqual(lines[response_index], f"assistant: {responses[i]}", f"Response {i + 1} is not in the correct order.")

    def test_sequence_flow(self):
        """Test the sequence flow: initial skeleton sequence and updates."""
        # Verify initial sequence matches the skeleton file
        with open("sequence_skeleton.xml", "r") as skeleton_file:
            expected_initial_sequence = skeleton_file.read().strip()
        
        initial_sequence = self.controller.sequence_manager.get_latest_sequence().strip()

        # Normalize both sequences by parsing and converting back to strings
        expected_tree = ET.fromstring(expected_initial_sequence)
        initial_tree = ET.fromstring(initial_sequence)
        expected_normalized = ET.tostring(expected_tree, encoding="unicode")
        initial_normalized = ET.tostring(initial_tree, encoding="unicode")

        self.assertEqual(initial_normalized, expected_normalized, "Initial sequence skeleton does not match the file.")
        self.assertEqual(len(self.controller.sequence_manager.steps), 1, "Number of sequences is not as expected.")

        # Simulate first update
        user_input_1 = "Add a simple animation for the intro section."
        response_1 = self.controller.communicate(user_input_1)

        expected_sequence_update = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
            <xsequence BaseChannel=\"0\" ChanCtrlBasic=\"0\" ChanCtrlColor=\"0\" FixedPointTiming=\"1\" ModelBlending=\"true\">
            <head>
            <version>2024.19</version>
            </head>
            <steps>
            <step>
            <number>1</number>
            <animation>Simple Animation</animation>
            </step>
            </steps>
            </xsequence>
            """

        updated_sequence_1 = self.controller.sequence_manager.get_latest_sequence()
        self.assertNotEqual(expected_sequence_update, updated_sequence_1, "Sequence was not updated after first response.")
        self.assertEqual(len(self.controller.sequence_manager.steps), 2, "Number of sequences is not 2.")

        # Simulate second update
        user_input_2 = "Add a more dynamic animation for the drop section."
        response_2 = self.controller.communicate(user_input_2)

        updated_sequence_2 = self.controller.sequence_manager.get_latest_sequence()
        
        # Assert number of sequences in manager
        self.assertNotEqual(expected_sequence_update, updated_sequence_2, "Sequence was not updated after second response.")
        self.assertEqual(len(self.controller.sequence_manager.steps), 3, "Number of sequences is not 3.")

if __name__ == "__main__":
    result = unittest.main(exit=False)
    if result.result.wasSuccessful():
        print("All tests passed successfully!")
