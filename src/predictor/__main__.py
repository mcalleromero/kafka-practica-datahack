import ast
import json
import logging
import time

import kafka.errors
from kafka import KafkaConsumer, KafkaProducer

from configuration import Configuration

FORMAT = "%(asctime)s  %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger("configuration")


from .sentiment import Predictor


class TweetError(Exception):
    pass


class Tweet:
    def __init__(self, message: dict):
        self.sentiment = {}

        try:
            self.user = message["user"]
        except KeyError:
            self.user = "undefined"

        try:
            self.content = message["tweet"]
        except KeyError:
            raise TweetError("Tweet content not found")

        try:
            # TODO: Format date
            self.date = message["date"]
        except KeyError:
            raise TweetError("Tweet date creation not found")

    def to_dict(self):
        return {
            "user": self.user,
            "content": self.content,
            "date": self.date,
            "sentiment": self.sentiment,
        }


def connect_to_kafka(retries=3):
    bootstrap_servers = f"{config.bootstrap_host}:{config.bootstrap_port}"
    for _ in range(retries):
        try:
            consumer = KafkaConsumer(
                config.input_topic,
                bootstrap_servers=[bootstrap_servers],
                group_id="predictor",
            )
            producer = KafkaProducer(
                bootstrap_servers=[bootstrap_servers],
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
        except kafka.errors.NoBrokersAvailable:
            time.sleep(10)
            continue
        else:
            break
    else:
        raise kafka.errors.NoBrokersAvailable()

    return consumer, producer


if __name__ == "__main__":
    config = Configuration(config_path="./configuration/config.yaml")
    logger.setLevel(config.log_level)
    consumer, producer = connect_to_kafka(retries=3)
    predictor = Predictor()

    # Tweets must be formatted
    # value: {
    #     "date": <date>,
    #     "user": <user>,
    #     "content": <content>
    # }
    for msg in consumer:
        message = msg.value.decode("utf8")
        try:
            message = ast.literal_eval(message)
            message = message["payload"]
        except (ValueError, SyntaxError):
            raise TweetError("Tweet is schemaless or is not JSON formatted")

        logger.debug(
            "%s:%d:%d: value=%s"
            % (
                msg.topic,
                msg.partition,
                msg.offset,
                message,
            )
        )

        try:
            tweet = Tweet(message=message)
        except TweetError as e:
            logger.debug("Error with tweet: %s:%s" % (message, e))
            continue

        _, result = predictor.predict(tweet.content)

        tweet.sentiment = result
        producer.send(config.output_topic, tweet.to_dict())
        logger.debug("Sent tweet: %s" % (tweet.to_dict()))

        consumer.commit()
