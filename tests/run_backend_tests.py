import json
import os
import logging
from controller.backends import GPTBackend, ClaudeBackend, GeminiBackend, DeepSeekBackend, StubBackend
import csv
from config import config as basic_config
from controller.interpreter import Interpreter

RELATIVE_DATA_PATH = "tests/data/"
TEST_FILENAME = "test_data.json"


def load_test_data(filename):
    """Load test data from a JSON file."""
    script_dir = os.getcwd()
    full_path = os.path.join(script_dir, RELATIVE_DATA_PATH, filename)
    with open(full_path, "r") as f:
        return json.load(f)


def run_tests(test_data, backends):
    """Run tests using the provided backends."""
    results = {}
    # selected_framework = basic_config.get("framework", None)
    # self.animation_manager = AnimationManager(selected_framework, message_streamer)
    # response_manager = Interpreter(None, basic_config)

    for backend_name, backend in backends.items():
        results[backend_name] = []
        for test in test_data["tests"]:
            instruction = test["instruction"]
            messages = [{"role": "user", "content": instruction}]
            response = backend.generate_response(messages)
            # if (basic_config.get("with_structured_output", False)):
            #     response = response_manager.parse_response(response)
            results[backend_name].append({
                "instruction": instruction,
                "response": response
            })
    return results


def main():
    logging.basicConfig(level=logging.INFO)
    test_data = load_test_data(TEST_FILENAME)

    backends = {
        "GPT": GPTBackend(name="GPT"),
        "Claude": ClaudeBackend(name="Claude"),
        "Gemini": GeminiBackend(name="Gemini"),
        "DeepSeek": DeepSeekBackend(name="DeepSeek"),
    }

    results = run_tests(test_data, backends)

    # Print results
    for backend_name, backend_results in results.items():
        print(f"Results for {backend_name}:")
        for result in backend_results:
            print(f"Instruction: {result['instruction']}")
            print(f"Response: {result['response']}\n")

    # Write results to a CSV file
    csv_filename = "tests/output/test_results.csv"
    with open(csv_filename, mode='w', newline='') as csv_file:
        fieldnames = ['backend', 'instruction', 'response']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for backend_name, backend_results in results.items():
            for result in backend_results:
                writer.writerow({
                    'backend': backend_name,
                    'instruction': result['instruction'],
                    'response': result['response']
                })


if __name__ == "__main__":
    main()
