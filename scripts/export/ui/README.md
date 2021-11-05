# README

This directory contains scripts to transform source validation specs into a form more suitable for consumption through
the sample service api. For example, by the kbase-ui sample and sample set landing pages, or the Narrative sample set
viewer.

All result files are in JSON format.

All scripts take an optional single argument, the destination directory, denoted as `DIR` below, which defaults
to `_temp` within the repo directory, a reasonable choice as it is included in `.gitignore`.

## `create_groups.py`

Transforms `/ordered.yml` to `DIR/groups.json`

## `create_schemas.py`

Transform files in `/vocabularies` to `schemas.json`. Since at the moment there are no links between the field
validation and description schemas, they are all stored in a single json file as an array of individual JSON-Schema
definitions. Previously they each field was stored in a separate file to enable cross-references, but that has not
materialized, so they were dropped. The single file is easier to consume.

## `export.py`

Combines transformations to create groups and schemas into one script, with verification.
