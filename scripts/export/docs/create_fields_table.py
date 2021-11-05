import codecs
import json
import sys
import uuid

import yaml


def get_unit(validator_spec, default_value=""):
    if "validators" not in validator_spec:
        return default_value
    for validator in validator_spec["validators"]:
        if validator["callable_builder"] == "units":
            return validator["parameters"]["units"]
    return default_value


def get_number_constraints(validator_spec, default_value=None):
    if default_value is None:
        default_value = {}
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


def get_ontology_constraints(validator_spec, default_value=None):
    if default_value is None:
        default_value = {}
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
    html = ""
    for key, value in value.items():
        html += '<div class="Field">'
        html += f'<div class="Label">{key}</div>'
        html += f'<div class="Value">{value}</div>'
        html += "</div>"

    return html


def validator_to_row(key, validator, style_id):
    field_type = validator["key_metadata"].get("type", "string")
    examples = "".join(
        [
            f"<li><code>{str(example)}</code></li>"
            for example in validator["key_metadata"].get("examples", [])
        ]
    )
    unit = get_unit(validator, None)
    constraints = {}
    if field_type == "number":
        constraints = get_number_constraints(validator)
    elif field_type == "string":
        if validator["key_metadata"].get("format", None) == "ontology-term":
            unit = "ontology_term"
            constraints = get_ontology_constraints(validator)

    return [
        key,
        validator["key_metadata"]["title"],
        validator["key_metadata"]["description"],
        f'<ul class="Examples-{style_id}">{examples}</ul>',
        field_type,
        unit,
        dict_to_table(constraints),
    ]


def create_table(input_file, grouping_file, style_id):
    with open(input_file) as f:
        metadata_validation = yaml.load(f, Loader=yaml.SafeLoader)

    with open(grouping_file) as f:
        grouping = json.load(f)

    validators = metadata_validation["validators"]

    grouped_rows = []
    for group in grouping:
        rows = []
        for field_key in group["fields"]:
            validator = validators[field_key]
            row = validator_to_row(field_key, validator, style_id)
            rows.append(row)
        grouped_rows.append({"group": group, "rows": rows})

    table_body = ""
    for group in grouped_rows:
        table_body += f'<div class="-titleRow">{group["group"]["title"]}</div>\n'
        table_body += """
<div class="-rowGroup">
    <div class="-headerRow ">
        <div class="-dataCol -title">
            Field name
        </div>
        <div class="-dataCol -desc">
            Description
        </div>
        <div class="-dataCol -type">
            Type 
        </div>
    </div>
"""

        for [key, title, description, examples, field_type, unit, constraints] in group[
            "rows"
        ]:
            unit_field = ""
            if unit is not None:
                unit_field = """
        <div class="Field">
            <div class="Label">unit</div>
            <div class="Value">{unit}</div>
        </div>
""".format(
                    unit=unit
                )

            table_body += """
    <div class="-dataRow">
        <div class="-dataCol -title">
            <div class="-titleCol">{title}</div>
            <div class="-fieldKeyCol">{key}</div>
        </div>
        <div class="-dataCol -desc">
            <div>{description}</div>
            <div style="font-size: 90%; color: rgb(157, 170, 182);">examples</div>
            <div>{examples}</div>
        </div>
        <div class="-dataCol -type">
            <div>{field_type}</div>
            {unit_field}
            <div>{constraints}</div>
        </div>
    </div>
""".format(
                key=key,
                title=title,
                description=description,
                examples=examples,
                field_type=field_type,
                unit_field=unit_field,
                constraints=constraints,
            )
        table_body += "</div>"

    return """
<div class="Validators-{style_id}">
    <div class="-body">
    {table_body}
    </div>
</div>
""".format(
        table_body=table_body, style_id=style_id
    )


