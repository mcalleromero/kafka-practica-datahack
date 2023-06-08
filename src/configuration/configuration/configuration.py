import logging
import os
from pathlib import Path

import yaml

FORMAT = "%(asctime)s  %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger("configuration")


class ConfigurationError(Exception):
    pass


class Configuration:
    def __init__(self, config_path="config.yaml"):
        self._config_path = os.environ.get("CONFIG_PATH", None)
        if self._config_path is None:
            self._config_path = Path(config_path)
        self._load_config()

    def _load_config(self):
        with open(self._config_path, "r") as config:
            try:
                self._configuration = yaml.safe_load(config)
            except yaml.YAMLError as exc:
                logger.error("Error while loading configuration yaml file")

    def get_config_param(self, section: str, key: str, type=str):
        return type(self._configuration.get(section).get(key))

    @property
    def bootstrap_host(self):
        return self.get_config_param("bootstrap", "host", str)

    @property
    def bootstrap_port(self):
        return self.get_config_param("bootstrap", "port", int)

    @property
    def input_topic(self):
        return self.get_config_param("topics", "input_topic", str)

    @property
    def output_topic(self):
        return self.get_config_param("topics", "output_topic", str)

    @property
    def log_level(self):
        return self.get_config_param("general", "log_level", str)
