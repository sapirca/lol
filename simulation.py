# simulation.py

from main_controller import MainController

if __name__ == "__main__":
    # Initialize the MainController with stub mode enabled
    controller = MainController()

    print("Running AI Agent Simulation...")
    print("Using backend in stub mode for testing.")

    # Define a series of simulated user inputs
    user_inputs = [
        "What is the best light effect for a fast-paced drop section?",
        "How can I match the lights to the chorus energy?",
        "What colors work well for a calm bridge?",
        "Generate a light sequence for the intro section.",
        "Can you suggest a layout for the house configuration?"
    ]

    # Simulate user interaction
    for user_input in user_inputs:
        print(f"You: {user_input}")
        response = controller.communicate(user_input)
        print(f"AI: {response}\n")

    print("Simulation complete.")
