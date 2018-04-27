__author__ = 'mrpozzi'

import os
import thereadingmachine.environment as env
from twitter import Twitter
from twitter.oauth import OAuth, read_token_file


class Credentials:
    """
    Go to http://twitter.com/apps/new to create an app and get these items
    See also http://dev.twitter.com/pages/oauth_single_token
    """

    def __init__(self):
        self.APP_KEY = ""
        self.APP_SECRET = ""
        self.OAUTH_TOKEN = ""
        self.OAUTH_TOKEN_SECRET = ""

    def read_from_file(self, file_name=os.path.expanduser(env.data_dir) + "/credentials.txt"):
        credentials = dict()
        credentials_file = file(file_name)
        for line in file.readlines(credentials_file):
            token = line.split("=")
            credentials[token[0]] = token[1].replace("\n", "")
        self.APP_KEY = credentials["APP_KEY"]
        self.APP_SECRET = credentials["APP_SECRET"]
        self.OAUTH_TOKEN = credentials["OAUTH_TOKEN"]
        self.OAUTH_TOKEN_SECRET = credentials["OAUTH_TOKEN_SECRET"]


def oauth_login(token_file=os.path.expanduser(env.data_dir) + "/credentials.txt"):

    credentials = Credentials()
    credentials.read_from_file(token_file)

    return Twitter(auth=OAuth(credentials.OAUTH_TOKEN, credentials.OAUTH_TOKEN_SECRET,
                              credentials.APP_KEY, credentials.APP_SECRET))  # , retry=True)


if __name__ == '__main__':

    oauth_login()
