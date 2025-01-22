import unittest
import os
from main_controller import MainController
from chat_history import ChatHistory
from sequence_manager import SequenceManager
from constants import XSEQUENCE_TAG, ANIMATION_OUT_TEMP_DIR
import xml.etree.ElementTree as ET

class TestMainController(unittest.TestCase):
    def setUp(self):
        # Initialize MainController with test configuration
        self.config = {
            "use_stub": True,
            "selected_backend": "StubBackend",
            "should_add_knowledge": False,
        }
        self.controller = MainController(self.config)
        self.chat_history = self.controller.chat_history
        self.sequence_manager = self.controller.sequence_manager

        # Create necessary directories for testing
        os.makedirs(ANIMATION_OUT_TEMP_DIR, exist_ok=True)

    def tearDown(self):
        # Cleanup temp files and directories
        if os.path.exists(ANIMATION_OUT_TEMP_DIR):
            for file in os.listdir(ANIMATION_OUT_TEMP_DIR):
                os.remove(os.path.join(ANIMATION_OUT_TEMP_DIR, file))

    def test_initial_prompt_added(self):
        """Test that the initial prompt is added to the chat history."""
        user_input = "What is the best light effect for a calm section?"
        self.controller.communicate(user_input)
        context = self.chat_history.get_context()
        self.assertTrue(context.startswith("<system>: You are an AI assistant specializing"), "Initial prompt is not added correctly.")

    def test_user_input_and_responses_order(self):
        """Test that user inputs and responses are added to the chat history in the correct order."""
        user_inputs = [
            "What is the best light effect for a calm section?",
            "y"
        ]

        responses = []
        for user_input in user_inputs:
            responses.append(self.controller.communicate(user_input))

        # Filter out 'animation' role entries
        filtered_history = [msg for msg in self.controller.chat_history.history if msg["role"] != "animation"]

        # Verify the length of filtered history
        expected_length = 1 + len(user_inputs) * 2  # 1 system message + 2 messages (user, assistant) per input
        self.assertEqual(len(filtered_history), expected_length, "Filtered chat history does not match expected length.")

        # Verify the initial system message
        self.assertEqual(filtered_history[0]["role"], "system", "First message is not a system message.")
        self.assertTrue(
            "You are an AI assistant specializing" in filtered_history[0]["content"],
            "Initial system message content is incorrect."
        )

        # Verify user inputs and assistant responses
        for i, user_input in enumerate(user_inputs):
            user_message = filtered_history[1 + i * 2]
            assistant_message = filtered_history[2 + i * 2]

            self.assertEqual(user_message["role"], "user", f"Message {i + 1} is not a user message.")
            self.assertEqual(user_message["content"], user_input, f"User input {i + 1} is incorrect.")

            self.assertEqual(assistant_message["role"], "assistant", f"Message {i + 1} is not an assistant message.")
            self.assertTrue(
                responses[i] in assistant_message["content"],
                f"Assistant response {i + 1} does not match the expected response."
            )

    def test_sequence_flow(self):
        """Test the sequence flow: initial skeleton sequence and updates."""
        tree = ET.parse("sequence_skeleton.xml")
        expected_initial_sequence = ET.tostring(tree.getroot(), encoding="unicode")

        # Verify the initial sequence matches the skeleton
        initial_sequence = self.controller.sequence_manager.get_latest_sequence()
        self.assertEqual(
            initial_sequence.strip(),
            expected_initial_sequence.strip(),
            "Initial sequence skeleton does not match the file."
        )

        # Simulate first user input
        user_input_1 = "Add a simple animation for the intro section."
        output_1 = self.controller.communicate(user_input_1)
        self.assertIn("Approve to save this animation to the sequence manager?", output_1, "Approval prompt not returned.")

        # Simulate user approval (saving the sequence)
        save_output_1 = self.controller.communicate("y")
        updated_sequence_1 = self.controller.sequence_manager.get_latest_sequence()
        self.assertNotEqual(initial_sequence, updated_sequence_1, "Sequence was not updated after user approval.")
        self.assertIn("Animation saved successfully as step", save_output_1, "Save confirmation not returned.")

        # Simulate second user input
        user_input_2 = "Add a more dynamic animation for the drop section."
        output_2 = self.controller.communicate(user_input_2)
        self.assertIn("Approve to save this animation to the sequence manager?", output_2, "Approval prompt not returned.")

        # Simulate user rejection (not saving the sequence)
        reject_output_2 = self.controller.communicate("n")
        updated_sequence_2 = self.controller.sequence_manager.get_latest_sequence()
        self.assertEqual(
            updated_sequence_1,
            updated_sequence_2,
            "Sequence was incorrectly updated after user rejection."
        )
        self.assertIn("Animation discarded.", reject_output_2, "Rejection confirmation not returned.")


    def test_response_manager_parse_logic(self):
        """Test parsed response handling for reasoning, consistency justification, and sequence."""
        user_input = "Add a new light sequence for the chorus section."
        response = self.controller.communicate(user_input)
        self.assertIn("animation has been stored", response.lower(), "Parsed response did not indicate animation handling.")

    def test_temp_animation_management(self):
        """Test the handling of temporary animation files."""
        user_input = "Create a new animation for the verse section."
        self.controller.communicate(user_input)
        self.assertIsNotNone(self.controller.temp_animation_path, "Temp animation path was not set.")
        self.assertTrue(os.path.exists(self.controller.temp_animation_path), "Temp animation file was not created.")

        # Simulate user approval
        approval_response = self.controller.handle_user_approval("y")
        self.assertIn("Animation saved successfully", approval_response, "Animation approval did not save the sequence.")
        self.assertFalse(os.path.exists(self.controller.temp_animation_path), "Temp animation file was not deleted after approval.")

    def test_invalid_user_response(self):
        """Test handling of invalid user responses during approval."""
        user_input = "Generate an animation."
        self.controller.communicate(user_input)

        invalid_response = self.controller.handle_user_approval("maybe")
        self.assertIn("Invalid response", invalid_response, "Invalid response was not handled correctly.")

    def test_chat_history_finalization(self):
        """Test chat history finalization and saving to logs."""
        self.controller.shutdown()
        log_dir = "chats/finals"
        files = os.listdir(log_dir)
        self.assertTrue(any(file.startswith("final_chat_log_") for file in files), "Final chat log was not saved.")

if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)