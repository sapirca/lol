# simulation.py

from datetime import datetime
import os
import subprocess
from simulations.user_inputs import user_inputs
print("Running AI Agent Simulation...")

try:
    process = subprocess.run(
        ["python", "console.py"],
        input="\n".join(user_inputs),
        text=True
    )
except Exception as e:
    print(f"Error running simulation: {e}")

print("Simulation complete.")