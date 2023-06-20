![pissed-off-people-on-twitter](./doc/img/twitter-logo-transformed.png "pissed-off-people-on-twitter")

Based on: https://huggingface.co/blog/sentiment-analysis-python

# Architecture (c4 model diagram - System context)

![arch-diagram](./doc/img/arch-diagram.system_context.v2.drawio.png "arch-diagram")

# REST connector

https://stackoverflow.com/questions/60617182/send-data-from-rest-api-to-kafka

Changed pom.xml from [REST connect plugin](https://github.com/llofberg/kafka-connect-rest/tree/master). URL from confluent repo was wrong

# TODO
- Kafka connect elastic sink
- Terminar los diagramas de la arquitectura
- Documentacion

# Apuntes

- Especificar que he utilizado y arreglado el plugin del REST connector (cambiando el pom.xml)
- Especificar necesario fichero de tweets para el conector API
- Detallar la arquitectura