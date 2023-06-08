import os
import time

import tweepy


class CollectError(Exception):
    pass


class Collect:
    def __init__(self):
        api_key = os.environ.get("API_KEY", None)
        if api_key is None:
            raise CollectError("API_KEY not defined")
        api_secret = os.environ.get("API_SECRET_KEY", None)
        if api_secret is None:
            raise CollectError("API_SECRET_KEY not defined")

        auth = tweepy.AppAuthHandler(api_key, api_secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)

    def __limit_handled(self, cursor):
        while True:
            yield cursor.next()
            # try:
            # except tweepy.errors.TweepyException:
            #     print("Reached rate limite. Sleeping for >15 minutes")
            #     time.sleep(15 * 61)
            # except StopIteration:
            #     break

    def search(self, query, count=10):
        query = f"{query}-filter:retweets"

        search = self.__limit_handled(
            tweepy.Cursor(
                self.api.search_tweets,
                q=query,
                tweet_mode="extended",
                lang="en",
                result_type="recent",
            ).items(count)
        )

        for x in search:
            import pdb

            pdb.set_trace()

        return search

    def save(self, path, query, count=10):
        tweets = self.search(query, count)
        with open(path, "w+") as file:
            file.write(tweets)

    def __call__(self, query, count):
        self.search(query, count)
