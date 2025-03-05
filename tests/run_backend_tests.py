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
from prompt import intro_prompt

RELATIVE_DATA_PATH = "tests/data/"

# TEST_FILENAME = "test_data.json"
TEST_FILENAME = "mini_test_data.json"


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

    # Switch Order
    for backend_name, backend in backends.items():
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

            try:
                if (basic_config.get("with_structured_output", False)):
                    parsed_response = response_manager.parse_structured(
                        response, backend_name)

                else:
                    parsed_response = response_manager.parse_response(response)

                results[backend_name].append({
                    "instruction":
                    instruction,
                    "difficulty":
                    test.get('difficulty', ""),
                    "reasoning":
                    parsed_response['reasoning'],
                    "animation_sequence":
                    json.dumps(parsed_response['animation_sequence'],
                               indent=2),
                    "expected_animation":
                    json.dumps(test.get('expected_output', ""), indent=2),
                    "additionals":
                    json.dumps(parsed_response.get('additionals', ""),
                               indent=2),
                })
            except Exception as e:
                results[backend_name].append({
                    "instruction":
                    instruction,
                    "difficulty":
                    test.get('difficulty', ""),
                    "reasoning":
                    response,
                    "animation_sequence":
                    " ",
                    "expected_animation":
                    " ",
                    "additionals":
                    " ",
                })
                print(f"Error parsing structured response for {backend}: {e}")

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


def write_csv(backend, results):
    try:
        # Write results to a CSV file
        csv_filename = f"tests/output/all_test_results_{basic_config['framework']}_{backend}.csv"
        with open(csv_filename, mode='w+', newline='',
                  encoding="utf-8") as csvfile:
            if basic_config["with_structured_output"]:
                fieldnames = [
                    'backend', 'difficulty', 'instruction',
                    'expected_animation', 'animation_sequence', 'reasoning',
                    'additionals'
                ]
            else:
                fieldnames = [
                    'backend',
                    'difficulty',
                    'instruction',
                    'expected_animation',
                    'animation_sequence',
                    'reasoning',
                ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for backend_name, backend_results in results.items():
                for result in backend_results:
                    if basic_config["with_structured_output"]:
                        writer.writerow({
                            'backend':
                            backend_name,
                            "difficulty":
                            result['difficulty'],
                            'instruction':
                            result['instruction'],
                            'expected_animation':
                            "\"" + result['expected_animation'] + "\"",
                            'animation_sequence':
                            "\"" + result['animation_sequence'] + "\"",
                            'reasoning':
                            result['reasoning'],
                            "additionals":
                            result['additionals']
                        })
                    else:
                        writer.writerow({
                            'backend':
                            backend_name,
                            'difficulty':
                            result['difficulty'],
                            'instruction':
                            result['instruction'],
                            'expected_animation':
                            "\"" + result['expected_animation'] + "\"",
                            'reasoning':
                            result['reasoning'],
                            'animation_sequence':
                            "\"" + result['animation_sequence'] + "\"",
                        })
    except Exception as e:
        print(f"Error writing results to CSV: {e}")
        # dump the results to a text file
        with open(
                f"tests/output/all_test_results_{basic_config['framework']}.txt",
                "w") as text_file:
            # write the entire file as is
            text_file.write(json.dumps(results, indent=2))


# backend = 'claude'
# backend = 'GPT'
# backend = 'gemini'
backend = 'all_three'


def main():
    logging.basicConfig(level=logging.INFO)
    # test_data = load_test_data(MINI_TEST_FILENAME)
    test_data = load_test_data(TEST_FILENAME)
    backends = {
        "GPT": GPTBackend(name="GPT", config=basic_config),
        "Claude": ClaudeBackend(name="Claude", config=basic_config),
        "Gemini": GeminiBackend(name="Gemini", config=basic_config),
        # "DeepSeek": DeepSeekBackend(name="DeepSeek", config=basic_config),
    }
    results = run_tests(test_data, backends)
    write_csv(backend, results)


def load_file(backend, write_csv):
    with open(f"tests/output/all_test_results_{basic_config['framework']}.txt",
              "r") as text_file:
        # read the entire file as is
        results = json.load(text_file)
        # print(results)

        write_csv(backend, results)


if __name__ == "__main__":
    # main()

    load_file(backend, write_csv)
