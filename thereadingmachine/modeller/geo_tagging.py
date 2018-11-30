import pandas as pd
from collections import defaultdict
# Create dictionary of countries


def make_dict_countries(raw, d_rep, separ=";"):
    id_country, list_synon = raw.split(separ)
    # Get list of synonymous names
    list_synon = list_synon.split(",")
    # Add as synonymous the country name itself
    list_synon.append(id_country)
    # Remove empty synonymous
    list_synon = filter(None, list_synon)
    # Remove if any duplicates
    list_synon = list(set(list_synon))
    if id_country == "Spain":
        pass
    for x in list_synon:
        try:
            x = x.decode('utf-8')
        except UnicodeDecodeError:
            x = None
    # Add to dictionary
    [d_rep[id_country].append(l) for l in list_synon]

# Return countries (keys) in article


def check_countries(text, dict):
    results = []
    for k in dict.keys():
        # print k
        if any(words in text for words in dict[k]):
            results.append(k)
    results = list(set(results))
    return results

# Read table countries


def read_countries(file):
    import re
    with open(file, 'rU') as f:
        list_countries = []
        for line in f:
            # Remove all parenthesis and their content
            regex = re.compile('\(.+?\)')
            countries = regex.sub('', line.strip())
            # Remove non-informative character
            regex = re.compile("_")
            countries = regex.sub('', countries)
            # Remove quotes
            regex = re.compile('"')
            countries = regex.sub('', countries)
            # Remove spaces before commas
            regex = re.compile(" *, *")
            countries = regex.sub(',', countries)
            # Filtering empty fields
            list_countries.append(
                ';'.join([x.strip()
                          for x in filter(None, countries.split(';'))]))
        return list_countries


def country_list_to_dict(country_list):
    ''' Function to convert country list to country dictionary.
    '''

    split_record = [l.split(';') for l in country_list]
    country_common_name = [record[0] for record in split_record]
    country_synom_name = [remove_non_ascii(record[1].split(','))
                          for record in split_record]

    country_dict = defaultdict(list,
                               {country[0]: country[1]
                                for country in zip(
                                   country_common_name, country_synom_name)})
    return country_dict


def remove_non_ascii(string_list):
    ''' Function to remove non-ascii names from a list.
    '''

    sanitised_list = list()
    for string in string_list:
        try:
            ascii_string = string.decode('ascii')
            sanitised_list.append(ascii_string)
        except UnicodeDecodeError:
            pass
    return sanitised_list


def geotag_article(articles, country_dict):
    ''' Append geographical location to existing articles.
    '''

    geotagged_articles = []
    for article in articles:
        geotagged_articles.append(
            {
                'id': article['id'],
                'geo_tag': remove_non_ascii(
                    check_countries(article['article'], country_dict)),
            })

    flattened_articles = flatten_geotagged_article(geotagged_articles)
    return pd.DataFrame(flattened_articles)


def flatten_geotagged_article(articles):
    flattened_list = []
    for article in articles:
        tags = article.get('geo_tag')
        number_of_tag = len(tags)
        for i in range(number_of_tag):
            flattened_list.append({'id': article.get('id'),
                                   'geo_tag': tags[i].decode('ascii')})
    return flattened_list
