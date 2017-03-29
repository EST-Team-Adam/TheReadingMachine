## Create dictionary of countries
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
    if id_country == "Spain":
        pass
    for x in list_synon:
        try:
            x = x.decode('utf-8')
        except UnicodeDecodeError:
            x = NA
    ## Add to dictionary
    [d_rep[id_country].append(x) for x in list_synon]

## Return countries (keys) in article
def check_countries(text, dict):
    results = []
    for k in dict.keys():
        print k
        if any(words in text for words in dict[k]):
            results.append(k)
    results = list(set(results))
    return results
              
## Read table countries 
def read_countries(file):
    import re
    with open(file, 'rU') as f:
        list_countries = []
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
        return list_countries
