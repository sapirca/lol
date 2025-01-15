
from datetime import datetime
import os
from main_controller import MainController

if __name__ == "__main__":
    # Initialize the MainController
    controller = MainController()

    # Ensure the logs directory exists
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Generate a log file name with date and time in the logs directory
    log_filename = os.path.join(log_dir, datetime.now().strftime("conversation_log_%Y-%m-%d_%H-%M-%S.txt"))

    # Open a file to log the session
    with open(log_filename, "a") as log_file:
        log_file.write(f"Session started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print("MainController is ready. Type 'exit' to quit.")
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Exiting. Goodbye!")
                log_file.write(f"Session ended at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                break

            response = controller.communicate(user_input)
            print(f"AI: {response}")

            # Write input and output to the log file
            log_file.write(f"You: {user_input}\n")
            log_file.write(f"AI: {response}\n")
