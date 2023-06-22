import random
from pathlib import Path

import pandas as pd

from .tw_configuration import config


class CollectError(Exception):
    pass


class Collect:
    def __init__(self, file_path, n_tweets=10):
        self.file_path = file_path
        self.n_tweets = n_tweets

        data_path = Path("/data") / Path(file_path)
        self.tweets = pd.read_csv(data_path)

    def __call__(self):
        return self.tweets.sample(random.randint(1, self.n_tweets)).to_json(
            orient="records"
        )


collect = Collect(config.tweets_file_path)
