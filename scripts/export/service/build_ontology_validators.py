import os
import sys
from copy import deepcopy

import yaml

# TODO: We should not need to know the Arangodb collection, should we??
NAMESPACE_TO_COLLECTION = {"envo_ontology": "ENVO_terms", "go_ontology": "GO_terms"}


def extract_ontology_callable_builder(validator_def):
    for validator in validator_def["validators"]:
        if validator["callable_builder"] == "ontology_has_ancestor":
            return "ontology_has_ancestor"
    raise ValueError(
        f"Only 'ontology_has_ancestor' callable builder supported, is {validator['callable_builder']}"
    )


def build_validator_file(source_file, output_file):
    "Pick out ontology field definitions from the source file, transform, and save to output file in yaml format"
    with open(source_file) as f_in:
        data = yaml.load(f_in, Loader=yaml.SafeLoader)

    ontology_validators = {}
    # Note the odd format, surely a mistake in the original implementation;
    # see schemas/legacy/ontology-validators.json
    for key, validator in data["validators"].items():
        if validator["key_metadata"].get("format") != "ontology-term":
            continue

        ontology_validators[key] = [
            {
                "ancestor_term": validator["key_metadata"]["ancestorTerm"],
                "display_name": validator["key_metadata"]["title"],
                "ontology": validator["key_metadata"]["namespace"],
                "ontology_collection": NAMESPACE_TO_COLLECTION[
                    validator["key_metadata"]["namespace"]
                ],
                "validator_type": extract_ontology_callable_builder(validator),
            }
        ]
    with open(output_file, "w") as f_out:
        yaml.dump(ontology_validators, f_out)


def main():
    # assert correct number of arguments.
    if len(sys.argv) < 2:
        raise RuntimeError(
            "Please provide the input file as the first argument to build_ontology_validators.py"
        )
    if len(sys.argv) < 3:
        raise RuntimeError(
            "Please provide the output file as the second argument to build_ontology_validators.py"
        )
    if len(sys.argv) > 3:
        raise RuntimeError("Too many arguments for build_ontology_validators.py")

    # get input files
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not output_file.endswith(".yml") and not output_file.endswith(".yaml"):
        output_file = output_file + ".yml"

    build_validator_file(input_file, output_file)


if __name__ == "__main__":
    main()
