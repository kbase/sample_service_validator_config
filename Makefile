all: script-runner validate-specs generate-dist validate-dist

script-runner:
	@docker build -t cli .

validate-specs:
	@echo "validate source specs"
	@docker run --rm cli scripts/automation/validate_source_specs.sh
	@echo "validate source spec units"
	@docker run --rm cli scripts/automation/validate_vocabulary_units.sh

generate-dist:
	@echo "build UI exports in 'dist' directory"
	@docker run --rm -v `pwd`/dist:/kb/module/dist cli scripts/automation/ui_export.sh 
	@echo "build validators config in 'dist' directory"
	@docker run --rm -v `pwd`/dist:/kb/module/dist cli scripts/automation/merge_validators.sh
	@echo "build validators documentation table in 'dist' directory"
	@docker run --rm -v `pwd`/dist:/kb/module/dist cli scripts/automation/create_fields_table.sh
	@echo "build templates in "dist" directory"
	@docker run --rm -v `pwd`/dist:/kb/module/dist cli scripts/automation/build_templates.sh
	@echo "add a 'readme' file to the dist directory"
	@docker run --rm -v `pwd`/dist:/kb/module/dist cli scripts/automation/copy_other_files.sh
	@echo "add a 'manifest' file to the dist directory"
	@docker run --rm -v `pwd`/dist:/kb/module/dist cli scripts/automation/create_manifest.sh

validate-dist:
	@echo "validate the generated validator files"
	@docker run --rm -v `pwd`/dist:/kb/module/dist cli scripts/automation/validate_generated_validators.sh
	@echo "validate the generated ui spec files"
	@docker run --rm -v `pwd`/dist:/kb/module/dist cli scripts/automation/validate_ui_export.sh

metadata-validation-file: script-runner
	@echo "build validators config in root directory"
	@docker run --rm -v `pwd`:/kb/module cli scripts/automation/merge_validators_legacy.sh
