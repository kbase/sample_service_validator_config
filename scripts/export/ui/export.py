import json
import sys

import create_groups
import create_schemas


def verify(output_dir):
    ####
    # Load transformed data
    ####

    # Load groups
    with open(f"{output_dir}/groups.json") as fin:
        groups = json.load(fin)

    duplicate_group_fields = []
    group_keys = {}
    for group in groups:
        for field_key in group["fields"]:
            if field_key in group_keys:
                duplicate_group_fields.append(
                    {
                        "group": group["name"],
                        "field_key": field_key,
                        "first_group": group_keys[field_key],
                    }
                )
            else:
                group_keys[field_key] = group["name"]

    # Load schemas
    with open(f"{output_dir}/schemas.json") as fin:
        schemas = json.load(fin)

    schemas_by_field = {}
    for schema in schemas:
        schemas_by_field[schema["kbase"]["sample"]["key"]] = schema

    ####
    # Verifications
    ####

    # check that groups do not repeat fields

    # check that all fields in groups are defined in schemas
    group_undefined_fields = []
    for group in groups:
        for field_key in group["fields"]:
            if field_key not in schemas_by_field:
                group_undefined_fields.append(
                    {"group": group["name"], "field_key": field_key}
                )

    # Check schemas
    schema_fields_not_in_group = []
    for schema in schemas:
        # check that all fields defined in schemas are in only one group
        field_key = schema["kbase"]["sample"]["key"]
        if field_key not in group_keys:
            schema_fields_not_in_group.append(schema)

    ####
    # Print diagnostics if inconsistencies found.
    ####
    if len(duplicate_group_fields):
        print()
        print("!! Duplicate fields found in groups")
        for field in duplicate_group_fields:
            print(
                f"    '{field['field_key']}' in '{field['group']}' but first in "
                f"'{field['first_group']}'"
            )

    if len(group_undefined_fields):
        print()
        print("!! Fields found in groups which are not defined in schemas")
        for field in group_undefined_fields:
            print(f"    '{field['field_key']}' in group '{field['group']}'")

    if len(schema_fields_not_in_group):
        print()
        print("!! Schemas found whose sample key is not in a group")
        for schema in schema_fields_not_in_group:
            print(f"    '{schema['kbase']['sample']['key']}'")


def main():
    # assert correct number of arguments.
    if len(sys.argv) > 2:
        raise RuntimeError(f"Too many arguments provided to export.py")

    if len(sys.argv) == 1:
        print(f"Output directory is required.")
        sys.exit(1)

    output_directory = sys.argv[1]

    create_groups.create_groups(output_directory)
    create_schemas.create_schemas(output_directory)

    verify(output_directory)


if __name__ == "__main__":
    main()
