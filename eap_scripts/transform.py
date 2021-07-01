import os
import sys
import json
import create_formats
import create_schemas
import create_groups
import validate

DEFAULT_OUTPUT_DIRECTORY = '_temp'


def verify(output_dir):
    ####
    # Load transformed data
    ####

    # Load groups
    with open(f'{output_dir}/groups.json') as fin:
        groups = json.load(fin)

    duplicate_group_fields = []
    group_keys = {}
    for group in groups:
        for field_key in group['fields']:
            if field_key in group_keys:
                duplicate_group_fields.append({
                    'group': group['name'],
                    'field_key': field_key,
                    'first_group': group_keys[field_key]
                })
            else:
                group_keys[field_key] = group['name']

    # Load schemas
    with open(f'{output_dir}/schemas.json') as fin:
        schemas = json.load(fin)

    schemas_by_field = {}
    for schema in schemas:
        schemas_by_field[schema['kbase']['sample']['key']] = schema

    # Load formats
    formats = []
    formats_key_map = []
    for format_file in os.listdir(f'{output_dir}/formats'):
        column_map = {}
        with open(f'{output_dir}/formats/{format_file}') as fin:
            format = json.load(fin)
            formats.append(format)
            for column in format['columns']:
                column_map[column['sample']['key']] = column
            formats_key_map.append({
                'name': format['name'],
                'column_map': column_map
            })

    ####
    # Verifications
    ####

    # check that groups do not repeat fields

    # check that all fields in groups are defined in schemas
    group_undefined_fields = []
    for group in groups:
        for field_key in group['fields']:
            if field_key not in schemas_by_field:
                group_undefined_fields.append({
                    'group': group['name'],
                    'field_key': field_key
                })

    # Check schemas
    schema_fields_not_in_group = []
    schema_fields_not_in_format = []
    for schema in schemas:
        # check that all fields defined in schemas are in only one group
        field_key = schema['kbase']['sample']['key']
        if field_key not in group_keys:
            schema_fields_not_in_group.append(schema)

        # check that schema fields are in at least one format.
        found_in_format = False
        for format in formats_key_map:
            if field_key in format['column_map']:
                found_in_format = True
                break
        # print(f'not found: {field_key}, {key_map}')
        if found_in_format is False:
            schema_fields_not_in_format.append(schema)

    # Check for formats with undefined fields.
    format_column_not_in_schema = []
    ignored_format_column_in_schema = []
    ignored_format_column_in_groups = []
    for format in formats:
        for column in format['columns']:
            if 'disposition' in column and column['disposition'] == 'ignore':
                # Ignored fields should not have a schema
                if column['sample']['key'] in schemas_by_field:
                    ignored_format_column_in_schema.append({
                        'format': format['name'],
                        'column': column
                    })
                # And should not be in a group either.
                if column['sample']['key'] in group_keys:
                    ignored_format_column_in_groups.append({
                        'format': format['name'],
                        'column': column
                    })
            else:
                # A format field must have a schema
                if column['sample']['key'] not in schemas_by_field:
                    format_column_not_in_schema.append({
                        'format': format['name'],
                        'column': column
                    })
                # A format field must be in a group is implied by above, since
                # we already ensure that all defined fields are in a group.

    ####
    # Print diagnostics if inconsistencies found.
    ####
    if len(duplicate_group_fields):
        print()
        print('!! Duplicate fields found in groups')
        for field in duplicate_group_fields:
            print(
                f"    '{field['field_key']}' in '{field['group']}' but first in "
                f"'{field['first_group']}'")

    if len(group_undefined_fields):
        print()
        print('!! Fields found in groups which are not defined in schemas')
        for field in group_undefined_fields:
            print(f"    '{field['field_key']}' in group '{field['group']}'")

    if len(schema_fields_not_in_group):
        print()
        print('!! Schemas found whose sample key is not in a group')
        for schema in schema_fields_not_in_group:
            print(f"    '{schema['kbase']['sample']['key']}'")

    if len(schema_fields_not_in_format):
        print()
        print('!! Schemas found whose sample key is not in a format')
        for schema in schema_fields_not_in_format:
            print(f"    {schema['kbase']['sample']['key']}")

    if len(format_column_not_in_schema):
        print()
        print('!! Format column not defined in a schema')
        for undefined in format_column_not_in_schema:
            print(
                f"    '{undefined['column']['sample']['key']}' in '"
                f"{undefined['format']}'")
            print(undefined['column'])

    if len(ignored_format_column_in_schema):
        print()
        print('!! Ignored format column defined in a schema')
        for undefined in ignored_format_column_in_schema:
            print(
                f"    '{undefined['column']['sample']['key']}' in '"
                f"{undefined['format']}'")
            print(undefined['column'])

    if len(ignored_format_column_in_groups):
        print()
        print('!! Ignored format column defined in a group')
        for undefined in ignored_format_column_in_groups:
            print(
                f"    '{undefined['column']['sample']['key']}' in '"
                f"{undefined['format']}'")
            print(undefined['column'])


if __name__ == "__main__":
    # assert correct number of arguments.
    if len(sys.argv) > 2:
        raise RuntimeError(f"Too many arguments provided to verify.py")

    if len(sys.argv) == 1:
        output_directory = DEFAULT_OUTPUT_DIRECTORY
        print(f"Output directory defaulted to '{DEFAULT_OUTPUT_DIRECTORY}'.")
    else:
        output_directory = sys.argv[1]

    create_formats.create_formats(output_directory)
    create_groups.create_groups(output_directory)
    create_schemas.create_schemas(output_directory)

    verify(output_directory)

    validate.validateFile(f'{output_directory}/groups.json', 'groups.json')

    validate.validateFile(f'{output_directory}/formats/sesar.json',
                          'format-with-api.json')
    validate.validateFile(f'{output_directory}/formats/enigma.json', 'format.json')

    for format_file in os.listdir(f'{output_directory}/schemas'):
        validate.validateFile(f'{output_directory}/schemas/{format_file}',
                              'schema.json')
