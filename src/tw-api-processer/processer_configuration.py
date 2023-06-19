from configuration import Configuration


class ProcesserConfiguration(Configuration):
    @property
    def input_topic(self):
        return self.get_config_param("INPUT_TOPIC", "topics", "input_topic", str)

    @property
    def output_topic(self):
        return self.get_config_param("OUTPUT_TOPIC", "topics", "output_topic", str)

    @property
    def output_schema(self):
        return self.get_config_param("OUTPUT_SCHEMA", "schemas", "output_schema", str)
