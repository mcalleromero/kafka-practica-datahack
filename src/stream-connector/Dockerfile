FROM maven:3.8.2-jdk-11 AS mvn_build

WORKDIR /opt

COPY kafka-connect-rest/ .

RUN mvn clean install

FROM confluentinc/cp-kafka-connect:7.3.0

COPY --from=mvn_build /opt/kafka-connect-rest-plugin/target/kafka-connect-rest-plugin-*-shaded.jar /jars/
COPY --from=mvn_build /opt/kafka-connect-transform-from-json/kafka-connect-transform-from-json-plugin/target/kafka-connect-transform-from-json-plugin-*-shaded.jar /jars/
COPY --from=mvn_build /opt/kafka-connect-transform-add-headers/target/kafka-connect-transform-add-headers-*-shaded.jar /jars/
COPY --from=mvn_build /opt/kafka-connect-transform-velocity-eval/target/kafka-connect-transform-velocity-eval-*-shaded.jar /jars/

ENV CONNECT_PLUGIN_PATH /usr/share/java,/usr/share/confluent-hub-components,/jars

RUN confluent-hub install --no-prompt jcustenborder/kafka-connect-spooldir:2.0.65
COPY input-spooldir.json .
COPY input-rest.json .
COPY install.sh .

CMD ["/bin/sh", "install.sh"]