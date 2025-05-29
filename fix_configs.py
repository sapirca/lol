import os
import json

# Main flags that should be removed from snapshot configs
MAIN_FLAGS = {
    "print_internal_messages",
    "auto_render",
    "show_all_animations",  # old name
    "send_llm_all_animations"  # new name
}


def fix_config_file(config_path):
    """Fix a single config file by removing main flags."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Remove main flags
        for flag in MAIN_FLAGS:
            config.pop(flag, None)

        # Write back the cleaned config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)

        print(f"Fixed {config_path}")
    except Exception as e:
        print(f"Error fixing {config_path}: {e}")


def main():
    # Find all config files
    snapshots_dir = "ui/tkinter/snapshots"
    for root, dirs, files in os.walk(snapshots_dir):
        if "config.json" in files:
            config_path = os.path.join(root, "config.json")
            fix_config_file(config_path)


if __name__ == "__main__":
    main()
