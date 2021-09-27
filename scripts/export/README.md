# Sample Specifications Distribution

This directory contains the distributable files for sample specifications.

## Contents:

### Used by Sample Service, Sample Uploader

These files are used by the Sample Service and/or Sample Uploader to validate samples.

- `metadata_validation.yml`: Validators for all sample fields; utilized by the Sample Service and Sample Uploader
- `metadata_validation.tsv`: ???
- `ontology_validators.tsv`: A subset of metadata validators for fields which hold KBase ontology terms.
- `templates`: Predefined sets of fields used by the Sample Uploader to interpret a set of samples in a spreadsheet given a sample format identifier (`SESAR` or `ENIGMA`).
        - `enigma_template.yml`
        - `sesar_template.yml`

### Used by UIs, via Sample Service

These files are essentially passed-through by the Sample Service to user interfaces.

- `groups.json`: A reformatting of the source `order.yml`, which arranges all sample fields within groups; ordering is provided by group order, and within groups, field order. Used by front end code to display sample fields in a consistent grouping and ordering.
- `schemas.json`: Contains all fields, with validation specification recast as JSONSchema; each field schema is standalone.