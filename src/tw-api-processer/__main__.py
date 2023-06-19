import ast
import json
import logging
import time
from datetime import datetime

import kafka.errors
import requests
from confluent_kafka.schema_registry import Schema, SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.schema_registry.error import SchemaRegistryError
from confluent_kafka.serialization import MessageField, SerializationContext
from kafka import KafkaConsumer, KafkaProducer

from .processer_configuration import ProcesserConfiguration

FORMAT = "%(asctime)s  %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger("configuration")


def connect_to_kafka(retries=3):
    bootstrap_servers = f"{config.bootstrap_host}:{config.bootstrap_port}"
    for _ in range(retries):
        try:
            consumer = KafkaConsumer(
                config.input_topic,
                bootstrap_servers=[bootstrap_servers],
                group_id="transformer",
            )
            producer = KafkaProducer(bootstrap_servers=[bootstrap_servers])
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


def init_serializer(schema_registry):
    try:
        value_schema = schema_registry.get_latest_version("stream-tweets-value").schema
    except SchemaRegistryError:
        schema_str = config.output_schema
        value_schema = Schema(schema_str=schema_str, schema_type="AVRO")
        schema_registry.register_schema(
            subject_name="stream-tweets-value", schema=value_schema
        )
    serializer = AvroSerializer(schema_registry, value_schema)
    context = SerializationContext(topic=config.output_topic, field=MessageField.VALUE)

    return serializer, context


if __name__ == "__main__":
    config = ProcesserConfiguration()
    logger.setLevel(config.log_level)
    consumer, producer = connect_to_kafka(retries=3)

    schema_registry = connect_to_schema_registry(retries=3)
    serializer = None

    for msg in consumer:
        if serializer is None:
            serializer, context = init_serializer(schema_registry)

        # AVRO adds some bytes by default, that is why [7:] is needed
        messages = json.loads(ast.literal_eval(msg.value[7:].decode("utf-8")))
        for message in messages:
            logger.debug(
                "%s:%d:%d: value=%s"
                % (
                    msg.topic,
                    msg.partition,
                    msg.offset,
                    message,
                )
            )

            producer.send(
                config.output_topic,
                key=json.dumps(message["id"]).encode("utf-8"),
                value=serializer(message, context),
            )
            logger.debug("Sent tweet: %s" % (message))

        consumer.commit()
