import json
import os
import sys

import yaml

KEEP_FILES = False


def create_formats(output_dir):
    format_sources = ['templates/' + f for f in os.listdir('templates')]

    os.makedirs(os.path.dirname(f'{output_dir}/'), exist_ok=True)

    if KEEP_FILES:
        os.makedirs(os.path.dirname(f'{output_dir}/formats/'), exist_ok=True)

    all_formats = []
    for format_source in format_sources:
        with open(format_source) as fin:
            template = yaml.load(fin, Loader=yaml.SafeLoader)
            format_name = template['Template']
            # Transform mappings:
            sample_format = {
                'name': format_name,
                'mappings': {
                    'id': template['ID'],
                    'parent': template['Parent'],
                    'name': template['Name']
                },
                'columns': [],
                'columnsFromSchema': False
            }

            if 'Config' in template:
                if 'skipLines' in template['Config']:
                    sample_format['mappings']['skipLines'] = template['Config'][
                        'skipLines']

            # Transform columns:
            if 'Columns' in template:
                for title, column in template['Columns'].items():
                    new_column = {
                        'title': title,
                        'sample': {
                            'key': column['transformations'][0]['parameters'][0]
                        }
                    }

                    if 'aliases' in column:
                        new_column['aliases'] = column['aliases']

                    if 'apiKey' in column and column['apiKey'] != '??':
                        new_column['apiKey'] = column['apiKey']

                    if 'disposition' in column:
                        new_column['disposition'] = column['disposition']

                    sample_format['columns'].append(new_column)
            else:
                sample_format['columnsFromSchema'] = True

            all_formats.append(sample_format)

            if KEEP_FILES:
                output_filename = f'{output_dir}/formats/{format_name}.json'
                with open(output_filename, 'w') as fout:
                    json.dump(sample_format, fout, indent=4)

    # Save all schemas into a big JSON array.
    # This is convenient, for the time being, to support front ends which
    # need to fake a "get_schemas" method before it is available.
    with open(f'{output_dir}/formats.json', 'w') as f:
        json.dump(all_formats, f, indent=4)


def main():
    # assert correct number of arguments.
    if len(sys.argv) > 2:
        raise RuntimeError(f"Too many arguments provided to create-formats.py")

    if len(sys.argv) == 1:
        print(f"Output directory is required.")
        sys.exit(1)

    output_directory = sys.argv[1]

    create_formats(output_directory)
    print(f"Templates converted to formats in '{output_directory}'.")


if __name__ == "__main__":
    main()
