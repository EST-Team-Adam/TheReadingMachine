import pandas as pd
import os
import sqlalchemy
import controller as ctr
from sqlalchemy import create_engine
from oauth_setup import oauth_login


# Configuration
data_dir = os.environ['DATA_DIR']
# source_data_table = 'RawArticle'
target_data_table = 'RawTweets'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))
twitter_file = '{0}/Free_Twitter_Followers_Report_on_amis.csv'.format(data_dir)

# Read twitter file
followers_list = pd.read_csv(twitter_file)['Screen Name'].tolist()

# Autenticate API
tt = oauth_login()

# Twitter articles
twitter_output = ctr.get_timelines(
    followers=followers_list, t=tt)


'article', 'date', 'link', 'title', 'source'
# Save output file
field_type = {'article': sqlalchemy.types.NVARCHAR(length=255),
              'date': sqlalchemy.types.NVARCHAR(lenght=255),
              'link': sqlaclchemy.types.NVARCHAR(lenght=255),
              'title': sqlaclchemy.types.NVARCHAR(lenght=255),
              'source': sqlalchemy.types.NVARCHAR(length=255)}
flattened_article_df = pd.DataFrame(twitter_output)
flattened_article_df.to_sql(con=engine, name=target_data_table, index=False,
                            if_exists='replace',
                            dtype=field_type)