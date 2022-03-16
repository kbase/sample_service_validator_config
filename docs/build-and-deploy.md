# Build and Deploy Sample Specs

The Sample Specifications are maintained in an idiosyncratic YAML format. The YAML files are located in the `specs` directory:

- `vocabularies/*.yml` - define sample fields
- `sesar.tsv` - SESAR template field definitions
- `enigma.tsv` - ENIGMA template field definitions
- `templates/*.yml` - both template definition source and generated template
- `ordered.yml` - defines sample field grouping and ordering

These files are transformed into an additional set of files for usage by the Sample Service and Sample Uploader. The process of transforming the source specifications to generate an additional set of files for usage is the subject of this document.

From the set of files above, additional files are generated:

- `metadata_validation.yml` - field definitions
- `ontology_validators.yml` - ontology term field definitions extracted and transformed
- `sample_uploader_mappings.yml` - additional configuration for sample importing
- `templates/sesar_template.yml` - upload template for SESAR samples
- `templates/enigma_template.yml` - upload template for ENIGMA samples

These files are used by the [Sample Service](https://github.com/kbase/sample_service) and [Sample Uploader](https://github.com/kbaseapps/sample_uploader). The Sample Service uses `metadata_validation.yml` to validate individual sample fields. The Sample Uploader uses `metadata_validation.yml` to validate sample fields, `ontology_validators.yml` to validate ontology sample fields, and `sample_uploader_mappings.yml` `templates/*.yml` to construct and validate samples of type SESAR or ENIGMA.

Until those services are updated to use the new config distribution scheme (described below), they are also left in their "legacy" location. The legacy locations are require that the developer generate the files locally and commit them with their changes.

## Prerequisites

In order to build and test the specs, you just need `make`, `python`, and a `bash` compatible shell.

For editing the files, you will also need to have Python 3.7 available. A `requirements.txt` is available, and shared with the build image.

E.g. to set up a virtual environment suitable for development:

```bash
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Legacy Config Generation

The Sample Service and Sample Uploader currently expect to find configuration files in specific locations in the "master" branch of this repo. In this document, these are called "legacy" config files.

At some future time these services will be refactored to pick up the same files from a distribution branch, as is described in sections below.

The legacy configuration files are created locally by a developer after making changes to the sources, and then pushed up to the canonical repo along with the source changes, and ultimately made available by merging a Pull Request to the master branch.

In order to generate these files, issue the following command:

```bash
make
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
- `ontology_validators.yml` - KBase-formatted validation configuration for ontology fields (different format than in metadata_validation.yml)
- `templates/enigma_template.yml` - Metadata fields defined for the ENIGMA sample type, utilized by the importer
- `templates/sesar_template.yml` - Metadata fields defined for the SESAR sample type, utilized by the importer

Note that `metadata_validation.tsv` is generated, but does not appear to be used.

In addition, the file `samples_uploader_mappings.yml` is utilized by the sample uploader, but is maintained by hand.

### Consumption by Services

This section describes how services consume the legacy files.

#### Sample Service

The Sample Service fetches the `metadata_validation.yml` file directly from the master branch of this repo through the url `https://raw.githubusercontent.com/kbase/sample_service_validator_config/master/metadata_validation.yml`.

#### Sample Importer

Sample import is conducted by the `import_samples` method of the `sample_uploader` app. This app acquires the legacy validation and template configs by cloning this repo at a specific commit by hash reference.

## Generating Config Distribution

A new generation process has been designed to replace the legacy process described above. Rather than generate the configs and include them in the repo directly, they are generated in the GitHub repository through a GitHub Action workflow, `.github/build-dist.yml`. We refer to the set of generated files intended for external usage as the "distribution", or "dist" for short.

The generated files are made available in special distribution branches, which are either created or updated by the workflow itself. This process is described in more detail below.

You may generate the distribution locally.

The following command

```bash
make
```

will run a set of scripts via the container to build and validate the source files and then build the distribution. The "build" of the distribution consists of just copying the files to the `dist` directory.

> The `dist` directory is excluded from `git`, so you may generate them locally in order to inspect and validate them without worrying about affecting the repo.

## GitHub Action Workflow Process

The heart of the GitHub Action build workflow invokes the makefile as described above. In addition to the build and validation steps, it also takes care to capture the generated files for releases (including pre-releases.)


### Build and Validate

The "Sample Service Validator Config Distribution Builder" workflow, `.github/build-dist.yml`, is responsible for validating the source specs, creating the generated files, and validating the generated files.

The generation and validation of config files is conducted via the Makefile as a sequence of scripts. This workflow step is the same one utilized in the local build procedure described above.

#### Preparation Steps

The workflow first takes care of boilerplate operations, like cloning the repo.

#### Validation and Build Steps

Following the preparation steps is the validation and build step.

These steps carry out the following tasks:

- validate source spec files
- generate files for distribution into `dist`
- copies a special `README.md` into the `dist` directory
- archives the directory as `dist.zip`

#### Create release asset

After the `dist.zip` archive is created it is uploaded to the release. Since this workflow is only triggered by the publication of a release (including pre-releases), this is safe to do.

### GHA Token

The GHA workflow requires a token named `KBASE_BOT_TOKEN`. This token requires  `repo:public_repo` access.

- create a PAT or other token with `repo:public_repo` access
- create a secret named `KBASE_BOT_TOKEN` with the value set to the token
