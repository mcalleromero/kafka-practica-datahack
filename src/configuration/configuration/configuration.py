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
        if not os.path.exists(self._config_path):
            return
        with open(self._config_path, "r") as config:
            try:
                self._configuration = yaml.safe_load(config)
            except yaml.YAMLError as exc:
                logger.error("Error while loading configuration yaml file")

    def get_config_param(self, env_var: str, section: str, key: str, type=str):
        env_var = os.environ.get(env_var, None)
        if env_var:
            return type(env_var)

        return type(self._configuration.get(section).get(key))

    @property
    def bootstrap_host(self):
        return self.get_config_param("BOOTSTRAP_HOST", "bootstrap", "host", str)

    @property
    def bootstrap_port(self):
        return self.get_config_param("BOOTSTRAP_PORT", "bootstrap", "port", int)

    @property
    def schema_registry_host(self):
        return self.get_config_param(
            "SCHEMA_REGISTRY_HOST", "schema_registry", "host", str
        )

    @property
    def schema_registry_port(self):
        return self.get_config_param(
            "SCHEMA_REGISTRY_PORT", "schema_registry", "port", int
        )

    @property
    def input_topic(self):
        return self.get_config_param("INPUT_TOPIC", "topics", "input_topic", str)

    @property
    def output_topic(self):
        return self.get_config_param("OUTPUT_TOPIC", "topics", "output_topic", str)

    @property
    def log_level(self):
        return self.get_config_param("LOG_LEVEL", "general", "log_level", str)

    @property
    def default_timezone(self):
        return self.get_config_param(
            "DEFAULT_TIMEZONE", "general", "default_timezone", str
        )
