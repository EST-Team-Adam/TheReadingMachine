from sqlalchemy import create_engine
import pandas as pd

# Initiate file names and parameters
file_prefix = "data/amis_articles"
version = '27_11_2016'
input_file_name = '{0}_{1}_indexed.jsonl'.format(file_prefix, version)
output_file_name = '{0}_{1}_processed.jsonl'.format(file_prefix, version)
test_sample_size = 1000

# Database configuration
dialect = 'mysql'
user = 'trm'
password = 'thereadingmachine'
host = 'thereadingmachine.cxwhnvtnzzyv.ap-northeast-1.rds.amazonaws.com'
port = '3306'
database = 'thereadingmachine'

database_url = '{}://{}:{}@{}:{}/{}'.format(
    dialect, user, password, host, port, database)
engine = create_engine(database_url)

# load the data


def read_jsonl(input_file_name, **kwargs):
    print "Reading data from '{0}' ...".format(input_file_name)
    articles = []
    with open(input_file_name) as f:
        if 'size' in kwargs:
            subset = islice(f, kwargs['size'])
            for line in subset:
                articles.append(json.loads(line))
        else:
            for line in f:
                articles.append(json.loads(line))
    return articles


# Read the data
articles = read_jsonl(input_file_name)
