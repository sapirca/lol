# simulation.py

from datetime import datetime
import os
import subprocess

# Simulate running the console application
print("Running AI Agent Simulation...")

# Simulated user inputs
user_inputs = [
    "What is the best light effect for a fast-paced drop section?",
    "How can I match the lights to the chorus energy?",
    "What colors work well for a calm bridge?",
    "Generate a light sequence for the intro section.",
    "Can you suggest a layout for the house configuration?",
    "exit"
]

# Create a temporary file for input simulation
input_file = "simulation_input.txt"
with open(input_file, "w") as f:
    f.write("\n".join(user_inputs))

try:
    # Run the console script with the simulated inputs
    process = subprocess.run(
        ["python", "console.py"],
        input=open(input_file, "r").read(),
        text=True
    )
except Exception as e:
    print(f"Error running simulation: {e}")
finally:
    # Clean up the temporary input file
    os.remove(input_file)

print("Simulation complete.")
