.PHONY: script-runner validate-specs clean validate-dist legacy-files

all: clean script-runner validate-specs dist validate-dist

script-runner:
	@docker build -t cli .

validate-specs:
	@printf "Validating source specs..."
	@docker run --rm -v ${PWD}:/kb/module cli scripts/automation/validate_source_specs.sh
	@printf "done.\n"
	@printf "Validating source spec units..."
	@docker run --rm -v ${PWD}:/kb/module cli scripts/automation/validate_vocabulary_units.sh
	@printf "done.\n"

clean:
	@printf "Removing dist directory..."
	@rm -rf dist
	@printf "done.\n"
	@printf "Removing the dist archive..."
	@rm -f dist.zip
	@printf "done.\n"

dist:
	@printf "Building UI exports in 'dist' directory..."
	@docker run --rm -v ${PWD}:/kb/module cli scripts/automation/ui_export.sh
	@printf "done.\n"
	@printf "Building validators config in 'dist' directory..."
	@docker run --rm -v ${PWD}:/kb/module cli scripts/automation/merge_validators.sh
	@printf "done.\n"
	@printf "Building validators documentation table in 'dist' directory..."
	@docker run --rm -v ${PWD}:/kb/module cli scripts/automation/create_fields_table.sh
	@printf "done.\n"
	@printf "Building templates in "dist" directory..."
	@docker run --rm -v ${PWD}:/kb/module cli scripts/automation/build_templates.sh
	@printf "done.\n"
	@printf "Adding a 'readme' file to the dist directory..."
	@docker run --rm -v ${PWD}:/kb/module cli scripts/automation/copy_other_files.sh
	@printf "done.\n"
	@printf "Adding a 'manifest' file to the dist directory..."
	@docker run --rm -v ${PWD}:/kb/module cli scripts/automation/create_manifest.sh
	@printf "Zip the dist directory..."
	@docker run --rm -v ${PWD}:/kb/module cli scripts/automation/zip_dist.sh
	@printf "done.\n"

validate-dist:
	@printf "Validating the generated validator files..."
	@docker run --rm -v ${PWD}:/kb/module cli scripts/automation/validate_generated_validators.sh
	@printf "done.\n"
	@printf "Validating the generated ui spec files..."
	@docker run --rm -v ${PWD}:/kb/module cli scripts/automation/validate_ui_export.sh
	@printf "done.\n"

legacy-files: script-runner
	@printf "Building validators config in root directory..."
	@docker run --rm -v ${PWD}:/kb/module cli scripts/automation/merge_validators_legacy.sh
	@printf "done.\n"
	@printf "Building templates in "dist" directory..."
	@docker run --rm -v ${PWD}:/kb/module cli scripts/automation/build_templates_legacy.sh
	@printf "done.\n"
	@printf "Build the ontology validators file..."
	@docker run --rm -v ${PWD}:/kb/module cli scripts/automation/build_ontology_validators.sh
	@printf "done.\n"
	@printf "Validate the generated validator files..."
	@docker run --rm -v ${PWD}:/kb/module cli scripts/automation/validate_validators_legacy.sh
	@printf "done.\n"
