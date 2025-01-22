import os
import sys
from main_controller import MainController
from config import config

if __name__ == "__main__":
    # Ensure proper module resolution
    sys.path.append(os.path.join(os.path.dirname(__file__), '../lol'))

    # Initialize MainController with configuration
    controller = MainController(config)

    print("AI Agent Console. Type 'exit' to quit.")

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                print("Shutting down...")
                controller.shutdown()
                print("Goodbye!")
                break

            output = controller.communicate(user_input)
            print(f"AI: {output}")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
