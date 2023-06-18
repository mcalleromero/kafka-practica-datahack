import os
import random
import time


class CollectError(Exception):
    pass


class Collect:
    def __init__(self, file_path, n_tweets=1, s_between_tweets=3, rand_time=True):
        self.file_path = file_path
        self.n_tweets = n_tweets
        self.s_between_tweets = s_between_tweets
        self.rand_time = rand_time

        with open(self.file_path, "r") as file:
            self._lines = file.readlines()

    def tweets(self):
        while True:
            if self.rand_time:
                seconds_to_wait = random.randint(self.s_between_tweets)

    def __call__(self, query, count):
        self.search(query, count)
