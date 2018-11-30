import pandas as pd
import controller as ctr
import thereadingmachine.environment as env
from oauth_setup import oauth_login

# Read twitter file
followers_list = pd.read_csv(env.twitter_file)['Screen Name'].tolist()

# Autenticate API
tt = oauth_login()

# Twitter articles
twitter_output = ctr.get_timelines(
    followers=followers_list, t=tt)


# Save output file
flattened_article_df = pd.DataFrame(twitter_output)
flattened_article_df.to_sql(con=env.engine, name=env.raw_tweet_table,
                            index=False, if_exists='replace',
                            dtype=env.raw_tweet_field_type)
