from configuration import Configuration


class TwitterConfiguration(Configuration):
    @property
    def tweets_file_path(self):
        return self.get_config_param("TWEETS_FILE_PATH", "tweets", "path", str)


config = TwitterConfiguration()
