import os
import sys
from main_controller import MainController

if __name__ == "__main__":
    # Ensure proper module resolution
    sys.path.append(os.path.join(os.path.dirname(__file__), '../lol'))

    # Initialize MainController with configuration
    from config import config
    controller = MainController(config)

    print("AI Agent Console. Type 'exit' to quit.")

    while True:
        user_input = input(">> ")
        if user_input.lower() == "exit":
            print("Exiting. Goodbye!")
            break

        output = controller.communicate(user_input)
        print(f"\nAgent: {output}")
