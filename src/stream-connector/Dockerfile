FROM confluentinc/cp-kafka-connect:7.4.0

WORKDIR /opt
ENV CONNECT_PLUGIN_PATH /usr/share/java,/usr/share/confluent-hub-components

RUN confluent-hub install --no-prompt jcustenborder/kafka-connect-spooldir:2.0.65
COPY input-spooldir.json .
# RUN curl -d @"input-spooldir.json" -H "Content-Type: application/json" -X POST http://localhost:8083/connectors

CMD /etc/confluent/docker/run