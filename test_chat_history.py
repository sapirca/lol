import unittest
import os
from chat_history import ChatHistory
import json

class TestChatHistory(unittest.TestCase):

    def setUp(self):
        self.snapshot_dir = "test_chats/snapshots"
        self.final_dir = "test_chats/finals"
        self.chat_history = ChatHistory(snapshot_dir=self.snapshot_dir, final_dir=self.final_dir)

        # Ensure directories are clean
        if os.path.exists(self.snapshot_dir):
            for file in os.listdir(self.snapshot_dir):
                os.remove(os.path.join(self.snapshot_dir, file))
        if os.path.exists(self.final_dir):
            for file in os.listdir(self.final_dir):
                os.remove(os.path.join(self.final_dir, file))

    def tearDown(self):
        # Clean up test directories
        if os.path.exists(self.snapshot_dir):
            for file in os.listdir(self.snapshot_dir):
                os.remove(os.path.join(self.snapshot_dir, file))
            os.rmdir(self.snapshot_dir)
        if os.path.exists(self.final_dir):
            for file in os.listdir(self.final_dir):
                os.remove(os.path.join(self.final_dir, file))
            os.rmdir(self.final_dir)

    def test_add_message_and_cache(self):
        self.chat_history.add_message("user", "Hello!")
        self.chat_history.add_message("assistant", "Hi there!")

        # Verify snapshot file exists
        snapshot_file = os.path.join(self.snapshot_dir, "chat_history_snapshot.json")
        self.assertTrue(os.path.exists(snapshot_file))

        # Verify snapshot content
        with open(snapshot_file, "r") as file:
            history = json.load(file)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "Hello!")
        self.assertEqual(history[1]["role"], "assistant")
        self.assertEqual(history[1]["content"], "Hi there!")

    def test_finalize(self):
        self.chat_history.add_message("user", "Hello!")
        self.chat_history.add_message("assistant", "Hi there!")

        self.chat_history.finalize()

        # Verify final log file exists
        final_logs = os.listdir(self.final_dir)
        self.assertEqual(len(final_logs), 1)

        final_log_path = os.path.join(self.final_dir, final_logs[0])
        with open(final_log_path, "r") as file:
            history = json.load(file)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "Hello!")
        self.assertEqual(history[1]["role"], "assistant")
        self.assertEqual(history[1]["content"], "Hi there!")

    def test_get_context_excludes_animations(self):
        self.chat_history.add_message("user", "What is the best light effect?")
        self.chat_history.add_message("assistant", "A soft blue ripple effect is great.")
        self.chat_history.add_message("animation", "<xsequence>...</xsequence>")

        context = self.chat_history.get_context()

        # Verify that "animation" is excluded from the context
        self.assertNotIn("<animation>", context)
        self.assertIn("<user>: What is the best light effect?", context)
        self.assertIn("<assistant>: A soft blue ripple effect is great.", context)


    def test_load_chat_history(self):
        self.chat_history.add_message("user", "Hello!")
        self.chat_history.add_message("assistant", "Hi there!")

        # Load snapshot through the same method
        self.chat_history.load_chat_history()

        self.assertEqual(len(self.chat_history.history), 2)
        self.assertEqual(self.chat_history.history[0]["role"], "user")
        self.assertEqual(self.chat_history.history[0]["content"], "Hello!")
        self.assertEqual(self.chat_history.history[1]["role"], "assistant")
        self.assertEqual(self.chat_history.history[1]["content"], "Hi there!")

        # Write a final log and load it
        self.chat_history.finalize()
        final_logs = os.listdir(self.final_dir)
        final_log_path = os.path.join(self.final_dir, final_logs[0])

        self.chat_history.load_chat_history(final_log_path)
        self.assertEqual(len(self.chat_history.history), 2)
        self.assertEqual(self.chat_history.history[0]["role"], "user")
        self.assertEqual(self.chat_history.history[0]["content"], "Hello!")
        self.assertEqual(self.chat_history.history[1]["role"], "assistant")
        self.assertEqual(self.chat_history.history[1]["content"], "Hi there!")


if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)
