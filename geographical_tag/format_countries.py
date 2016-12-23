import re
import sys
import os
from collections import defaultdict

d = defaultdict()

input_file_name = sys.argv[1]
output_file_name = os.path.splitext(input_file_name)
print output_file_name

with open(input_file_name, 'rU') as f:
    for line in f:
        ## Remove all parenthesis and their content
        regex = re.compile('\(.+?\)')
        ## Remove non-informative character
        regex1 = re.compile("_")
        ## Remove quotes
        regex2 = re.compile('"')
        ## Remove spaces before commas
        regex3 = re.compile(" *, *")
        output = regex.sub('', line.strip())
        output = regex1.sub('', output)
        output = regex2.sub('', output)
        output = regex3.sub(',', output)
        print(';'.join([x.strip() for x in filter(None, output.split(';'))]))