def create_stylesheet(style_id):
    stylesheet = """
<style>
div.Validators-{style_id} {{
    width: 100%;
    font-size: 16px;
    font-family: Content-font, Roboto, sans-serif;
    font-weight: 400;
    line-height: 1.625;
    border-collapse: collapse;
    display: flex;
    flex-direction: column;
}}

div.Validators-{style_id} .-rowGroup {{
    border: 1px solid silver;
    border-radius: 8px;
    padding: 8px;
}}
div.Validators-{style_id} .-titleRow {{
    flex: 0 0 auto;
    display: flex;
    flex-direction: row;
    font-size: 150%;
    font-weight: bold;
    color: rgb(157, 170, 182);
    margin-top: 20px;
}}

div.Validators-{style_id} .-headerRow {{
    border-bottom: 1px solid rgb(230, 236, 241);
    flex: 0 0 auto;
    display: flex;
    flex-direction: row;
    font-weight: bold;
    color: rgb(157, 170, 182);
}}

div.Validators-{style_id} .-dataRow {{
    border-bottom: 1px solid rgb(230, 236, 241);
    flex: 0 0 auto;
    display: flex;
    flex-direction: row;
    padding: 10px 0;
}}


div.Validators-{style_id} .-dataRow:nth-last-child(1) {{
    border-bottom: none;
}}

div.Validators-{style_id} .-dataRow:hover {{
    background-color: rgba(230, 236, 241, 0.5);
}}

div.Validators-{style_id} .-dataCol {{
    flex: 1 1 0;
    display: flex;
    flex-direction: column;
}}

div.Validators-{style_id} .-dataCol + .-dataCol {{
    margin-left: 0.25em;
}}


div.Validators-{style_id} .-dataCol:nth-child(1) {{
    flex: 2 1 0;
}}

div.Validators-{style_id} .-dataCol:nth-child(2) {{
    flex: 3 1 0;
}}

div.Validators-{style_id} .-dataCol:nth-child(3) {{
    flex: 1 1 0;
}}

/* individual fields */
div.Validators-{style_id} .-dataCol .-titleCol  {{
    font-weight: bold;
}}

div.Validators-{style_id} .-dataCol .-fieldKeyCol  {{
    font-family: monospace;
    white-space: pre;
    font-size: 90%;
}}

div.Validators-{style_id} .Field {{
    flex: 0 0 auto;
    display: flex; 
    flex-direction: row;
    font-size: 80%;
}}

div.Validators-{style_id} .Label {{
    color: rgb(157, 170, 182);
    margin-right: 0.5em;
}}

div.Validators-{style_id} .Value {{
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
    font-size: 90%;
    list-style: none;
    margin: 0;
    padding: 0;
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


def build_page(content):
    return """<!DOCTYPE html>
<html>
<head>
    <title>KBase Sample Metadata Fields</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="og:description" content="An up-to-date catalog of all KBase Sample Metadata fields, including their descriptions, types, and constraints." />
    <meta name="og:title" content="KBase Sample Metadata Fields" />
    <meta name="og:type" content="website" />
    <meta name="og:url" content="https://github.com/kbase/sample_service_validator_config" />
    <meta name="og:site_name" content="KBase" />
</head>
<body>
{content}
</body>
</html>
""".format(
        content=content
    )


def main():
    if len(sys.argv) != 4:
        print("Usage: create_table.py <input-file> <groupings-file> <output-directory>")
        sys.exit(1)

    input_file = sys.argv[1]
    grouping_file = sys.argv[2]
    output_dir = sys.argv[3]

    style_id = str(uuid.uuid4())

    html_table = create_table(input_file, grouping_file, style_id)
    table_stylesheet = create_stylesheet(style_id)

    html = f"{table_stylesheet}{html_table}"

    with codecs.open(f"{output_dir}/sample_fields.html", "w", "utf-8-sig") as f:
        f.write(build_page(html))

    print(f"    created table  {input_file} written to {output_dir}.")


if __name__ == "__main__":
    main()
