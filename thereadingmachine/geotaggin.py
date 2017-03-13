import re
import sys
import os
from collections import defaultdict

d_countries = defaultdict()

input_file_name = sys.argv[1]

## Create dictionary
def make_dict_countries(raw, d_rep, separ = ";"):
    id_country, list_synon = raw.split(separ)
    ## Get list of synonymous names
    list_synon = list_synon.split(",")
    ## Add as synonymous the country name itself
    list_synon.append(id_country)
    ## Remove empty synonymous
    list_synon = filter(None, list_synon)
    ## Remove if any duplicates
    list_synon = list(set(list_synon))
    ## Add to dictionary
    [d_rep[id_country].append(x) for x in list_synon]


## Return countries in article
def check_countries(text, dict):
    results = []
    for k in dict.keys():
        if any(words in text for words in dict[k]):
            results.append(k)
    results = list(set(results))
    return results
              
## Formatting input file
list_countries = []
with open(input_file_name, 'rU') as f:
    for line in f:
        ## Remove all parenthesis and their content
        regex = re.compile('\(.+?\)')
        countries = regex.sub('', line.strip())
        ## Remove non-informative character
        regex = re.compile("_")
        countries = regex.sub('', countries)
        ## Remove quotes
        regex = re.compile('"')
        countries = regex.sub('', countries)
        ## Remove spaces before commas
        regex = re.compile(" *, *")
        countries = regex.sub(',', countries)
        ## Filtering empty fields
        list_countries.append(';'.join([x.strip() for x in filter(None, countries.split(';'))]))
        #print(';'.join([x.strip() for x in filter(None, countries.split(';'))]))

## Create dictionary of countries
d_countries = defaultdict(list)
[make_dict_countries(l, d_countries) for l in list_countries]






