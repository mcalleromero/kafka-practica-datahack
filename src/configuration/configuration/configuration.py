import logging
import os
import pkgutil
from pathlib import Path

import yaml

FORMAT = "%(asctime)s  %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger("configuration")


class ConfigurationError(Exception):
    pass


class Configuration:
    DEFAULT_CONFIG_PATH = "config.yaml"

    def __init__(self, extra_config_paths=None):
        default_configuration = pkgutil.get_data(__name__, self.DEFAULT_CONFIG_PATH)
        self._configuration = yaml.safe_load(default_configuration)
        self._config_paths = set()
        self._extra_config_paths = os.environ.get("CONFIG_PATHS", None)
        if self._extra_config_paths is None:
            self._extra_config_paths = extra_config_paths
        if self._extra_config_paths is not None:
            self._config_paths.update(self._extra_config_paths.split(","))
        for config_path in self._config_paths:
            try:
                self._load_config(Path(config_path))
            except ConfigurationError:
                continue

    def _load_config(self, config_path):
        if not os.path.exists(config_path):
            warning_message = f"Configuration file '{config_path}' does not exist"
            logger.warning(warning_message)
            raise ConfigurationError(warning_message)
        with open(config_path, "r") as config:
            try:
                self._configuration.update(yaml.safe_load(config))
            except yaml.YAMLError:
                warning_message = (
                    f"Error while loading configuration yaml file: {config_path}"
                )
                logger.warning(warning_message)
                raise ConfigurationError(warning_message)

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
    def log_level(self):
        return self.get_config_param("LOG_LEVEL", "general", "log_level", str)

    @property
    def default_timezone(self):
        return self.get_config_param(
            "DEFAULT_TIMEZONE", "general", "default_timezone", str
        )
