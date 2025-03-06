import json
import os
import logging
from animation.animation_manager import AnimationManager
from controller.backends import GPTBackend, ClaudeBackend, GeminiBackend, DeepSeekBackend, StubBackend
import csv
# from config import config as basic_config

from configs.config_conceptual import config as basic_config
# from configs.config_kivsee import config as basic_config

from controller.interpreter import Interpreter
from controller.response_schema import ResponseSchema
from prompt import intro_prompt

RELATIVE_DATA_PATH = "tests/data/"

# TEST_FILENAME = "test_data.json"
TEST_FILENAME = "mini_test_data.json"


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
    if general_knowledge:
        prompt_parts.append("\n### General Knowledge\n")
        prompt_parts.append(general_knowledge)
    if animation_knowledge:
        prompt_parts.append("\n### Animation Knowledge\n")
        prompt_parts.append(animation_knowledge)
    # if song_structure:
    #     prompt_parts.append("\n### Song Structure\n")
    #     prompt_parts.append(song_structure)
    if world_structure:
        prompt_parts.append("\n### World Structure\n")
        prompt_parts.append(world_structure)

    full_prompt = "\n".join(prompt_parts)

    return full_prompt


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
        test_results = {
            "instruction": instruction,
            "difficulty": test.get('difficulty', ""),
            "expected_output": test.get("expected_output", "")
        }

        for backend_name, backend in backends.items():
            messages = [{
                "role": "system",
                "content": full_prompt
            }, {
                "role": "user",
                "content": instruction
            }]
            try:
                response = backend.generate_response(messages)
            except Exception as e:
                response = f"Error: {str(e)}"

            if isinstance(response, ResponseSchema):
                test_results[backend_name] = response.model_dump_json(indent=4)
            elif isinstance(response, str):
                data = json.loads(response)
                formatted_json = json.dumps(data, indent=2)
                test_results[backend_name] = formatted_json
            else:
                test_results[backend_name] = response

        results.setdefault("tests", []).append(test_results)
    return results


def write_csv(results):
    try:
        tested_backends = "_".join([backend for backend in results.keys()])
        csv_filename = f"tests/output/csv_{basic_config['framework']}_{tested_backends}.csv"
        with open(csv_filename, mode='w+', newline='',
                  encoding="utf-8") as csvfile:
            fieldnames = ['instruction', 'difficulty', 'expected_output'
                          ] + list(results["tests"][0].keys())[2:]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for test_result in results["tests"]:
                writer.writerow(test_result)
    except Exception as e:
        print(f"Error writing results to CSV: {e}")
        full_name = f"tests/output/dump_{basic_config['framework']}_results.txt"
        with open(full_name, "w+") as text_file:
            text_file.write(json.dumps(results, indent=2))
        print(f"Results dumped to {full_name}")


def main():
    logging.basicConfig(level=logging.INFO)
    test_data = load_test_data(TEST_FILENAME)
    backends = {
        # "GPT": GPTBackend(name="GPT", config=basic_config),
        # "Claude": ClaudeBackend(name="Claude", config=basic_config),
        # "Gemini": GeminiBackend(name="Gemini", config=basic_config),
        "DeepSeek": DeepSeekBackend(name="DeepSeek", config=basic_config),
    }
    results = run_tests(test_data, backends)
    write_csv(results)


def load_file(backend, write_csv):
    with open(f"tests/output/all_test_results_{basic_config['framework']}.txt",
              "r") as text_file:
        results = json.load(text_file)
        write_csv(backend, results)


if __name__ == "__main__":
    main()

    # load_file(backend, write_csv)
