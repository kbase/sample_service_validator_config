from jsonschema import validate, RefResolver
import os
import json
import sys


def relative_path(path):
    return os.path.abspath(os.path.dirname(__file__) + '/' + path)


def validateFile(dataFile, schemaFile):
    # dataPath = relative_path(f'../_temp/{dataFile}')
    schema_path = relative_path(f'schemas/{schemaFile}')
    schema_dir = relative_path('schemas')
    resolver = RefResolver(f'file://{schema_dir}/', None)
    with open(dataFile) as dataIn:
        data = json.load(dataIn)
    with open(schema_path) as schema_in:
        schema = json.load(schema_in)
    validate(instance=data, schema=schema, resolver=resolver)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: <validate-schemas.py> <file-to-validate> <schema-file-name>")
        print("...")
        sys.exit(1)

    file_to_validate = sys.argv[1]
    schema_file = sys.argv[2]

    validateFile(file_to_validate, schema_file)
