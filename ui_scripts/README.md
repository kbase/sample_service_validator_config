# README

This directory contains scripts to transform validation specs into a form more suitable for consumption through the sample service api. For example, by the kbase-ui sample and sample set landing pages, or the Narrative sample set viewer.

All result files are in JSON format.

All scripts take an optional single argument, the destination directory, denoted as `DIR` below, which defaults to `_temp` within the repo directory, a reasonable choice as it is included in `.gitignore`.

## `create-groups.py`

Transforms `/ordered.yml` to `DIR/groups.json`

## `create-jsonschema.py`

Transform files in `/vocabularies` to `DIR/schemas/*.json`, where each file in `DIR/schemas` is a JSONSchema file, and `DIR/schemas.json` which contains an array of all the schemas.

The latter is useful for front end code which currently needs to mock the sample service api to provide the schemas. (Simply put, loading a single json file into source is easier; the sample service would be expected to load and cache each schema as they are encountered)

## `export.py`

Combines transformations to create groups and schemas into one script.

## `verify.py`

Requires the above transformations to have already been conducted.

This script applies schemas found in `schemas` to the generated schemas. This ensures proper structure of the resulting output

## Adding apiKey

When requesting samples via the search interface, under certain conditions (large # of samples), the sample CSVs use snake-cased identifiers for columns rather than the usual human-friend labels. This necessitated adding the apiKey for the SESAR template, which provides the spreadsheet to sample key mapping.

Not all fields can be discovered this way.

There is an xml schema https://app.geosamples.org/4.0/sample.xsd which provides the equivalent information.

https://app.geosamples.org/4.0/sample.xsd