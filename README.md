# sample-service-validator-config

[![standard-readme compliant](https://img.shields.io/badge/standard--readme-OK-green.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

Sample specification definitions and generator for files to be used by services and apps.

This repo contains:

- the source specification files defining all sample fields known to the KBase Sample System. The specs contain definitions, validation rules, and user interface hints.
- a standard grouping and ordering of all sample fields
- collections of fields into "templates" used by the sample importer
- tools (scripts) to generate files more suitable for consumption by downstream services, apps, and user interfaces

## Table of Contents

- [Background](#background)
- [Install](#install)
- [Usage](#usage)
- [API](#api)
- [Maintainers](#maintainers)
- [Contributing](#contributing)
- [License](#license)

## Background

The KBase Sample Service is a collection of services, apps, and user interfaces for managing and using samples within KBase.

A sample is composed of individual sample measurement or observations which are stored as individual fields within the system. This repo exists to provide uniform validation of samples as they enter the system, naming and descriptions, and presentation characteristics.

It achieves this by serving as a repository for all sample fields, as well as two strategies for organizing them (templates, and groupings), which are prepared and packaged for usage via a build and publish workflow at GitHub.

The published files are currently utilized by the following KBase products:

- [Sample Service](https://github.com/kbase/sample_service)
- [Sample Uploader](https://github.com/kbaseapps/sample_uploader)
- [Sample Landing Page](https://github.com/kbase/kbase-ui-plugin-samples)
- [Sample Set Landing Page](https://github.com/kbase/kbase-ui-plugin-dataview)
- [Narrative](https://github.com/kbase/narrative)

## Install

Prerequisites:

- Docker
- Python 3

Generation and validation of files requires Docker. Development of scripts requires Python 3.

## Usage

To validate source, generate files, and validate generated files:

```bash
make
```

Please see [the developer docs](docs/index.md) for further information.

## API

Generated configuration files are available in distribution branches - see [the build and deploy docs](docs/build-and-deploy.md).

## Maintainers

KBase Developers

## Contributing

See [the contributing file](CONTRIBUTING.md)!

PRs accepted.

If editing the README, please conform to the [standard-readme](https://github.com/RichardLitt/standard-readme) specification.

## License

[LICENSE.md](LICENSE.md)
