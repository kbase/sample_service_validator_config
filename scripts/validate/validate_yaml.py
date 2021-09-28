from jsonschema import validate, RefResolver
import os
import json
import sys
import yaml

#
# validate_schemas.py
#
# validates source sample specs: templates, vocabularies, ordering.
#


def relative_path(path):
    return os.path.abspath(os.path.dirname(__file__) + "/" + path)


def validate_file(data_file, schema_dir, schema_file):
    schema_path = relative_path(f"../../schemas/{schema_dir}/{schema_file}")
    schema_root = relative_path(f"../../schemas/{schema_dir}")
    resolver = RefResolver(f"file://{schema_root}/", None)
    with open(data_file) as dataIn:
        _, ext = os.path.splitext(data_file)
        if ext == ".json":
            data = json.load(dataIn)
        elif ext == ".yaml" or ext == ".yml":
            data = yaml.safe_load(dataIn)
        else:
            raise Exception(f'Unsupported data file extension "{ext}"')
    with open(schema_path) as schema_in:
        schema = json.load(schema_in)
    try:
        validate(instance=data, schema=schema, resolver=resolver)
    except Exception as ex:
        print("!! Validation Error")
        print(str(ex))


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: <validate-schemas.py> all or <file-to-validate> <schema-dir> <schema-file-name>"
        )
        sys.exit(1)

    file_to_validate = sys.argv[1]
    schema_dir = sys.argv[2]
    schema_file = sys.argv[3]

    if os.path.isdir(file_to_validate):
        for file in os.listdir(file_to_validate):
            validate_file(f"{file_to_validate}/{file}", schema_dir, schema_file)
    else:
        validate_file(file_to_validate, schema_dir, schema_file)


if __name__ == "__main__":
    main()
