# GHA-based sample service spec releases

## Concepts

The sample service specs are composed of source yaml files which are processed to create a set of json files intended for consumption by external services or processes.

At present, both the sample importer and sample service consume these files.

The goal of this effort is to provide a more reliable method for producing and consuming these files.

An idealized workflow is:

- a contributor (internal or external) checks out the sample service spec repo
- Contributor creates a branch
- Contributor adds or modifies source yaml specs
- Contributor runs tests to ensure that the changes are compliant (pass internal validation)
- Contributor is somehow able to verify that the changes will work with their samples (at least to an initial degree)
- Contributor pushes their branch to the canonical KBase repo under their branch name.
  - Or perhaps, if we are accepting changes from external developers, we need to stick with the forking model
- Contributor issues a Pull Request to the kbase repo
- If all tests pass, a development release is created under some branch naming schema
  - This allows the CI or some other environment sample service and/or importer to be temporarily deployed against the development release
- Upon approval, the PR is merged by KBase staff
- Upon commits to "main", including PR merging, a new "development" tag is created.
  - This tag may be used for evaluating changes in CI or next.
- A release is created with a semver tag
  - fixes will result in a fix number increment, e.g. 1.2.3 -> 1.2.4
  - any additions result in a minor version number increment, e.g. 1.2.3 -> 1.3.0
  - any breaking changes, e.g. a change to the format, results in a major version number bump, e.g. 1.2.3 -> 2.0.0
- A release will also be created with an evergreen "latest" or "release" tag
- A release may be marked as pre-release, and should use a semver tag like 1.2.3-dev.1, 1.2.3-dev.2, etc.
  - Not sure about this - an evergreen 
- The sample service has a method for triggering it to fetch a release, receiving a tag.
- The sample service will clone or fetch an archive of the repo at the provided tag, extract the necessary files, and place them in the sample servers filesystem.
  - any related caches will need to be cleared
  - the sample importer will need a similar process, but that is out of scope here
  - even if the method call is for the currently active version, the fetch and extraction will occur; this supports tickling the service for evergreen branches like "release" and "develop"
- The sample service will store the most recently set tag somewhere; the only persistent storage available is arangodb, so that is the likely location.
- Upon restarting, the sample service will consult database for the current config tag, fetch and extract it before starting.
- A fresh installation will require a configuration option, e.g. environment variable, to set the baseline release to use, or the most recent release can be queried from GitHub.

## Current Process

The current process 





## The Plan

Documentation on the process

Remove all generated assets

Add GHA to:

	- generate assets
	- create a branch
	- commit the changes to the branch
	- ideally the branch is composed of only the generated files

all generated files in to a single dist directory at the top level

## Distribution branches

What to name them?

We should operate the repo with forks and PRs. Thus we don't need to support feature or fix branches.

The reason is that we expect third party contribution, and the branch/PR model requires giving push access to the repo.

### Releases

Created when a release is created through github.

Format: For release `v1.2.3`: `dist-release-v1-2-3`

Usage: usage in production sample service, sample uploader

Also the evergreen branch `release` is created?

### Pull Requests

Created when a PR is created or updated

Format:  For PR 123, `dist-pr-123`

Usage: Evaluation of changes in a pull request. E.g. may be temporarily deployed to CI, or used in local testing.

### Merge to `master`

Created when anything is merged into the `master` branch. Most common use case is Pull Requests. Enables usage of latest approved changes in CI.

Format: `dist-master`

Usage: an evergreen distribution for CI



## Questions

I think the dist-per-pr should be utilized, but I fear it will be underutilized compared to the # of dist-pr-* branches that might be created.

One solution is to create them, but to have a GHA which deletes PR dist branches when they are merged. This might get messy, though, with the sample service CI deploys, which might get tied to a particular PR for evaluation, but them someone forgets to reset it to dist-master after merging the PR.