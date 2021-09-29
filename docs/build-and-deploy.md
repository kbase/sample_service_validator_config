# Build and Deploy Sample Specs

The Sample Specifications are maintained in an internal YAML format, located in files stored in the `specs` directory.

- `specs/vocabularies/*.yml` - define sample fields
- `specs/templates/*.yml` - define upload templates
- `specs/ordered.yml` - defines sample field grouping and ordering

For historical reasons, these files are transformed into an additional set of files for usage by the Sample Service, Sample Uploader, and sample user interfaces. The process of transforming the source specifications to generate an additional set of files for usage is the subject of this document.

There are actually two sets of generated files. The original set is composed of yaml files in a proprietary format:

- `metadata_validation.yml` - field definitions
- `templates/sesar.yml` - upload template for SESAR samples
- `templates/enigma.yml` - upload template for ENIGMA samples

These files are used by the Sample Service and Sample Uploader. The Sample Service uses `metadata_validation.yml` to validate individual sample fields. The Sample Uploader uses `metadata_validation.yml` to validate sample fields, and the templates to validate sample sets of type SESAR or ENIGMA.

The second set are composed of JSON files, one of which is in JSON-Schema format.

- `schemas.json` - field definitions provided as an array of JSON-Schema specs, one per field
- `groups.json` - field grouping and ordering, covering all fields defined in `schemas.json`.

These files are utilized by user interfaces, including the Sample Landing Page, Sample Set Landing Page, and the Sample Set Viewer.

## Generating

You won't find the generated files in the repo. In a previous iteration, the generated files were created locally by a developer after making changes to the sources, and then pushed up to the canonical repo. They would eventually be made available by creating a release at GitHub, and the resulting generated files fetched directly from the repo (master branch? actual release?)

