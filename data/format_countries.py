from thereadingmachine.geotagging import make_dict_countries
from thereadingmachine.geotagging import check_countries
import sys
from collections import defaultdict


# Reading data
# --------------------------------------------------

# Initiate file names and parameters
file_prefix = "data/amis_articles"
version = '27_11_2016'
input_file_name = '{0}_{1}_indexed.jsonl'.format(file_prefix, version)
output_file_name = '{0}_{1}_geotagged.jsonl'.format(file_prefix, version)
test_sample_size = 1000

# Getting file of list of countries 

# Read the data
articles = read_jsonl(input_file_name)

input_file_name = sys.argv[1]

list_countries = []
d_countries = defaultdict()

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

#located_keywords = set([word for word in keywords if word in text])

tt = check_countries(text1, d_countries)
tt1 = check_countries(text2, d_countries)


a = [key for key in d_countries.keys() if any(words in text1 for words in d_countries[key])]

t = 1





#def readGene(f,g_repository,gname = "",  samples_idx = 0):
#    try:
#        genename = ""
#        oldgene = ""
#        for lraw in f:
#            lraw = lraw.strip()
#            l = lraw.split('\t') #######tab separated                                                                                                                      
#            if len(l)<3:
#              l = lraw.strip().split(',') #######tab separated                                                                                                             
#            for i in range(0,samples_idx):
#              l[i]=l[i].replace("-","|") ##bloody csv corrections for annotations                                                                                          
#            genename = l[4].split('(')[0]
#
#            if '-' not in genename and (genename == gname or gname == ""):
#                if len(l)>1:
#                  g_repository[genename].append(l)
#    except:
#        raise StopIteration
#    return g_repository
