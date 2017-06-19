import pandas as pd
import json
import sys
import sqlalchemy
import controller as ctr
from sqlalchemy import create_engine
from twitter import TwitterHTTPError
from oauth_setup import oauth_login
from twitter_utils import get_timelines


# Configuration
data_dir = os.environ['DATA_DIR']
# source_data_table = 'RawArticle'
target_data_table = 'RawArticle'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))
twitter_file = '{0}/Free_Twitter_Followers_Report_on_amis.csv'.format(data_dir)

# Read twitter file
followers_list = pd.read_csv(twitter_file)['Screen Name'].tolist()

# Autenticate API
tt = oauth_login()

# Geotag articles
twitter_output = ctr.get_timelines(
    followers=follower_list, t = tt)

# Output test
output_file = data_directory + "twitter_timelines.jsonl"
all_tweets.apply(lambda x: json.dumps(dict(x)), 1).to_csv(output_file)

# TODO: define output
# Save output file
field_type = {'id': sqlalchemy.types.Integer(),
              'geo_tag': sqlalchemy.types.NVARCHAR(length=255)}
flattened_article_df = pd.DataFrame(geotagged_articles)
flattened_article_df.to_sql(con=engine, name=target_data_table, index=False,
                            if_exists='replace',
                            dtype=field_type)






