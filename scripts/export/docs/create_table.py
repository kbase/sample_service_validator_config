import sys
import yaml
import pandas as pd
import codecs
import uuid


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


def dict_to_table(value, style_id):
    html = f'<table class="Dict-{style_id}">'

    html += "<tbody>"
    for key, value in value.items():
        html += "<tr>"
        html += f"<th >{key}</th>"
        html += f"<td >{value}</td>"
        html += "</tr>"
    html += "</tbody></table>"

    return html


def create_table(input_file, style_id):
    with open(input_file) as f:
        metadata_validation = yaml.load(f, Loader=yaml.SafeLoader)

    table_columns = [
        {"key": "key", "label": "Field Key"},
        {"key": "label", "label": "Field Label"},
        {"key": "description", "label": "Description"},
        {"key": "examples", "label": "Example(s)"},
        {"key": "type", "label": "Type"},
        {"key": "unit", "label": "Unit"},
        {"key": "constraints", "label": "Constraints"},
    ]

    validators = metadata_validation["validators"]
    # f"<div style='margin-bottom: 4px; display: flex; flex-direction: row;'><div style='flex: 0 0 1em; color: gray;'>⦁</div><div style='1 1 0;'><code>{str(example)}</code></div></div>"
    rows = []
    for key, validator in validators.items():
        field_type = validator["key_metadata"].get("type", "string")
        examples = "".join(
            [
                f"<li><code>{str(example)}</code></li>"
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
                f'<ul class="Examples-{style_id}">{examples}</ul>',
                field_type,
                unit,
                dict_to_table(constraints, style_id),
            ]
        )

    table_head = ""
    for col in table_columns:
        table_head += f'<th>{col["label"]}</th>'

    table_body = ""
    for row in rows:
        table_body += "<tr>\n"
        for col in row:
            table_body += f"<td>{col}</td>\n"
        table_body == "</tr>\n"

    table_html = """
<table class="Validators-{style_id}">
    <thead>
        <tr>
            {table_head}
        </tr>
    </thead>
    <tbody>
    {table_body}
    </tbody>
</table>
"""
    return table_html.format(
        table_head=table_head, table_body=table_body, style_id=style_id
    )


def create_stylesheet(style_id):
    stylesheet = """
<style>
table.Validators-{style_id} {{
    width: 100%;
    font-size: 16px;
    font-family: Content-font, Roboto, sans-serif;
    font-weight: 400;
    line-height: 1.625;
    border-collapse: collapse;
}}
table.Validators-{style_id} > thead > tr {{
    border-bottom: 1px solid rgb(230, 236, 241);
}}
table.Validators-{style_id} > thead > tr > th,
table.Validators-{style_id} > tbody > tr > td {{
    margin: 0; 
    padding: 6px;
    border: 1px solid rgb(200, 200, 200);
    vertical-align: top;
}}

table.Validators-{style_id} > thead > tr > th {{
    font-weight: 700;
    color: rgb(157, 170, 182);
}}


table.Dict-{style_id} {{
    width: 100%;
    font-size: 14px;
    font-family: Content-font, Roboto, sans-serif;
    font-weight: 400;
    line-height: 1.625;
    border-collapse: collapse;
}}
table.Dict-{style_id} > thead > tr {{
    border-bottom: 1px solid rgb(230, 236, 241);
}}
table.Dict-{style_id} > tbody > tr > th,
table.Dict-{style_id} > tbody > tr > td {{
    margin: 0; 
    padding: 2px;
    vertical-align: top;
}}

table.Dict-{style_id} > tbody > tr > td {{
    font-family: monospace;
    white-space: pre;
}}

table.Dict-{style_id} > tbody > tr > th {{
    text-align: right; 
    font-style: italic; 
    font-weight: normal; 
    color: rgb(157, 170, 182);
}}

table.Dict-{style_id} > tbody > tr > th::after {{
    content: ":"
}}

ul.Examples-{style_id} {{
    list-style: none;
    margin: 0;
    padding: 0;
    margin: 0.5em;
}}

ul.Examples-{style_id} > li::before {{
    content: "\\2981";
    color: gray;
    display: inline-block;
    width: 0.5em;
    margin-right: 0.25em;
}}
</style>
"""
    return stylesheet.format(style_id=style_id)


def main():
    if len(sys.argv) != 3:
        print("Usage: create_table.py <file-to-transform> <output-directory>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    style_id = str(uuid.uuid4())

    html_table = create_table(input_file, style_id)
    table_stylesheet = create_stylesheet(style_id)

    html = f'<div class="">{table_stylesheet}{html_table}</div>'

    with codecs.open(f"{output_dir}/sample_fields.html", "w", "utf-8-sig") as f:
        f.write(html)

    print(f"    created table  {input_file} written to {output_dir}.")


if __name__ == "__main__":
    main()
