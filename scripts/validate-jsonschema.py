from jsonschema import validate, RefResolver
import os
import json
import sys
import yaml


def relative_path(path):
    return os.path.abspath(os.path.dirname(__file__) + '/' + path)


def validateFile(data_file, schema_file):
    # dataPath = relative_path(f'../_temp/{dataFile}')
    schema_path = relative_path(f'../schemas/{schema_file}')
    schema_dir = relative_path('../schemas')
    resolver = RefResolver(f'file://{schema_dir}/', None)
    with open(data_file) as dataIn:
        _, ext = os.path.splitext(data_file)
        if ext == '.json':
            data = json.load(dataIn)
        elif ext == '.yaml' or ext == '.yml':
            data = yaml.safe_load(dataIn)
        else:
            raise Exception(f'Unsupported data file extension "{ext}"')
    with open(schema_path) as schema_in:
        schema = json.load(schema_in)
    result = validate(instance=data, schema=schema, resolver=resolver)
    if result is not None:
        print('!! Validation Error')
        print(result)



def validateAll():
    for template_file in os.listdir('templates'):
        validateFile(f'templates/{template_file}', 'template.json')

    validateFile('ordered.yml', 'ordered.json')

    for vocabulary_file in os.listdir('vocabularies'):
        validateFile(f'vocabularies/{vocabulary_file}', 'vocabulary.json')


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == 'all':
            validateAll();
        else:
            print(
                "Usage: <validate-schemas.py> all or <file-to-validate> "
                "<schema-file-name>")
            print("...")
            sys.exit(1)

    elif len(sys.argv) != 3:
        print(
            "Usage: <validate-schemas.py> all or <file-to-validate> <schema-file-name>")
        print("...")
        sys.exit(1)
    else:
        file_to_validate = sys.argv[1]
        schema_file = sys.argv[2]

        # validateFile('_temp/schemas/elevation.json', 'schema-number.json')
        validateFile(file_to_validate, schema_file)
