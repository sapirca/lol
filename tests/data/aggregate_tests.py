import os
import json
import argparse

# python /Users/sapir/repos/lol/tests/data/aggregate_tests.py --difficulty Moderate
# Define the difficulty levels
difficulty_levels = ["Basic", "Moderate", "Intermediate"]

# Parse command-line arguments
parser = argparse.ArgumentParser(
    description='Aggregate tests based on difficulty.')
parser.add_argument('--difficulty',
                    choices=difficulty_levels,
                    required=True,
                    help='The difficulty level of the tests to aggregate.')
args = parser.parse_args()

# Define the input and output directories
input_dir = f'/Users/sapir/repos/lol/tests/data/0{difficulty_levels.index(args.difficulty)}_{args.difficulty.lower()}'
output_file = f'/Users/sapir/repos/lol/tests/data/{args.difficulty.lower()}_tests.json'

# Aggregate all individual test files into one file
aggregated_tests = []
for filename in os.listdir(input_dir):
    if filename.endswith('.json'):
        with open(os.path.join(input_dir, filename), 'r') as file:
            test = json.load(file)
            # Remove the wrapping "tests": [ { ... } ]
            if "tests" in test and isinstance(test["tests"], list):
                aggregated_tests.extend(test["tests"])

# Write the aggregated tests to the output file
with open(output_file, 'w') as file:
    file.write('{\n    "tests":\n')
    json.dump(aggregated_tests, file, indent=4)
    file.write('\n}')

print(
    f"Aggregated {len(aggregated_tests)} {args.difficulty.lower()} tests into {output_file}"
)
