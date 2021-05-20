import os
import sys
import yaml
import json
from pathlib import PurePosixPath


def create_formats(format_sources, output_dir):
    for format_source in format_sources:
        format_name = PurePosixPath(format_source).stem

        with open(format_source) as fin:
            template = yaml.load(fin, Loader=yaml.SafeLoader)
            # Transform mappings:
            sample_format = {
                'name': format_name,
                'mappings': {
                    'id': template['Mappings']['ID'],
                    'parent': template['Mappings']['ParentID'],
                    'name': template['Mappings']['Name']
                },
                'columns': [],
                'columnsFromSchema': False
            }

            if 'SkipLines' in template['Mappings']:
                sample_format['mappings']['skipLines'] = template['Mappings']['SkipLines']


            # Transform columns:
            if 'Columns' in template:
                for title, column in template['Columns'].items():
                    if 'transformations' not in column:
                        print(f'no transformation in column "{title}')
                        continue
                    column = {
                        'title': title,
                        'aliases': column['aliases'],
                        'sampleKey': column['transformations'][0]['parameters'][0]
                    }
                    sample_format['columns'].append(column)
            else:
                sample_format['columnsFromSchema'] = True

            output_filename = f'{output_dir}/{format_name}.json'
            os.makedirs(os.path.dirname(output_filename), exist_ok=True)
            with open(output_filename, 'w') as fout:
                json.dump(sample_format, fout, indent=4)


if __name__ == "__main__":
    # assert correct number of arguments.
    if len(sys.argv) < 2:
        raise RuntimeError('Please provide the output directory '
                           'as an argument to create-jsonschema.py')
    if len(sys.argv) > 2:
        raise RuntimeError("Too many arguments for create-formats.py")

    output_directory = sys.argv[1]

    files = os.listdir('templates')
    files = ['templates/' + f for f in files]
    create_formats(files, output_directory)
    print(f"Templates converted to formats in '{output_directory}'")
