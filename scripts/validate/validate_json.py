import json
import os
import sys

from jsonschema import validate, RefResolver


def relative_path(path):
    return os.path.abspath(os.path.dirname(__file__) + "/" + path)


def validate_file(data_file, schema_dir, schema_file):
    # dataPath = relative_path(f'../_temp/{dataFile}')
    schema_path = relative_path(f"../../schemas/{schema_dir}/{schema_file}")
    schema_root = relative_path(f"../../schemas/{schema_dir}")
    resolver = RefResolver(f"file://{schema_root}/", None)
    with open(data_file) as dataIn:
        data = json.load(dataIn)
    with open(schema_path) as schema_in:
        schema = json.load(schema_in)
    validate(instance=data, schema=schema, resolver=resolver)


def main():
    if len(sys.argv) != 4:
        print("Usage: validate.py <file-to-validate> <schema-dir> <schema-file-name>")
        sys.exit(1)

    file_to_validate = sys.argv[1]
    schema_dir = sys.argv[2]
    schema_file = sys.argv[3]

    validate_file(file_to_validate, schema_dir, schema_file)


if __name__ == "__main__":
    main()
