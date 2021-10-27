# Build and Deploy Sample Specs

The Sample Specifications are maintained in an internal YAML format, located in files stored in the `specs` directory.

- `specs/vocabularies/*.yml` - define sample fields
- `specs/templates/*.yml` - define upload templates
- `specs/ordered.yml` - defines sample field grouping and ordering

For historical reasons, these files are transformed into an additional set of files for usage by the Sample Service, Sample Uploader, and sample user interfaces. The process of transforming the source specifications to generate an additional set of files for usage is the subject of this document.

There are actually two sets of generated files. The original set is composed of yaml files in a proprietary format:

- `metadata_validation.yml` - field definitions
- `templates/sesar_template.yml` - upload template for SESAR samples
- `templates/enigma_template.yml` - upload template for ENIGMA samples

These files are used by the Sample Service and Sample Uploader. The Sample Service uses `metadata_validation.yml` to validate individual sample fields. The Sample Uploader uses `metadata_validation.yml` to validate sample fields, and the templates to validate sample sets of type SESAR or ENIGMA.

The second set are composed of JSON files, one of which is in JSON-Schema format.

- `schemas.json` - field definitions provided as an array of JSON-Schema specs, one per field
- `groups.json` - field grouping and ordering, covering all fields defined in `schemas.json`.

These files are utilized by user interfaces, including the Sample Landing Page, Sample Set Landing Page, and the Sample Set Viewer.

## Generating

You won't find the generated files in the repo. In a previous iteration, the generated files were created locally by a developer after making changes to the sources, and then pushed up to the canonical repo. They would eventually be made available by creating a release at GitHub, and the resulting generated files fetched directly from the repo (master branch? actual release?)

The generation process was redesigned to take place in the upstream GitHub repository through a GitHub Action workflow, `.github/build-dist.yml`. We refer to the set of generated files intended for external usage as the "distribution", or "dist" for short.

Although the distribution is not stored in the main repo, you may generate them locally with just Docker.

The following command

```bash
make
```

will build a Docker image with Python and all dependencies installed, and then proceed to run a set of scripts to build and validate the source files, build the distribution, and validate the distribution.

The `Makefile` also contains tasks to run each group of scripts separately.

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

The heart of the GitHub Action build workflow is equivalent to the script run above. In addition to the build and validation steps, it also takes care to capture the generated files in distribution branches. More on that later.

An additional small workflow deletes distribution branches created for pull requests.

### Build and Validate

The "Sample Service Validator Config Distribution Builder" workflow, `.github/build-dist.yml`, is responsible for validating the source specs, creating the generated files, and validating the generated files.

The workflow has a single step for each logical operation. Each operation is run inside a docker container, the same one utilized in the local build procedure. If you peek into the workflow file, you'll see that each each step actually runs a shell script. The default entry point for the image is `bash`, and the command is expected to be a script. All of the scripts run within the workflow are located in `scripts/automation`.

Each shell script in turn calls a Python script to conduct the actual work. These scripts are located in `scripts/export` and `scripts/validate`. This double-step process is used because each Python script expects a certain number of parameters. This facilitates re-usage for some of the scripts, and testability for all. It also insulates the build process from the details of script execution, other than the very simple shell scripts. However, the build process always uses the same parameters. The automation scripts are used to decouple the workflow from the specific values required, and instead they are encoded into the automation scripts.

#### Preparation Steps

The workflow first takes care of boilerplate operations, like cloning the repo and preparing some environment variables.

The final preparation step is to create the script-runner image, which is tagged `cli`, since it is used for running commands.

#### Validation and Build Steps

Following the preparation steps is a sequence of validation and build steps, all run through the script-runner container simply using docker run. A local (i.e. in the GHA runner itself) directory `dist` is volume mounted into the container at `/kb/module/dist`. This allows the files generated within the container to be available locally.

These steps carry out the following tasks:
    - validation source spec files
    - generate files for distribution into `dist`
    - validate generated files
    - copies a special `README.md` into the `dist` directory
    - creates a special `manifest.json` file in `dist`, containing information about the build itself

#### Create distribution branch steps

After the `dist` directory is populated and verified, it is copied into a special `dist-*` branch. Which branch it is copied into depends on the trigger which invoked the workflow.

The following trigger and branch naming conventions are used:

| trigger                             | description                                                                                                                                               | branch name           | tag name              |
|-------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------|-----------------------|
| `push` to `master`                  | Captures primarily PR merging into the master branch, but also other commits; creates                                                                     | `dist-master`         | n/a                   |
| `pull_request` to `master`          | Default triggers (`opened`, `synchronize`, `reopened`) for a PR against `master`; `#` is the PR number                                                    | `dist-pull_request-#` | n/a                   |
| `release` `published` from `master` | Captures the state of a `release` against the `master` branch when it is `published`; `v*.*.*` is the semantic-version-formatted tag used for the release | `dist-release` | `dist-release-v#.#.#` |

The resulting branch is created or updated with just the contents of the `dist` directory; all other content in the repo is absent. This makes these branches suitable for consumption by downstream services or clients.

Note that releases create or update an evergreen branch `dist-release` as well as creating a per-release tag `dist-release-v#.#.#` on the `dist-release` branch.

### Remove pull request branches

As you, astute reader, may have recognized, creating a distribution branch per pull request would result in many extant `dist-pull_request-#` branches. When a PR is active, the pull request branches can be useful for testing and evaluation. However, once a PR is closed (whether merged or abandoned), the associated `dist` branch has no further use.

The workflow verbosely named `delete-closed-pr-dist-branch.yml` takes care of that by triggering the deletion of a PR's `dist` branch when the PR is closed, using the trigger `pull_request` for `master` branch when `closed`.
