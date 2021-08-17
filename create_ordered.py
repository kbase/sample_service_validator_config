import yaml
from yaml import Dumper, Loader
import json
import sys
categories = yaml.load(open(sys.argv[1]), Loader=Loader)

ordered_cat = dict()
for f in sys.argv[2:]:
   templ = yaml.load(open(f), Loader=Loader)
   ordered = [None] * 200
   for k in templ:
       ordered[templ[k]['order']] = k
   for i in ordered:
       if not i:
           continue
       cat = templ[i]['category']
       if 'transformations' not in templ[i]:
           continue
       kbk = templ[i]['transformations'][0]['parameters'][0]
       if cat not in ordered_cat:
           ordered_cat[cat] = list()
       if kbk not in ordered_cat[cat]:
           ordered_cat[cat].append(kbk)

cat_order = [ 'description', 'geolocation', 'collection', 'curation', 'measurement', 'well', 'relation_to_parent']
order = {'ordered': []}
for cat in cat_order:
    order['ordered'].append({'name': cat, 'display': categories[cat]['display'], 'ordered_fields': ordered_cat[cat]})


print(yaml.dump(order))
