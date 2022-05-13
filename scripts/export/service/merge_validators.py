import os
import sys
from copy import deepcopy

import yaml

_BUILTIN = "SampleService.core.validator.builtin"
_NOOP = [{"callable_builder": "noop", "module": _BUILTIN}]

VOCABULARY_DIR = "specs/vocabularies"


def expand_validators(val):
    nv = []
    if "type" not in val:
        print("type required for validator")
        print(val)
        raise ValueError("Missing type")
    typ = val["type"]
    field_format = val.get("format")
    if "units" in val:
        v = {
            "callable_builder": "units",
            "module": _BUILTIN,
            "parameters": {"key": "units", "units": val["units"]},
        }
        nv.append(v)
    v = {
        "callable_builder": typ,
        "module": _BUILTIN,
    }
    if typ == "number":
        v["parameters"] = {"keys": "value"}
        if "maximum" in val:
            v["parameters"]["lte"] = val["maximum"]
        if "minimum" in val:
            v["parameters"]["gte"] = val["minimum"]
        if "required" in val:
            v["parameters"]["required"] = val["required"]
    elif "enum" in val:
        v["callable_builder"] = "enum"
        v["parameters"] = {"allowed-values": deepcopy(val["enum"])}
    elif "max-len" in val:
        v["parameters"] = {"max-len": val["max-len"]}
    elif typ == "string":
        if field_format == "ontology-term":
            v["callable_builder"] = "ontology_has_ancestor"
            v["parameters"] = {
                "ontology": val["namespace"],
                "ancestor_term": val["ancestorTerm"],
            }
        else:
            return deepcopy(_NOOP)
    else:
        print("type not recognized %s" % typ)
        raise KeyError("type %s not recognized" % typ)
    nv.append(v)
    return nv


def merge_to_existing_validators(val_type, val_data, key, val, data):
    if val_data.get(key):
        # update auxiliary fields and not the 'validators'
        for data_field in ["static_mappings", "key_metadata"]:
            if data[val_type][key].get(data_field):
                if val_data[key].get(data_field):
                    for sub_key, sub_val in data[val_type][key][data_field].items():
                        val_data[key][data_field][sub_key] = sub_val
                else:
                    val_data[key][data_field] = data[val_type][key][data_field]
    else:
        nv = {"key_metadata": {}, "validators": expand_validators(val)}
        for k in val:
            nv["key_metadata"][k] = val[k]

        val_data[key] = deepcopy(nv)
    return val_data


def merge_validation_files(files, output_file):
    validators = {}
    prefix_validators = {}

    for f in files:
        with open(f) as f_in:
            data = yaml.load(f_in, Loader=yaml.SafeLoader)
        prefix = ""
        if "namespace" in data:
            prefix = data["namespace"] + ":"
        for val_type, val_data in [("terms", validators)]:
            if data.get(val_type):
                for key, val in data[val_type].items():
                    keyname = prefix + key
                    val_data = merge_to_existing_validators(
                        val_type, val_data, keyname, val, data
                    )

    data = {}
    if validators:
        data["validators"] = validators
    if prefix_validators:
        data["prefix_validators"] = prefix_validators

    with open(output_file, "w") as f_out:
        yaml.dump(data, f_out)


def main():
    # assert correct number of arguments.
    if len(sys.argv) < 2:
        raise RuntimeError(
            "Please provide the output file as an argument to merge_validators.py"
        )
    if len(sys.argv) > 2:
        raise RuntimeError("Too many arguments for merge_validators.py")

    # get input files
    output_file = sys.argv[1]

    if not output_file.endswith(".yml") and not output_file.endswith(".yaml"):
        output_file = output_file + ".yml"

    files = os.listdir(VOCABULARY_DIR)
    files = [f"{VOCABULARY_DIR}/{f}" for f in files]
    merge_validation_files(files, output_file)


if __name__ == "__main__":
    main()
