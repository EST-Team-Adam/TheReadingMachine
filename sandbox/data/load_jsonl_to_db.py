import json
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from itertools import islice


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


article = read_jsonl('amis_articles_27_11_2016.jsonl')
engine = create_engine('sqlite:///the_reading_machine.db')

field_type = {
    'id': sqlalchemy.types.Integer(),
    'date': sqlalchemy.types.Date(),
    'source': sqlalchemy.types.NVARCHAR(length=250),
    'link': sqlalchemy.types.NVARCHAR(length=255),
    'title': sqlalchemy.types.NVARCHAR(length=255),
    'article': sqlalchemy.types.Text()
}

# Sort and add index
article_df = pd.DataFrame(article)
article_df['date'] = pd.to_datetime(article_df['date'])
article_df.sort_values(['date'], ascending=[1], inplace=True)
article_df['id'] = range(1, article_df.shape[0] + 1)

# Save the data to database
article_df.to_sql(con=engine, name='RawArticle', if_exists='replace',
                  dtype=field_type, index=False)
