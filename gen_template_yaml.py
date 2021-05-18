#!/usr/bin/env python

import csv
import sys
import yaml
from yaml import Dumper, Loader
import json


def load_validations():
    return yaml.load(open('metadata_validation.yml'), Loader=Loader)


def read_tsv(csvfn):
    """
    Read in the table of terms.  Each row defines the column in the
    template file
    """
    rows = []
    col_names = []
    with open(csvfn) as csvfile:
        data = csv.DictReader(csvfile, delimiter='\t')
        for row in data:
            rows.append(row)
            col_names.append(row['Column name'])
    return rows, col_names

def create_aliases(col_name, prov_aliases):
    """
    Expand out the aliases
    """
    aliases=[col_name.lower()]
    if prov_aliases and prov_aliases != '':
        for alias in prov_aliases.split(','):
            aliases.append(alias) 
            aliases.append(alias.lower()) 
    return aliases

def validate_transform(new_transform):
    """
    Validate the tranform. Make sure the transform is valid
    and that the appropriate parameters are passed.
    """
    valid_transforms = ['map', 'percent', 'unit_measurement', 'unit_measurement_fixed', '']
    transform = new_transform['transform']
    params = new_transform.get('parameters', [])
    if transform not in valid_transforms:
        raise KeyError("Transform %s not recognized" % (transform))
    if transform:
        # get params
        ids = []
        col_ids = []
        if transform == "map":
            ids.append(params[0])
        elif transform == "unit_measurement":
            ids.append(params[0])
            if params[1] == "":
                raise ValueError("Missing field %s" % (col_name))
            col_ids.append(params[1])
        elif transform == "unit_measurement_fixed":
            ids.append(params[0])
            if params[1] == "":
                raise ValueError("Missing unit %s" % (col_name))
    return ids, col_ids

def process_row(row, ct):
    """
    Process a single row and return the column definition
    """
    col_name = row['Column name']
    ids = []
    col_ids = []
#          'category': row['Category'],
#          'example': row['Example'].replace("\r\n", ' '),
#          'definition': row['Definition'].replace("\r\n", ' '),
#          'order': ct
    new = {
          }
    new['required'] = False
    if row['Required'].lower() == 'y':
        new['required'] = True
#    if row['Additional instructions'] != '':
#        new['instructions'] = row['Additional instructions']
    new['aliases']=create_aliases(col_name, row.get('Aliases'))
    transform = row['Transformation']
    if transform != '':
        new_transform = {'transform': row['Transformation']}
        params = []
        for param in ['Parameter', 'Parameter 2']:
            if row[param]:
                params.append(row[param])
        if len(params) > 0:
            new_transform['parameters'] = params
        ids, col_ids = validate_transform(new_transform)
        new['transformations'] = [new_transform]
    return col_name, new, ids, col_ids

def main():
    failed = False
    required_units = []
    yamlfn = sys.argv[1]
    csvfn = sys.argv[2]
    validation = load_validations()
    ct = 0
    rows, cols = read_tsv(csvfn)
    outdata = {}
    for row in rows:
        col_name, new_row, ids, col_ids = process_row(row, ct)
        for kid in ids:
            if kid not in validation['validators']:
                print("Missing %s" % (kid))
                failed = True
        # Verify that referenced unit column exist
        for key in col_ids:
            if key not in cols:
                print("Missing unit key %s" % (key))
                failed = True
        outdata[col_name] = new_row
        ct += 1


    if failed:
        sys.exit(1)
    # Generate new yaml file
    newtemp = yaml.load(open(yamlfn), Loader=Loader)
    if 'Columns' in newtemp:
        newtemp.pop('Columns')
    newtemp['Columns'] = outdata
    with open(yamlfn, "w") as f:
         f.write(yaml.dump(newtemp, Dumper=Dumper, default_flow_style=False))

if __name__ == '__main__':
    main()
