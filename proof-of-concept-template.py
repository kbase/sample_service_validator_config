#!/usr/bin/env python

import yaml
from yaml import Dumper, Loader
import json
import csv
import sys
from SampleServiceClient import SampleService

def alias_map(templ):
    """
    aliases map
    Expand all the aliases into a map
    This maps from the alias name to the proper column name
    """
    aliases = dict()
    for field in templ:
        aliases[field] = field
        aliases[field.lower()] = field
        for alias in templ[field].get('aliases',[]):
            aliases[alias] = field
    return aliases

# Do a reverse lookup in the map
def _lookup_by_value(themap, value):
    """
    Do a reverse lookup on a map (assumes 1-to-1)
    """
    for k in themap:
        if value == themap[k]:
            return k
    return None

def gen_source(newkey, col, value):
    src = {
       'key': newkey,
       'skey': col,
       'svalue': {'value': value}
       }
    return src

def merge_transform(row, transform, col_map):
    method = transform['transform']
    params = transform['parameters']
    if method == 'merge_time':
        print("TODO")
        df = _lookup_by_value(col_map, params[0])
        tf = _lookup_by_value(col_map, params[1])
    elif method == 'other':
        print("TODO")
    else:
      raise ValueError("Not implemented")

def controlled_term(row, col, conf, col_map):
    """
    Transform one controlled value
    """
    pairs = dict()
    source = []
   
    if 'transformations' not in conf:
        # Unused or used as merged field
        return pairs, source
    value = row[col]
    if value == "" or value == None:
        return pairs, source
    for t in conf['transformations']:
        if t['transform']=='map':
           newkey = t['parameters'][0]
           pairs[newkey] = {'value': value}
           source.append(gen_source(newkey, col, value))
        elif t['transform']=='unit_measurement_fixed':
           newkey = t['parameters'][0]
           pairs[newkey] = {'value': float(value)}
           pairs[newkey]['units'] = t['parameters'][1]
           source.append(gen_source(newkey, col, value))
        elif t['transform']=='unit_measurement':
           newkey = t['parameters'][0]
           pairs[newkey] = {'value': float(value)}
           unit_field = _lookup_by_value(col_map, t['parameters'][1])
           pairs[newkey]['units'] = row[unit_field]
           source.append(gen_source(newkey, col, value))
        else:
           raise ValueError("Transform {} not implemented".format(t))
    return pairs, source

def do_row(row, templ, col_map):
    """
    Process a single row
    Returns: controlled terms, user terms, and source meta data
    """
    cont = dict()
    user = dict()
    source = []
    templ_cols = templ['Columns']
    for k in row.keys():
        if k in col_map:
            pk = col_map[k]
            cterms, sterms = controlled_term(row, k, templ_cols[pk], col_map)
            cont.update(cterms)
            source.extend(sterms)
        else:
            user[k] = row[k]
    for t in templ['Merge']:
        merge_transform(row, t, col_map)
    return cont, user, source

def find_aliases(fields, aliases):
    """
    Scans through columns and finds the proper name 
    """
    col_map = dict()
    for k in fields:
        if k in aliases:
           col_map[k] = aliases[k]
        if k.lower() in aliases:
           col_map[k] = aliases[k.lower()]
    return col_map

def generate_sample(id, name, controlled_metadata, user_metadata, source_meta):
    """
    Create a sample record
    """
    sample = {
        'node_tree': [{
            "id": id,
            "type": "BioReplicate",
            "meta_controlled": controlled_metadata,
            "meta_user": user_metadata,
            'source_meta': source_meta
        }],
        'name': name,
    }
    return sample

def read_data(fn):
    """
    Read data from a TSV file
    """
    rows = []
    with open(sys.argv[2]) as fn:
        data = csv.DictReader(fn, delimiter='\t')
        cols = data.fieldnames
        for row in data:
            rows.append(row)
    return cols, rows 


def main():
    """
    main routine
    takes a template YAML file and TSV as input
    """
    templ_fn = sys.argv[1]
    tsv_fn = sys.argv[2]
    ss = SampleService('https://ci.kbase.us/services/sampleservicetest')
    print(ss.status())
#    print(json.dumps(ss.get_sample({'id': 'af2e6802-8cfa-4076-bcff-5c120652694b'}), indent=2))
    templ = yaml.load(open(templ_fn), Loader=Loader)
    templ_cols = templ['Columns']
    idfield = templ['ID']
    namefield = templ['Name']
    aliases = alias_map(templ_cols)
    cols, rows = read_data(tsv_fn)
    col_map = find_aliases(cols, aliases)
    for row in rows:
        cont, user, source = do_row(row, templ, col_map)        
        name = cont[namefield]['value']
        id = cont[idfield]['value']
        sample = generate_sample(id, name, cont, user, source)
        #print(json.dumps(sample, indent=2))
        resp = ss.create_sample({'sample': sample})
        print(resp)
        break

if __name__ == "__main__":
    main()
