import json
import os


def read_and_print_tests(filename):
    """
    Reads animation test data from a JSON file, prints the setup prompt once,
    and then prints the instructions, difficulty, and JSON representation of 
    the expected output for each test case.

    Args:
        filename (str): The name of the JSON file to read, relative to the workspace directory.
    """
    try:
        print()
        print("-" * 20)  # Separator
        print("Loading test file data...")
        # Assuming the workspace directory is the directory containing the script.
        working_dir = os.getcwd()

        print(working_dir)
        # Construct the full file path by joining the working directory and the filename.
        full_path = os.path.join(working_dir, filename)
        print(full_path)

        with open(full_path, "r") as f:
            test_data = json.load(f)
        print("-" * 20)  # Separator

        if "tests" in test_data and isinstance(test_data["tests"], list):
            for test in test_data["tests"]:
                instruction = test.get("instruction")
                difficulty = test.get("difficulty")
                expected_output = test.get("expected_output")
                if instruction and difficulty and expected_output:
                    index = test_data["tests"].index(test) + 1
                    print(f"{index}. [{difficulty}] {instruction}")
                    # print(json.dumps(expected_output,
                    #                  indent=4))  # Print JSON with indentation
                    # print("-" * 20)  # Separator
                    print()
                else:
                    print("Error: Incomplete test data found.")
        else:
            print("Error: Test data is not a list or missing 'tests' key.")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found. Full path: {full_path}")
    except json.JSONDecodeError:
        print(
            f"Error: Invalid JSON format in '{filename}'. Full path: {full_path}"
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

RELATIVE_DATA_PATH = "tests/data/"
if __name__ == "__main__":
    # read_and_print_tests(filename="tests/data/basic_tests.json")
    read_and_print_tests(filename=f"{RELATIVE_DATA_PATH}moderate_tests.json")
