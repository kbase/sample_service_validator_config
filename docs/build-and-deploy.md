# Build and Deploy Sample Specs

The Sample Specifications are maintained in an idiosyncratic YAML format. The YAML files are located in the `specs` directory:

- `specs/vocabularies/*.yml` - define sample fields
- `specs/templates/*.yml` - define upload templates
- `specs/ordered.yml` - defines sample field grouping and ordering

These files are transformed into an additional set of files for usage by the Sample Service, Sample Uploader, and sample user interfaces. The process of transforming the source specifications to generate an additional set of files for usage is the subject of this document.

There are two sets of generated files.

One set is composed of yaml files in a proprietary format:

- `metadata_validation.yml` - field definitions
- `templates/sesar_template.yml` - upload template for SESAR samples
- `templates/enigma_template.yml` - upload template for ENIGMA samples

These files are used by the [Sample Service](https://github.com/kbase/sample_service) and [Sample Uploader](https://github.com/kbaseapps/sample_uploader). The Sample Service uses `metadata_validation.yml` to validate individual sample fields. The Sample Uploader uses `metadata_validation.yml` to validate sample fields, and the templates to validate sample sets of type SESAR or ENIGMA.

Until those services are updated to use the new config distribution scheme (described below), they are also generated in their "legacy" location, which is conducted by the individual developer locally, and included directly as part of the repo.

The second set are composed of JSON files, one of which is in JSON-Schema format.

- `schemas.json` - field definitions provided as an array of JSON-Schema specs, one per field
- `groups.json` - field grouping and ordering, covering all fields defined in `schemas.json`.

These files are utilized by user interfaces, including the Sample Landing Page, Sample Set Landing Page, and the Sample Set Viewer.

## Prerequisites

In order to build and test the specs, you just need `make`, `docker`, and a `bash` compatible shell.

For editing the files, you will also need to have Python 3.7 available. No special Python tooling is required, but it is recommended to use `black` to format all code prior to issuing a pull request.

## Legacy Config Generation

The Sample Service and Sample Uploader currently expect to find configuration files in specific locations in the "master" branch of this repo. In this document, these are called "legacy" config files.

At some future time these services will be refactored to pick up the same files from a distribution branch, as is described in sections below.

The legacy configuration files are created locally by a developer after making changes to the sources, and then pushed up to the canonical repo along with the source changes, and ultimately made available by merging a Pull Request to the master branch.

In order to generate these files, issue the following command:

```bash
make legacy-files
```

This will result in the following files being created or replaced:

```text
├── metadata-validation.json
└── templates
    ├── enigma_template.yml
    └── sesar_template.yml
```

- `metadata-validation.json` - KBase-formatted validation configuration for each defined metadata field
- `templates/enigma_template.yml` - Metadata fields defined for the ENIGMA sample type, utilized by the importer
- `templates/sesar_template.yml` - Metadata fields defined for the SESAR sample type, utilized by the importer

### Consumption by Services

This section describes how services consume the legacy files.

#### Sample Service

The Sample Service fetches the `metadata_validation.yml` file directly from the master branch of this repo through the url `https://raw.githubusercontent.com/kbase/sample_service_validator_config/master/metadata_validation.yml`.

#### Sample Importer

Sample import is conducted by the `import_samples` method of the `sample_uploader` app. This app acquires the legacy validation and template configs by cloning this repo at a specific commit by hash reference.

## Generating Config Distribution

A new generation process has been designed to replace the legacy process described above. Rather than generate the configs and include them in the repo directly, they are generated in the GitHub repository through a GitHub Action workflow, `.github/build-dist.yml`. We refer to the set of generated files intended for external usage as the "distribution", or "dist" for short.

The generated files are made available in special distribution branches, which are either created or updated by the workflow itself. This process is described in more detail below.

You may generate the distribution locally with just Docker.

The following command

```bash
make
```

will build a Docker image with Python and all dependencies installed, and then proceed to run a set of scripts via the container to build and validate the source files, build the distribution, and validate the distribution.

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
├── sample_fields.html
├── schemas.json
└── templates
    ├── enigma_template.yml
    └── sesar_template.yml

1 directory, 8 files
```

Let's itemize those files

- `README.me` - short doc describing the directory
- `groups.json` - field grouping and ordering, covering all fields defined in `schemas.json`.
- `manifest.json` - information about the distribution build
- `metadata_validation.yml` - field definitions for services
- `schemas.json` - field definitions provided as an array of JSON-Schema specs, one per field, for user interfaces
- `templates` - upload templates
  - `sesar_template.yml` - upload template for SESAR samples
  - `enigma_template.yml` - upload template for ENIGMA samples

## GitHub Action Workflow Process

The heart of the GitHub Action build workflow invokes the makefile as described above. In addition to the build and validation steps, it also takes care to capture the generated files in distribution branches. More on that later.

An additional small workflow deletes distribution branches created for pull requests after the PR is merged.

### Build and Validate

The "Sample Service Validator Config Distribution Builder" workflow, `.github/build-dist.yml`, is responsible for validating the source specs, creating the generated files, and validating the generated files.

The generation and validation of config files is conducted via the Makefile as a sequence of scripts run inside a docker container. This workflow step is the same one utilized in the local build procedure described above.

#### Preparation Steps

The workflow first takes care of boilerplate operations, like cloning the repo and preparing some environment variables.

The final preparation step is to create the script-runner image, which is tagged `cli`, since it is used for running commands.

#### Validation and Build Steps

Following the preparation steps is the validation and build step. A repo directory (i.e. in the GHA runner itself) is volume mounted into the container at `/kb/module`. This allows the files generated within the container to be available in the GHA host for later steps.

These steps carry out the following tasks:

- validation source spec files
- generate files for distribution into `dist`
- validate generated files 
- copies a special `README.md` into the `dist` directory
- creates a special `manifest.json` file in `dist`, containing information about the build itself

#### Create distribution branch steps

After the `dist` directory is populated and verified, it is copied into a special `dist-*` branch. Which branch it is copied into depends on which trigger invoked the workflow.

The following trigger and branch naming conventions are used:

| trigger                             | description                                                                                                                                               | branch name           | tag name              |
|-------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------|-----------------------|
| `pull_request` to `master`          | Default triggers (`opened`, `synchronize`, `reopened`) for a PR against `master`; `#` is the PR number                                                    | `dist-pull_request-#` | n/a                   |
| `push` to `master`                  | Captures primarily PR merging into the master branch, but also other commits; creates                                                                     | `dist-master`         | n/a                   |
| `release` `published` from `master` | Captures the state of a `release` against the `master` branch when it is `published`; `v*.*.*` is the semantic-version-formatted tag used for the release | `dist-release`        | `dist-release-v#.#.#` |

The resulting branch is created or updated with just the contents of the `dist` directory; all other content in the repo is absent. This makes these branches suitable for consumption by downstream services or clients.

Note that releases create or update an evergreen branch `dist-release` as well as creating a per-release
tag `dist-release-v#.#.#` on the `dist-release` branch.

### Remove pull request branches

As you, astute reader, may have recognized, creating a distribution branch per pull request would result in many extant `dist-pull_request-#` branches. When a PR is active, the pull request branches can be useful for testing and evaluation. However, once a PR is closed (whether merged or abandoned), the associated `dist` branch has no further use.

The workflow verbosely named `delete-closed-pr-dist-branch.yml` takes care of that by triggering the deletion of a PR's `dist` branch when the PR is closed, using the trigger `pull_request` for `master` branch when `closed`.

### GHA Token

The GHA workflow requires a token named `KBASE_BOT_TOKEN`. This token requires just `repo:public_repo` access.

- create a PAT or other token with `repo:public_repo` access
- create a secret named `KBASE_BOT_TOKEN` with the value set to the token
