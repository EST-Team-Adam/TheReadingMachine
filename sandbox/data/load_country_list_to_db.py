

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


country_list = read_countries('list_of_countries.csv')
