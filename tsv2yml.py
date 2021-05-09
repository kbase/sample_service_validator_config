#!/usr/bin/env python

import csv
import sys
import yaml
from yaml import Dumper, Loader
import json

valid_transforms = ['map', 'percent', 'unit_measurement', 'unit_measurement_fixed', '']
validation = yaml.load(open('metadata_validation.yml'), Loader=Loader)
outdata = {}
failed = False
required_units = []
with open(sys.argv[1]) as csvfile:
    spamreader = csv.DictReader(csvfile, delimiter='\t')
    ct = 0
    for row in spamreader:
        col_name = row['Column name']
        new = {
              'category': row['Category'],
              'example': row['Example'].replace("\r\n", ' '),
              'definition': row['Definition'].replace("\r\n", ' '),
              'order': ct
              }
        new['required'] = False
        if row['Required'].lower() == 'y':
            new['required'] = True
        if row['Additional instructions'] != '':
            new['instructions'] = row['Additional instructions']
        new['aliases']=[col_name.lower()]
        if 'Aliases' in row and row['Aliases'] != '':
            for alias in row['Aliases'].split(','):
                new['aliases'].append(alias) 
                new['aliases'].append(alias.lower()) 
        transform = row['Transformation']
        if transform not in valid_transforms:
            print("Transform %s not recognized" % (transform))
            failed = True
        if transform:
            new['transformations'] = [{'transform': transform}]
            params = []
            for param in ['Parameter', 'Parameter 2']:
                if row[param]:
                    params.append(row[param])
            if len(params) > 0:
                new['transformations'][0]['parameters'] = params
            if transform == "map":
                kid = row['Parameter']
                if row['Parameter'] not in validation['validators']:
                    failed = True
                    print("Missing %s" % (row['Parameter']))
                    if row['Parameter'].replace('sesar:','') in validation['validators']:
                        print("Maybe core")
            elif transform == "unit_measurement":
                kid = row['Parameter']
                if row['Parameter'] not in validation['validators']:
                    failed = True
                    print("Missing %s" % (row['Parameter']))
                if row['Parameter 2'] == "":
                    failed = True
                    print("Missing field %s" % (col_name))
                required_units.append(row['Parameter 2'])
            elif transform == "unit_measurement_fixed":
                kid = row['Parameter']
                if row['Parameter'] not in validation['validators']:
                    failed = True
                    print("Missing %s" % (row['Parameter']))
                if row['Parameter 2'] == "":
                    failed = True
                    print("Missing unit %s" % (col_name))
#            if not failed:
#                print(validation['validators'][kid]['key_metadata']['description'])
        outdata[col_name] = new
        ct += 1

# Verify that all refernced units exist
for key in required_units:
     if key not in outdata:
         print("Missing unit key %s" % (key))
         failed = True

if failed:
    sys.exit(1)
print(yaml.dump(outdata, Dumper=Dumper, default_flow_style=False))
