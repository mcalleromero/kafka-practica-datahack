import json
import logging
import time
from datetime import datetime

import kafka.errors
import pytz
import requests
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import MessageField, SerializationContext
from kafka import KafkaConsumer, KafkaProducer

from .predictor_configuration import PredictorConfiguration
from .sentiment import Predictor

FORMAT = "%(asctime)s  %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger("configuration")


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
            date = message["date"]
            self.date = self._format_date(date)
        except KeyError:
            raise TweetError("Tweet date creation not found")

    def _format_date(self, date: str) -> datetime:
        formatted_date = (
            datetime.strptime(date, "%a %b %d %H:%M:%S PDT %Y")
            .replace(tzinfo=pytz.timezone(config.default_timezone))
            .astimezone(pytz.utc)
        )

        return formatted_date

    def to_dict(self):
        return {
            "user": self.user,
            "content": self.content,
            "date": self.date.strftime("%Y-%m-%dT%H:%M:%SZ"),
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


def connect_to_schema_registry(retries=3):
    schema_registry_server = (
        f"http://{config.schema_registry_host}:{config.schema_registry_port}"
    )
    for _ in range(retries):
        try:
            schema_registry = SchemaRegistryClient({"url": schema_registry_server})
        except requests.exceptions.ConnectionError:
            time.sleep(10)
            continue
        else:
            break
    else:
        raise requests.exceptions.ConnectionError()

    return schema_registry


if __name__ == "__main__":
    config = PredictorConfiguration()
    logger.setLevel(config.log_level)
    consumer, producer = connect_to_kafka(retries=3)
    predictor = Predictor()

    schema_registry = connect_to_schema_registry(retries=3)
    deserializer = None

    for msg in consumer:
        if deserializer is None:
            value_schema = schema_registry.get_latest_version(
                "stream-tweets-value"
            ).schema
            deserializer = AvroDeserializer(schema_registry, value_schema)
            context = SerializationContext(
                topic=config.input_topic, field=MessageField.VALUE
            )

        message = deserializer(msg.value, context)

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
