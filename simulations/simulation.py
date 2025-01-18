# simulation.py

from main_controller import MainController
from simulations.user_inputs import user_inputs
from config import config

if __name__ == "__main__":
    controller = MainController(config)

    print("Running AI Agent Simulation...")
    print("Using backend in stub mode for testing.")

    for user_input in user_inputs:
        print(f"You: {user_input}")
        response = controller.communicate(user_input)
        print(f"AI: {response}\n")

    print("Simulation complete.")
