import os
import yaml
import sys
from pint import UnitRegistry
from pint import DimensionalityError
from pint import UndefinedUnitError
from pint import DefinitionSyntaxError


def relative_path(path):
    return os.path.abspath(os.path.dirname(__file__) + "/" + path)


def validate_unit(unit, unit_registry):
    try:
        unit_registry.parse_expression(unit)
    except UndefinedUnitError as e:
        raise ValueError(f"unable to parse units '{unit}': undefined unit: {e.args[0]}")
    except DefinitionSyntaxError as e:
        raise ValueError(f"unable to parse units '{unit}': syntax error: {e.args[0]}")


def validate_vocabulary_units(vocabulary_file, definitions_file):
    unit_registry = UnitRegistry()
    unit_registry.load_definitions(definitions_file)
    failures = 0
    with open(vocabulary_file) as dataIn:
        vocabulary = yaml.safe_load(dataIn)
    for key, term in vocabulary["terms"].items():
        if "units" in term:
            try:
                validate_unit(term["units"], unit_registry)
            except Exception as e:
                failures += 1
                print(f"Unit validation failed for {term['units']}")
                print(f"  in term {key}: {term['title']}")
                print(f"  in file {vocabulary_file}")

    if failures > 0:
        print(f"{failures} fields failed unit validation")
        return False
    return True


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: validate_units.py <DIRECTORY> <PINT_DEFINITIONS>"
            "to validate units in all vocabularies in the given directory"
        )
        sys.exit(1)

    vocabulary_directory_or_file = sys.argv[1]
    pint_definitions = sys.argv[2]

    failed = False

    if os.path.isdir(vocabulary_directory_or_file):
        for file in os.listdir(vocabulary_directory_or_file):
            if not validate_vocabulary_units(
                f"{vocabulary_directory_or_file}/{file}", pint_definitions
            ):
                failed = True
    else:
        if not validate_vocabulary_units(
            vocabulary_directory_or_file, pint_definitions
        ):
            failed = True

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
