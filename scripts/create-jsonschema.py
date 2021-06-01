import os
import sys
import yaml
import json
import re


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

    if validator['type'] == 'enum':
        schema['type'] = 'string'
        copy_if(validator, 'allowed-values', schema, 'enum')
    elif validator['type'] == 'string':
        schema['type'] = 'string'
        schema = copy_if(validator, 'format', schema)
        schema = copy_if(validator, 'minLength', schema)
        schema = copy_if(validator, 'maxLength', schema)
        schema = copy_if(validator, 'ancestorTerm', schema)
        schema = copy_if(validator, 'namespace', schema)
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


def transform_validation_files(validation_files, output_dir):
    for validation_file in validation_files:

        print(f'Merging {validation_file}...')
        with open(validation_file) as f_in:
            validator_config = yaml.load(f_in, Loader=yaml.SafeLoader)

        key_prefix = ''
        if 'namespace' in validator_config:
            key_prefix = validator_config['namespace'] + ":"

        for key, validator in validator_config['terms'].items():
            namespaced_key = key_prefix + key
            # should not use ":" in filenames (will fail on windows), so
            # substitute with "-".
            output_filename = re.sub(r':', '-', namespaced_key)

            ui_schema = transform_validator(namespaced_key, validator)
            output_filename = f'{output_dir}/{output_filename}.json'
            os.makedirs(os.path.dirname(output_filename), exist_ok=True)
            with open(output_filename, 'w') as f:
                json.dump(ui_schema, f, indent=4)


if __name__ == "__main__":
    # assert correct number of arguments.
    if len(sys.argv) < 2:
        raise RuntimeError('Please provide the output directory '
                           'as an argument to create-jsonschema.py')
    if len(sys.argv) > 2:
        raise RuntimeError("Too many arguments for create-jsonschema.py")

    # get input files
    output_directory = sys.argv[1]

    files = os.listdir('vocabularies')
    files = ['vocabularies/' + f for f in files]
    transform_validation_files(files, output_directory)
    print(f"Validators transformed to jsonschema, written to {output_directory}")
