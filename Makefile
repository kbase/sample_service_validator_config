VALIDATION_FILE=metadata_validation.yml
TEMP_FILE=temp_file.yml
TEMP_FILE_2=temp_file2.yml
SAMPLE_SERVICE_SCHEMA = test_data/validator_schema.json
MACRO_SCHEMA = test_data/validator_macro_schema.json
VOCAB_SCHEMA = test_data/vocabulary_schema.json
TEMPLATES_DIR = 'templates'

all: update templates

templates:
	python3 ./gen_template_yaml.py sesar_template.yml sesar.tsv
	python3 ./gen_template_yaml.py enigma_template.yml enigma.tsv
test:
	python3 scripts/validate_schemas.py $(SAMPLE_SERVICE_SCHEMA) $(VALIDATION_FILE)
	python3 scripts/validate_schemas.py $(MACRO_SCHEMA) vocabularies/*yml
	python3 scripts/validate_templates.py $(TEMPLATES_DIR)/*yml
	python3 scripts/validate-jsonschema.py all

update:
	python3 scripts/export/merge_validators.py $(VALIDATION_FILE) 
	python3 scripts/export/create_tsv.py $(VALIDATION_FILE)
	python3 scripts/export/ui_export.py dist
