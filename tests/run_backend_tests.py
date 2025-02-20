import json
import os
import logging
from controller.backends import GPTBackend, ClaudeBackend, GeminiBackend, DeepSeekBackend, StubBackend

RELATIVE_DATA_PATH = "tests/data/"
TEST_FILENAME = "data_filled.json"


def load_test_data(filename):
    """Load test data from a JSON file."""
    script_dir = os.getcwd()
    full_path = os.path.join(script_dir, RELATIVE_DATA_PATH, filename)
    with open(full_path, "r") as f:
        return json.load(f)


def run_tests(test_data, backends):
    """Run tests using the provided backends."""
    results = {}
    for backend_name, backend in backends.items():
        results[backend_name] = []
        for test in test_data["tests"]:
            instruction = test["instruction"]
            messages = [{"role": "user", "content": instruction}]
            response = backend.generate_response(messages)
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
        "Stub": StubBackend(name="Stub")
    }

    results = run_tests(test_data, backends)

    # Print results
    for backend_name, backend_results in results.items():
        print(f"Results for {backend_name}:")
        for result in backend_results:
            print(f"Instruction: {result['instruction']}")
            print(f"Response: {result['response']}\n")


if __name__ == "__main__":
    main()
