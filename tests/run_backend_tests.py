import json
import os
import logging
from animation.animation_manager import AnimationManager
from controller.backends import GPTBackend, ClaudeBackend, GeminiBackend, DeepSeekBackend, StubBackend
import csv
from config import config as basic_config
from controller.interpreter import Interpreter
from prompt import intro_prompt

RELATIVE_DATA_PATH = "tests/data/"
# TEST_FILENAME = "test_data.json"

MINI_TEST_FILENAME = "mini_test_data.json"


def load_test_data(filename):
    """Load test data from a JSON file."""
    script_dir = os.getcwd()
    full_path = os.path.join(script_dir, RELATIVE_DATA_PATH, filename)
    with open(full_path, "r") as f:
        return json.load(f)


def run_tests(test_data, backends):
    """Run tests using the provided backends."""
    results = {}
    selected_framework = basic_config.get("framework", None)
    animation_manager = AnimationManager(selected_framework, None)
    response_manager = Interpreter(animation_manager, basic_config)

    full_prompt = prepare_full_prompt(animation_manager)

    for backend_name, backend in backends.items():
        results[backend_name] = []

        for test in test_data["tests"]:
            instruction = test["instruction"]

            messages = [{
                "role": "system",
                "content": full_prompt
            }, {
                "role": "user",
                "content": instruction
            }]
            response = backend.generate_response(messages)

            # if (basic_config.get("with_structured_output", False)):
            parsed_response = response_manager.parse_response(response)

            if basic_config["with_structured_output"]:
                results[backend_name].append({
                    "instruction":
                    instruction,
                    "reasoning":
                    parsed_response['response_wo_animation'],
                    "animation_sequence":
                    parsed_response['animation_sequence'],
                    "pretty_animation":
                    json.dumps(parsed_response['animation_sequence'], indent=2)
                })
            else:
                results[backend_name].append({
                    "instruction": instruction,
                    "response": response
                })
    return results


def prepare_full_prompt(animation_manager):
    """Prepare the full prompt for the backend."""

    song_structure = None
    # song_name = basic_config.get("song_name")
    # song_structure = backend.song_provider.get_song_structure(
    #     song_name) if song_name else ""

    world_structure = animation_manager.get_world_structure()
    general_knowledge = animation_manager.get_general_knowledge()
    animation_knowledge = animation_manager.get_domain_knowledge()

    prompt_parts = []
    if intro_prompt:
        prompt_parts.append(intro_prompt)
    if animation_knowledge:
        prompt_parts.append("\n### Animation Knowledge\n")
        prompt_parts.append(animation_knowledge)
    if general_knowledge:
        prompt_parts.append("\n### General Knowledge\n")
        prompt_parts.append(general_knowledge)
    if song_structure:
        prompt_parts.append("\n### Song Structure\n")
        prompt_parts.append(song_structure)
    if world_structure:
        prompt_parts.append("\n### World Structure\n")
        prompt_parts.append(world_structure)

    full_prompt = "\n".join(prompt_parts)

    return full_prompt


def main():
    logging.basicConfig(level=logging.INFO)
    test_data = load_test_data(MINI_TEST_FILENAME)

    backends = {
        "GPT": GPTBackend(name="GPT", config=basic_config),
        "Claude": ClaudeBackend(name="Claude", config=basic_config),
        "Gemini": GeminiBackend(name="Gemini", config=basic_config),
        "DeepSeek": DeepSeekBackend(name="DeepSeek", config=basic_config),
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
