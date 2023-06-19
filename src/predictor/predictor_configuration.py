from configuration import Configuration


class PredictorConfiguration(Configuration):
    @property
    def input_topic(self):
        return self.get_config_param("INPUT_TOPIC", "topics", "input_topic", str)

    @property
    def output_topic(self):
        return self.get_config_param("OUTPUT_TOPIC", "topics", "output_topic", str)
