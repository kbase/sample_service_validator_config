import os
import sys
import yaml


def validate_template(template_file):
    with open(template_file) as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    # confirm a few aspects of the file
    keys = ['Columns', 'ID', 'Name', 'Template']
    data_keys = list(data.keys())
    for key in keys:
        if key not in data_keys:
            raise ValueError(f"Missing required key {key} from file {template_file}")
    '''
    1.) make sure no two files have the same transformation
    2.) make surew no alias maps to multiple fields
    '''
    existing_validation_targets = {}
    existing_alias_targets = {}
    existing_orders = {}
    for term, datum in data['Columns'].items():
        for transform in datum.get('transformations', []):
            # first parameter is always the validation target field
            v = transform['parameters'][0]
            if v in existing_validation_targets:
                other_term = existing_validation_targets[v]
                raise ValueError(f"cannot use the same validation field \"{v}\" for multiple terms: \"{term}\" and \"{other_term}\"")
            else:
                existing_validation_targets[v] = term
        for alias in datum.get('aliases', []):
            if alias in existing_alias_targets:
                other_term = existing_alias_targets[alias]
                raise ValueError(f'Alias {alias} maps to multiple terms: "{term}" and "{other_term}"')
            else:
                existing_alias_targets[alias] = term
        if datum.get('order'):
            order = datum.get('order')
            if order in existing_orders:
                other_term = existing_orders[order]
                raise ValueError(f'template file "{template_file}" has collision on "order" field on terms: "{term}" and "{other_term}"')
            else:
                existing_orders[order] = term


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise RuntimeError(f'Please provide template files for validation')
    for template_file in sys.argv[2:]:
        validate_template(template_file)
