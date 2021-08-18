import json
import os
import re
import sys

import yaml

KEEP_FILES = False


####
# python scripts/create-jsonschema.py outputdir
#
# E.g.
# python scripts/create-jsonschema.py _temp/schemas
#
####

def copy_if(source, from_key, dest, to_key=None, must=False):
    if to_key is None:
        to_key = from_key
    if from_key in source:
        dest[to_key] = source[from_key]
    elif must:
        raise Exception(f'key "{from_key}" must exist in source')
    return dest


def transform_validator(key, validator):
    schema = {
        '$schema': 'http://json-schema.org/draft-07/schema#',
        'kbase': {
            'sample': {
                'key': key
            }
        }
    }

    copy_if(validator, 'title', schema, must=True)
    copy_if(validator, 'description', schema, must=True)
    copy_if(validator, 'examples', schema, must=True)

    if 'type' not in validator:
        raise Exception('The type is required')

    if validator['type'] == 'string':
        schema['type'] = 'string'
        schema = copy_if(validator, 'format', schema)
        schema = copy_if(validator, 'minLength', schema)
        schema = copy_if(validator, 'maxLength', schema)
        schema = copy_if(validator, 'ancestorTerm', schema)
        schema = copy_if(validator, 'namespace', schema)
        copy_if(validator, 'enum', schema, 'enum')
    elif validator['type'] == 'number':
        schema['type'] = 'number'
        schema = copy_if(validator, 'minimum', schema)
        schema = copy_if(validator, 'minimumExclusive', schema)
        schema = copy_if(validator, 'maximum', schema)
        schema = copy_if(validator, 'maximumExclusive', schema)
    elif validator['type'] == 'integer':
        schema['type'] = 'integer'
        schema = copy_if(validator, 'minimum', schema)
        schema = copy_if(validator, 'minimumExclusive', schema)
        schema = copy_if(validator, 'maximum', schema)
        schema = copy_if(validator, 'maximumExclusive', schema)
    else:
        raise Exception(f'Unsupported type: {validator["type"]}')

    if 'units' in validator:
        schema['kbase']['unit'] = validator['units']

    if 'formatting' in validator:
        schema['kbase']['formatting'] = validator['formatting']

    return schema


def create_schemas(output_dir):
    os.makedirs(os.path.dirname(f'{output_dir}/'), exist_ok=True)

    if KEEP_FILES:
        os.makedirs(os.path.dirname(f'{output_dir}/schemas/'), exist_ok=True)

    validation_files = ['vocabularies/' + f for f in os.listdir('vocabularies')]

    all_schemas = []
    for validation_file in validation_files:

        print(f'Merging {validation_file}...')
        with open(validation_file) as f_in:
            validator_config = yaml.load(f_in, Loader=yaml.SafeLoader)

        key_prefix = ''
        if 'namespace' in validator_config:
            key_prefix = validator_config['namespace'] + ":"

        for key, validator in validator_config['terms'].items():
            namespaced_key = key_prefix + key

            ui_schema = transform_validator(namespaced_key, validator)
            all_schemas.append(ui_schema)

            if KEEP_FILES:
                # should not use ":" in filenames (will fail on windows), so
                # substitute with "-".
                output_filename = re.sub(r':', '-', namespaced_key)
                output_filename = f'{output_dir}/schemas/{output_filename}.json'
                with open(output_filename, 'w') as f:
                    json.dump(ui_schema, f, indent=4)

    # Save all schemas into a big JSON array.
    # This is convenient, for the time being, to support front ends which
    # need to fake a "get_schemas" method before it is available.
    with open(f'{output_dir}/schemas.json', 'w') as f:
        json.dump(all_schemas, f, indent=4)


def main():
    # assert correct number of arguments.
    if len(sys.argv) > 2:
        raise RuntimeError(f"Too many arguments provided to create-jsonschema.py")

    if len(sys.argv) == 1:
        print(f"Output directory is required.")
        sys.exit(1)

    output_directory = sys.argv[1]

    create_schemas(output_directory)
    print(f"Validators transformed to jsonschema, written to '{output_directory}'.")


if __name__ == "__main__":
    main()
