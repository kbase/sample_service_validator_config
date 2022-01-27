import json
import os
import sys

import yaml

SPECS_DIR = "specs"


def create_groups(output_dir):
    source_file = f"{SPECS_DIR}/ordered.yml"

    os.makedirs(os.path.dirname(f"{output_dir}/"), exist_ok=True)

    with open(source_file) as fin:
        ordered = yaml.load(fin, Loader=yaml.SafeLoader)

    # Fix up the file.
    groups = []
    for group in ordered["ordered"]:
        group["title"] = group["display"]
        group.pop("display")
        group["fields"] = group["ordered_fields"]
        group.pop("ordered_fields")
        groups.append(group)

    output_filename = f"{output_dir}/groups.json"

    with open(output_filename, "w") as fout:
        json.dump(groups, fout, indent=4)


def main():
    # assert correct number of arguments.
    if len(sys.argv) > 2:
        raise RuntimeError(f"Too many arguments provided to create-groups.py")

    if len(sys.argv) == 1:
        print(f"Output directory is required.")
        sys.exit(1)

    output_directory = sys.argv[1]

    create_groups(output_directory)


if __name__ == "__main__":
    main()
