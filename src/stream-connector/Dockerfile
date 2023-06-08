FROM confluentinc/cp-kafka-connect:7.4.0

WORKDIR /opt
ENV CONNECT_PLUGIN_PATH /usr/share/java,/usr/share/confluent-hub-components

RUN confluent-hub install --no-prompt jcustenborder/kafka-connect-spooldir:2.0.65
COPY input-spooldir.json .
COPY install-connector.sh .

CMD bash -c install-connector.sh