import sys
import yaml
from jsonschema import validate


if len(sys.argv) < 3:
    raise RuntimeError(f'Usage: validate_schema.py <schema file> [<yaml files>]')
json_schema_file = sys.argv[1]

with open(json_schema_file) as f:
    _META_VAL_JSONSCHEMA = yaml.safe_load(f)


for file in sys.argv[2:]:
    with open(file) as f:
        cfg = yaml.safe_load(f)
    validate(instance=cfg, schema=_META_VAL_JSONSCHEMA)
