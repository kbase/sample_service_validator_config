import sys
import yaml
import pandas as pd
import codecs


def get_unit(validator_spec, default_value=""):
    if "validators" not in validator_spec:
        return default_value
    for validator in validator_spec["validators"]:
        if validator["callable_builder"] == "units":
            return validator["parameters"]["units"]
    return default_value


def get_number_constraints(validator_spec, default_value={}):
    if "validators" not in validator_spec:
        return default_value
    for validator in validator_spec["validators"]:
        if validator["callable_builder"] == "number":
            constraints = {}
            for key in ["gte", "lte"]:
                if key in validator["parameters"]:
                    constraints[key] = validator["parameters"][key]

            return constraints
    return default_value


def get_ontology_constraints(validator_spec, default_value={}):
    if "validators" not in validator_spec:
        return default_value
    for validator in validator_spec["validators"]:
        if validator["callable_builder"] == "ontology_has_ancestor":
            return {
                "ancestor_term": validator["parameters"]["ancestor_term"],
                "ontology": validator["parameters"]["ontology"],
            }
    return default_value


def dict_to_table(value):
    table_style = "width: 100%;"
    th_style = (
        "text-align: left; font-style: italic; font-weight: normal; padding: 2px;"
    )
    td_style = "margin: 0; padding: 2px;  "
    html = f'<table cellspacing="0" style="{table_style}">'

    html += "<tbody>"
    for key, value in value.items():
        html += "<tr>"
        html += f'<th style="{th_style}">{key}</th>'
        html += f'<td style="{td_style}">{value}</td>'
        html += "</tr>"
    html += "</tbody></table>"

    return html


def main():
    if len(sys.argv) != 3:
        print("Usage: create_table.py <file-to-transform> <output-directory>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    with open(input_file) as f:
        metadata_validation = yaml.load(f, Loader=yaml.SafeLoader)

    table_columns = [
        {"key": "key", "label": "Sample Key"},
        {"key": "label", "label": "Label"},
        {"key": "description", "label": "Description"},
        {"key": "examples", "label": "Example(s)"},
        {"key": "type", "label": "Type"},
        {"key": "unit", "label": "Unit"},
        {"key": "constraints", "label": "Constraints"},
    ]

    validators = metadata_validation["validators"]
    rows = []
    for key, validator in validators.items():
        field_type = validator["key_metadata"].get("type", "string")
        examples = "".join(
            [
                f"<div style='margin-bottom: 4px; display: flex; flex-direction: row;'><div style='flex: 0 0 1em; color: gray;'>⦁</div><div style='1 1 0;'><code>{str(example)}</code></div></div>"
                for example in validator["key_metadata"].get("examples", [])
            ]
        )
        unit = get_unit(validator)
        constraints = {}
        if field_type == "number":
            constraints = get_number_constraints(validator)
        elif field_type == "string":
            if validator["key_metadata"].get("format", None) == "ontology-term":
                unit = "ontology_term"
                constraints = get_ontology_constraints(validator)

        rows.append(
            [
                key,
                validator["key_metadata"]["title"],
                validator["key_metadata"]["description"],
                f"<div>{examples}</div>",
                field_type,
                unit,
                dict_to_table(constraints),
            ]
        )

    # Generate an html table the cheesy way:
    # table_style = ""
    th_style = "margin: 0; padding: 4px; border: 1px solid rgba(200, 200, 200, 1); "
    td_style = "margin: 0; padding: 4px; border: 1px solid rgba(200, 200, 200, 1); "

    html = '<table cellspacing="0">'

    html += "<thead>"

    for col in table_columns:
        html += f'<th style="{th_style}">{col["label"]}</th>'
    html += "</thead>"

    html += "<tbody>"
    for row in rows:
        html += "<tr>"
        for col in row:
            html += f'<td style="{td_style}">{col}</td>'
    html += "</tbody></table>"

    with codecs.open(f"{output_dir}/sample_fields.html", "w", "utf-8-sig") as f:
        f.write(html)

    print(f"    created table  {input_file} written to {output_dir}.")


if __name__ == "__main__":
    main()
