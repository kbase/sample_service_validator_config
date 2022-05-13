# Build and Deploy Sample Specs

The Sample Specifications are maintained in an idiosyncratic YAML format. The YAML files are located in the `specs` directory:

- `specs/vocabularies/*.yml` - define sample fields
- `specs/templates/*.yml` - define upload templates
- `specs/ordered.yml` - defines sample field grouping and ordering

These files are transformed into an additional set of files for usage by the Sample Service, Sample Uploader, and sample user interfaces. The process of transforming the source specifications to generate an additional set of files for usage is the subject of this document.

There are two sets of generated files.

One set is composed of yaml files in a proprietary format:

- `metadata_validation.yml` - field definitions
- `ontology_validators.yml` - ontology term field definitions extracted and transformed
- `sample_uploader_mappings.yml` - additional configuration for sample importing
- `templates/sesar_template.yml` - upload template for SESAR samples
- `templates/enigma_template.yml` - upload template for ENIGMA samples

These files are used by the [Sample Service](https://github.com/kbase/sample_service) and [Sample Uploader](https://github.com/kbaseapps/sample_uploader). The Sample Service uses `metadata_validation.yml` to validate individual sample fields. The Sample Uploader uses `metadata_validation.yml` to validate sample fields, `ontology_validators.yml` to validate ontology sample fields, and the templates to validate sample sets of type SESAR or ENIGMA.

In addition `metadata_validation.tsv` is generated but does not appear to be used.

Until those services are updated to use the new config distribution scheme (described below), they will also be left in their "legacy" location in the root of the rpo. The legacy locations require that the developer generate the files locally and then commit them. This is because the Sample Service and Sample Uploader fetch these files directly from the master branch at GitHub.

The second set of generated config files are in JSON format.

- `schemas.json` - field definitions provided as an array of JSON-Schema specs, one per field
- `groups.json` - field grouping and ordering, covering all fields defined in `schemas.json`.

These files are utilized by user interfaces, including the Sample Landing Page, Sample Set Landing Page, and the Narrative Sample Set Viewer.

## Prerequisites

In order to build and test the specs, you just need `make`, `docker`, and a `bash` compatible shell.

For editing the files, you will also need to have Python 3.7 available. A `requirements.txt` is available, and shared with the build image, and `requirements-dev.txt` provides additional developer support.

E.g. to set up a virtual environment suitable for development:

```bash
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
```

## Legacy Config Generation

The Sample Service and Sample Uploader currently expect to find configuration files in specific locations in the "master" branch of this repo. In this document, these are called "legacy" config files.

At some future time these services will be refactored to pick up the same files from a release, as is described in sections below.

The legacy configuration files are created locally by a developer after making changes to the sources, and then pushed up to the canonical repo along with the source changes, and ultimately made available by merging a Pull Request to the master branch.

In order to generate these files, issue the following command:

```bash
make legacy-files
```

This will result in the following files being created or replaced:

```text
├── metadata_validation.yml
├── metadata_validation.tsv
├── ontology_validators.yml
└── templates
    ├── enigma_template.yml
    └── sesar_template.yml
```

- `metadata_validation.yml` - KBase-formatted validation configuration for each defined metadata field
- `metadata_validation.tsv` - Alternative format of the above; usage unknown
- `ontology_validators.yml` - KBase-formatted validation configuration for ontology fields (different format than in metadata_validation.yml)
- `templates/enigma_template.yml` - Metadata fields defined for the ENIGMA sample type, utilized by the importer
- `templates/sesar_template.yml` - Metadata fields defined for the SESAR sample type, utilized by the importer

### Consumption by Services

This section describes how services consume the legacy files.

#### Sample Service

The Sample Service fetches the `metadata_validation.yml` file directly from the master branch of this repo through the url `https://raw.githubusercontent.com/kbase/sample_service_validator_config/master/metadata_validation.yml`.

#### Sample Importer

Sample import is conducted by the `import_samples` method of the `sample_uploader` app. This app acquires the legacy validation and template configs by cloning this repo at a specific commit by hash reference.

## Generating Config Distribution

A new process has been designed to replace the legacy process described above. Rather than generate the configs and include them in the repo directly, they are generated in the GitHub repository through a GitHub Action workflow, `.github/release.yml`. We refer to the set of generated files intended for external usage as the "distribution", or "dist" for short.

The generated files are made available as an asset in a GitHub release. 

You may also generate the distribution locally with just Docker.

The following command

```bash
make
```

will build a Docker image with Python and all dependencies installed, and then proceed to run a set of scripts via the container to validate the source files, build the generated files, validate the generated files, and create the distribution.

> The `dist` directory is excluded from `git`, so you may generate them locally in order to inspect and validate them without worrying about affecting the repo.

 If you peek into the Makefile, you'll see that each step actually runs one or more shell scripts. The default entry point for the image is `bash`, and the command is expected to be a script. All the scripts run within the workflow are located in `scripts/automation`.

Each automation shell script in turn calls a Python script to conduct the actual work. These scripts are located in `scripts/export` and `scripts/validate`. This double-step process is used because each Python script expects certain parameters. This facilitates re-usage and testability. It also insulates the build process from the details of script execution, other than the very simple shell scripts.

After running `make`, you should see a `dist` directory, with the following contents:

```bash
% tree dist
dist
├── README.md
├── groups.json
├── manifest.json
├── metadata_validation.yml
├── ontology_validators.yml
├── pint_unit_definitions.txt
├── sample_fields.html
├── sample_uploader_mappings.yml
├── schemas.json
└── templates
    ├── enigma_template.yml
    └── sesar_template.yml

1 directory, 11 files
```

Let's itemize those files

- `README.me` - short doc describing the directory
- `groups.json` - field grouping and ordering, covering all fields defined in `schemas.json`.
- `manifest.json` - information about the distribution build
- `metadata_validation.yml` - field definitions for services
- `ontology_validators.yml` - subset of metadata_validation.yml utilized by the sample_uploader app 
- `pint_unit_definitions.txt` - custom unit definitions
- `sample_fields.html` - a report of all sample fields, grouped and ordered, copied into docs.kbase.us
- `sample_uploader_mappings.yml` - manually curated file used by the sample_uploader app
- `schemas.json` - field definitions provided as an array of JSON-Schema specs, one per field, for user interfaces
- `templates` - upload templates
  - `sesar_template.yml` - upload template for SESAR samples
  - `enigma_template.yml` - upload template for ENIGMA samples

## GitHub Action Workflow Process

The heart of the GitHub Action build workflow invokes the makefile as described above. In addition to the build and validation steps, it also archives the distribution and attaches it to a GitHub release.

### Build and Validate

The GitHub Action workflow, `.github/pull_request.yml`, triggered by a pull request open, reopen, or synchronize. It will validate the source specs, create the generated files, and validate the generated files. This, together with branch protection for the `master` branch, ensures that the specs are correct before a PR can be merged.

The generation and validation of config files is conducted via the Makefile as a sequence of scripts run inside a docker container. This workflow step is the same one utilized in the local build procedure described above.

#### Preparation Steps

The workflow first takes care of boilerplate operations, like cloning the repo and preparing some environment variables.

The final preparation step is to create the script-runner image, which is tagged `cli`, since it is used for running commands.

#### Validation and Build Steps

Following the preparation steps is the validation and build step. The repo directory (i.e. in the GHA runner itself) is volume mounted into the container at `/kb/module`. This allows the files generated within the container to be available in the GHA host for later steps.

These steps carry out the following tasks:

- validate source spec files
- generate files for distribution into `dist`
- validate generated files 
- copies generated and other files into `dist` directory if they were not generated there 
- creates a special `manifest.json` file in `dist`, containing information about the build itself

#### Publish a release

When a release is created, the workflow `release.yml` is triggered. This workflow generates the files and builds the distribution as described above, and also makes the distribution available in the release.

This is conducted by:
- archiving the distribution found in the `dist` directory into a single zip file `dist.zip`
- uploads `dist.zip` to the release assets

### GHA Token

The GHA workflow requires a token named `KBASE_BOT_TOKEN`. This token requires just `repo:public_repo` access.

- create a PAT or other token with `repo:public_repo` access
- create a secret named `KBASE_BOT_TOKEN` with the value set to the token
