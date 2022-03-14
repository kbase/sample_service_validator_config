# Sample Specifications Distribution

This directory contains the distributable files for sample specifications used for validation, description, and presentation.

## Contents

### Used by Sample Service, Sample Uploader

These files are used by the Sample Service and Sample Uploader to validate samples.

- `metadata_validation.yml`: Validators for all sample fields; utilized by the Sample Service and Sample Uploader.
- `ontology_validators.tsv`: Subset of validators for ontology term sample fields; used by the sample uploader.
- `sample_uploader_mappings.yml`: Used by sample uploader
- `templates`: Predefined sets of fields used by the Sample Uploader to interpret a set of samples in a spreadsheet given a sample format identifier (`SESAR` or `ENIGMA`).
        - `enigma_template.yml`
        - `sesar_template.yml`
