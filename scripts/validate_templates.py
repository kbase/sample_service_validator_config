import sys
import yaml


def validate_template(template_file):
    """
    This function does the following checks within a template file:
    1.) file contains 'Columns', 'ID', 'Name' and 'Template' fields at highest level
    2.) No two terms in 'Columns' have the same transformation target
    3.) No two terms in 'Columns' share aliases
    4.) No collisions on 'order' field between terms
    """
    with open(template_file) as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)

    # Confirm top level keys
    keys = ['Template', 'ID', 'Parent', 'Name',  'Columns']
    data_keys = list(data.keys())
    for key in keys:
        if key not in data_keys:
            raise ValueError(f"Required key {key} missing from template file {template_file}")

    existing_validation_targets = {}
    existing_alias_targets = {}
    existing_orders = {}
    for term, datum in data['Columns'].items():
        for transform in datum.get('transformations', []):
            # first parameter is always the validation target field
            v = transform['parameters'][0]
            if v in existing_validation_targets:
                other_term = existing_validation_targets[v]
                raise ValueError(
                    f"cannot use the same validation field \"{v}\" for multiple "
                    f"terms: \"{term}\" and \"{other_term}\"")
            else:
                existing_validation_targets[v] = term
        for alias in datum.get('aliases', []):
            if alias in existing_alias_targets:
                other_term = existing_alias_targets[alias]
                raise ValueError(
                    f'Alias {alias} maps to multiple terms: "{term}" and "'
                    f'{other_term}"')
            else:
                existing_alias_targets[alias] = term
        if datum.get('order'):
            order = datum.get('order')
            if order in existing_orders:
                other_term = existing_orders[order]
                raise ValueError(
                    f'template file "{template_file}" has collision on "order" field '
                    f'on terms: "{term}" and "{other_term}"')
            else:
                existing_orders[order] = term


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise RuntimeError(f'Please provide template files for validation')
    for template_file in sys.argv[2:]:
        validate_template(template_file)
