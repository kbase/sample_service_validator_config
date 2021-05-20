import os
import sys
import yaml
import json


def create_groups(source_file, output_dir):
    with open(source_file) as fin:
        ordered = yaml.load(fin, Loader=yaml.SafeLoader)

    # Fix up the file.
    groups = []
    for group in ordered['ordered']:
        group['title'] = group['display']
        group.pop('display')
        group['fields'] = group['ordered_fields']
        group.pop('ordered_fields')
        groups.append(group)

    output_filename = f'{output_dir}/groups.json'
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    with open(output_filename, 'w') as fout:
        json.dump(groups, fout, indent=4)


if __name__ == "__main__":
    # assert correct number of arguments.
    if len(sys.argv) < 2:
        raise RuntimeError('Please provide the output directory '
                           'as an argument to create-jsonschema.py')
    if len(sys.argv) > 2:
        raise RuntimeError("Too many arguments for create-formats.py")

    output_directory = sys.argv[1]

    file = 'ordered.yml'
    create_groups(file, output_directory)
    print(f"Ordered config converted to groups in '{output_directory}'")
