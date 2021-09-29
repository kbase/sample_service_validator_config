docker build -t cli .

echo "run tests in container"
docker run -v `pwd`/dist:/kb/module/dist cli scripts/automation/validate_source_specs.sh

echo "build UI exports in 'dist' directory"
docker run -v `pwd`/dist:/kb/module/dist cli scripts/automation/ui_export.sh 

echo "build validators config in 'dist' directory"
docker run -v `pwd`/dist:/kb/module/dist cli scripts/automation/merge_validators.sh

echo "build validators documentation table in 'dist' directory"
docker run -v `pwd`/dist:/kb/module/dist cli scripts/automation/create_fields_table.sh

echo "build templates in "dist" directory"
docker run -v `pwd`/dist:/kb/module/dist cli scripts/automation/build_templates.sh

echo "validate the generated validator files"
docker run -v `pwd`/dist:/kb/module/dist cli scripts/automation/validate_generated_validators.sh

echo "validate the generated ui spec files"
docker run -v `pwd`/dist:/kb/module/dist cli scripts/automation/validate_ui_export.sh

echo "add a 'readme' file to the dist directory"
docker run -v `pwd`/dist:/kb/module/dist cli scripts/automation/copy_readme.sh

echo "add a 'manifest' file to the dist directory"
docker run -v `pwd`/dist:/kb/module/dist cli scripts/automation/create_manifest.sh
