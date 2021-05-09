import os
import sys
import yaml
from copy import deepcopy


ONTOLOGY_MAPPING = {
    "envo_ontology": "ENVO_terms",
    "go_ontology": "GO_terms"
}

_BUILTIN = 'SampleService.core.validator.builtin'
_NOOP = [{
    'callable_builder': 'noop',
    'module': _BUILTIN
    }]

def find_ontology_validator(data_field, key, ontology_validators):
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

def expand_validators(val, validators):
    if 'validators' not in val:
        val['validators'] = []
    if 'units' in validators:
        v = {
            'callable_builder': 'units',
            'module': _BUILTIN,
            }
        v['parameters'] = {
                'key': 'units',
                'units': validators['units']
                }
        val['validators'].append(v)
    if 'type' not in validators:
        print("type required for validator")
        print(validators)
        raise ValueError("Missing type")
    typ = validators['type']
    v = {
        'callable_builder': typ,
        'module': _BUILTIN,
        }
    if typ=='number':
        v['parameters'] = {'keys': 'value'}
        for p in ['gte', 'lte', 'gt', 'lt', 'required']:
            if p in validators:
                v['parameters'][p] = validators[p]
    elif typ=='enum':
        v['parameters'] = {'allowed-values': validators['allowed-values']}
    elif typ=='ontology':
        v['callable_builder'] = 'ontology_has_ancestor'
        v['parameters'] = {
                'ontology': validators['ontology'],
                'ancestor_term': validators['ancestor_term']
                }
    elif typ=='string':
        v['parameters'] = {'max-len': validators['max-len']}
    else:
        print("type not recongnized %s" % (typ))
        raise KeyError("type %s not recognized" % (typ))
    val['validators'].append(v)
    return True


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
        if 'validators' in val:
            validators = val.pop('validators')
            expand_validators(val, validators)
        if 'validators' not in val:
            val['validators'] = deepcopy(_NOOP)

        val_data[key] = val
    return val_data


def merge_validation_files(files, output_file, ontology_file):
    validators = {}
    prefix_validators = {}
    ontology_validators = {}

    for f in files:
        origin_file = f.split('.')[0]
        with open(f) as f_in:
            data = yaml.load(f_in, Loader=yaml.SafeLoader)
        prefix = ''
        if 'namespace' in data:
            prefix = data['namespace'] + ":"
        for val_type, val_data in [
            ('validators', validators), ('prefix_validators', prefix_validators)
        ]:
            if data.get(val_type):
                for key, val in data[val_type].items():
                    keyname = prefix + key
                    val_data = merge_to_existing_validators(
                        val_type, val_data, keyname, val, data
                    )
                    ontology_validators = find_ontology_validator(
                        data[val_type], key, ontology_validators
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
    if len(sys.argv) < 3:
        raise RuntimeError('Please provide both output file and ontology '
                           'file paths as arguments to merge_validators.py')
    if len(sys.argv) > 3:
        raise RuntimeError("Too many arguments for merge_validators.py")
    # get input files
    output_file = sys.argv[1]
    ontology_file = sys.argv[2]
    if not output_file.endswith('.yml') and not output_file.endswith('.yaml'):
        output_file = output_file + '.yml'
    if not ontology_file.endswith('.yml') and not ontology_file.endswith('.yaml'):
        ontology_file = ontology_file + '.yml'
    files = os.listdir('validation_files')
    files = ['validation_files/' + f for f in files]
    merge_validation_files(files, output_file, ontology_file)
    print(f"    Validators merged, written to {output_file}")
