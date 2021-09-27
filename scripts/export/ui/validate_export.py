import sys
import yaml
from jsonschema import validate

#
# validate_export.py
#
# General purpose script to validate some yaml file against a jsonschema file.
# However, only used for exported yaml files.
# See validate_source_specs.py for validation of the source sample specs.
#


def main():
    if len(sys.argv) < 3:
        raise RuntimeError(f"Usage: validate_export.py <schema file> [<yaml files>]")
    json_schema_file = sys.argv[1]

    with open(json_schema_file) as f:
        _META_VAL_JSONSCHEMA = yaml.safe_load(f)

    for file in sys.argv[2:]:
        with open(file) as f:
            cfg = yaml.safe_load(f)
        validate(instance=cfg, schema=_META_VAL_JSONSCHEMA)


if __name__ == "__main__":
    main()
