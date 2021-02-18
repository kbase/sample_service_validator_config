import os
import sys
import yaml
from ontology_utils import create_ontology_mapping


def find_ontology_validator(data_field, key, ontology_validators, ONTOLOGY_MAPPING):
    if data_field[key].get('validators'):
        for validator in data_field[key]['validators']:
            if validator['callable_builder'] == 'ontology_has_ancestor':
                if not ontology_validators.get(key):
                    ontology_validators[key] = []
                ontology_validators[key].append({
                    "validator_type": "ontology_has_ancestor",
                    "ontology": validator.get('parameters', {}).get('ontology'),
                    "ontology_collection": ONTOLOGY_MAPPING.get(validator.get('parameters', {}).get('ontology'), ""),
                    "ancestor_term": validator.get('parameters', {}).get('ancestor_term'),
                    "display_name": data_field[key].get('key_metadata', {}).get('display_name')
                })
    return ontology_validators


def merge_to_existing_validators(val_type, val_data, key, val, data):
    if val_data.get(key):
        # update auxilliary fields and not the 'validators'
        for data_field in ['static_mappings', 'key_metadata']:
            if data[val_type][key].get(data_field):
                if val_data[key].get(data_field):
                    for sub_key, sub_val in data[val_type][key][data_field].items():
                        val_data[key][data_field][sub_key] = sub_val
                else:
                    val_data[key][data_field] = data[val_type][key][data_field]
    else:
        val_data[key] = val
    return val_data


def merge_validation_files(files, output_file, ontology_file, env):
    validators = {}
    prefix_validators = {}
    ontology_validators = {}
    ONTOLOGY_MAPPING = create_ontology_mapping(env)

    for f in files:
        origin_file = f.split('.')[0]
        with open(f) as f_in:
            data = yaml.load(f_in, Loader=yaml.SafeLoader)
        for val_type, val_data in [
            ('validators', validators), ('prefix_validators', prefix_validators)
        ]:
            if data.get(val_type):
                for key, val in data[val_type].items():
                    ontology_validators = find_ontology_validator(
                        data[val_type], key, ontology_validators, ONTOLOGY_MAPPING
                    )
                    val_data = merge_to_existing_validators(
                        val_type, val_data, key, val, data
                    )

    v_keys = sorted(list(validators.keys()))
    pv_keys = sorted(list(prefix_validators.keys()))

    data = {}
    if validators:
        data['validators'] = validators
    if prefix_validators:
        data['prefix_validators'] = prefix_validators
    # try default_style with quotes here.
    with open(output_file, 'w') as f:
        yaml.dump(data, f)  #, default_style='"')
    # save ontology_file
    with open(ontology_file, 'w') as f:
        yaml.dump(ontology_validators, f)  # , default_stype='"')


if __name__ == "__main__":
    # assert correct number of arguments.
    if len(sys.argv) < 4:
        raise RuntimeError('Please provide the environment, output file and ontology '
                           'file paths as arguments to merge_validators.py')
    if len(sys.argv) > 4:
        raise RuntimeError("Too many arguments for merge_validators.py")
    # get input files
    output_file = sys.argv[1]
    ontology_file = sys.argv[2]
    env = str(sys.argv[3])
    env = env.lower()
    print(f"Running merge_validators to output files {output_file} and {ontology_file} in environment '{env}'.")
    # make sure env is a valid environment
    if env not in ['ci', 'appdev', 'narrative', 'narrative-dev']:
        raise ValueError(f"environment '{env}' not in approved list of environments ['ci', 'appdev', 'narrative', 'narrative-dev']")
    if not output_file.endswith('.yml') and not output_file.endswith('.yaml'):
        output_file = output_file + '.yml'
    if not ontology_file.endswith('.yml') and not ontology_file.endswith('.yaml'):
        ontology_file = ontology_file + '.yml'
    files = os.listdir('validation_files')
    files = ['validation_files/' + f for f in files]
    merge_validation_files(files, output_file, ontology_file, env)
    print(f"    Validators merged, written to {output_file}")
