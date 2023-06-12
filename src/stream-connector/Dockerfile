FROM confluentinc/cp-kafka-connect:7.1.0-1-ubi8

ENV CONNECT_PLUGIN_PATH /usr/share/java,/usr/share/confluent-hub-components

RUN confluent-hub install --no-prompt jcustenborder/kafka-connect-spooldir:2.0.65
COPY input-spooldir.json .
COPY install.sh .

CMD ["/bin/sh", "install.sh"]