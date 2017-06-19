import pandas as pd
import sys

from twitter import TwitterHTTPError

def get_timeline(screen_name, t):

    all_tweets = []
    new_tweets = t.statuses.user_timeline(screen_name=screen_name, count=200)

    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:

        # save most recent tweets
        all_tweets.extend(new_tweets)

        # update the id of the oldest tweet less one
        oldest = all_tweets[-1]['id'] - 1

        print "getting tweets before https://twitter.com/{0}/status/{1}".format(screen_name, oldest)

        # all subsequent requests use the max_id param to prevent duplicates
        new_tweets = t.statuses.user_timeline(screen_name=screen_name, count=200, max_id=oldest)

        print "...{0} tweets downloaded so far [{1}]".format(len(all_tweets), screen_name)

    tweets = pd.DataFrame([{'link': 'https://twitter.com/' + screen_name,
                   'title': tweet['id'],
                   'date': tweet['created_at'],
                   'article': tweet['text'],
                  } for tweet in all_tweets])
    return tweets


def get_timelines(followers, t):
    all_tweets = pd.DataFrame()
    for screen_name in followers:
        try:
            tweets = get_timeline(screen_name, t)
            if len(tweets)>0:
                all_tweets = all_tweets.append(tweets)
        except TwitterHTTPError:
            print >> sys.stderr, "No Response for id ", screen_name
    all_tweets['source'] = "twitter"
    #all_tweets['created_at'] = pd.to_datetime(all_tweets['created_at'])
    all_tweets['article'] = all_tweets['article'].apply(lambda x: x.encode('utf-8'))
    #all_tweets = all_tweets.set_index(all_tweets.id)
    return all_tweets
