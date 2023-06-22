# Despliegue

## Requisitos previos

- Conexión a internet
- Docker
- Docker-compose

Comando de despliegue de la aplicación:

```bash
$ docker-compose --env-file=run.env up -d
```

Comando para terminar la aplicación:

```bash
$ docker-compose --env-file=run.env down
```

# Configuración

Aparte de la configuración de usuario ([Manual de usuario](./doc/manual_uso.md)), es posible configurar otros parámetros de la aplicación. Principalmente, se pueden modificar los parámetros de configuración del stack de Kafka, detallados en el fichero _server.env_. Estos parámetros sirven para integrar todos los componentes de la aplicación. La modificación de estos parámetrso podría implicar un comportamiento incorrecto de la aplicación. Los parámetros de configuración de cada componente se pueden revisar en la [documentación oficial](https://docs.confluent.io/platform/current/installation/docker/config-reference.html) de las imágenes del stack de Kafka.

También se pueden modificar los parámetros de configuración de los servicios construídos internamente:

- _General_. Fichero `config.yaml` del directorio `configuration`. Los parámetros de configuración por defecto pueden ser sobreescritos en cualquier microservicio, sin embargo, se debe sobreescribir una sección con todos los niveles, sino algunos valores serán _null_.
    - **LOG_LEVEL** o **general.log_level**: nivel de logs del sistema. Por defecto, INFO; si se quiere hacer troubleshooting del sistema se debe establecer a DEBUG. Si la carga de logs es demasiado alta, se recomienda establecer en WARNING.
    - **DEFAULT_TIMEZONE** o **general.default_timezone**: zona de timestamp por defecto de los mensajes recibidos. Este parámetro es utilizado para convertir las fechas y horas a UTC internamente.
    - **BOOTSTRAP_HOST y BOOTSTRAP_PORT** o **bootstrap.host y bootstrap.port**: configuración para la conexión con clúster de Kafka.
    - **SCHEMA_REGISTRY_HOST y SCHEMA_REGISTRY_PORT** o **schema_registry.host y schema_registry.port**: configuración para la conexión con contenedor de Schema Registry.
- _Predictor_. Fichero `configuration.yaml` del directior `predictor`.
    - **INPUT_TOPIC** o **topics.input_topic**: topic de entrada del predictor.
    - **OUTPUT_TOPIC** o **topics.output_topic**: topic de salida del predictor.
- _Twitter API_. Por defecto, variable de entorno.
    - **TWEETS_FILE_PATH** o **tweets.path**: Nombre del fichero donde se encuentra el fichero de tweets.
- _Twitter API Processer_. Fichero `configuration.yaml` del directior `tw-api-processer`.
    - **INPUT_TOPIC** o **topics.input_topic**: topic de entrada del predictor.
    - **OUTPUT_TOPIC** o **topics.output_topic**: topic de salida del predictor.
    - **OUTPUT_SCHEMA** o **schemas.output_schema**: esquema de los mensajes que se escriben en el output topic. Debe ser compatible con el esquema de la configuración del conector de ficheros.

## Configuración conectores

La configuración de los tres conectores se detalla en formato JSON en el directorio `src > stream-connector`.

## REST

El fichero de configuración del conector REST de Kafka Connect se llama `input-rest.json`. Con esta configuración podemos modificar el intervalo de milisegundos entre llamada y llamada al endpoint, `rest.source.poll.interval.ms`. Podemos modificar, también, los parámetros del endpoint de conexión para la extracción de tweets: `rest.source.method`, `rest.source.headers` y `rest.source.url`. Finalmente, podemos modificar el topic de destino, `rest.source.destination.topics`.

```json
{
    "name": "RESTSource",
    "config": {
        "connector.class": "com.tm.kafka.connect.rest.RestSourceConnector",
        "rest.source.poll.interval.ms": "10000",
        "rest.source.method": "GET",
        "rest.source.headers": "Content-Type:application/json,Accept:application/json",
        "rest.source.url": "http://twitter-api:8099/tweets",
        "rest.source.topic.selector": "com.tm.kafka.connect.rest.selector.SimpleTopicSelector",
        "rest.source.destination.topics": "stream-tweets-api"
    }
}
```

## Ficheros

El fichero de configuración del conector de ficheros de Kafka Connect se llama `input-spooldir.json`. Podemos modificar la ruta de los ficheros que se leen con `input.path`, sin embargo, esta ruta es la ruta interna del contenedor y sería necesario modificar también el mount link que existe con el volumen de docker. Este mismo proceso es igual para las rutas de los ficheros erróneos y los ficheros que han sido procesados, `error.path` y `finished.path`, respectivamente. También se permite modificar el patrón de lectura de ficheros, por defecto se permite la lectura de cualquier fichero que siga la nomenclatura `tweets_<anything>.csv` mediante el patrón `^tweets_.*\\.csv` especificado en el parámetro de configuración `input.file.pattern`. También se pueden configurar otros parámetros que no están directamente relacionados con los ficheros:

- `halt.on.error`: Controla el comportamiento del conector en caso de error. Si el parámetro se configura a false, no para la ejecución y sigue procesando el resto de ficheros.
- `csv.first.row.as.header`: Si los ficheros carecen de cabecera, este parámetro se debe configurar a false. Por defecto, true, pues se espera que los ficheros de lectura contengan una cabecera descriptiva de las columnas.
- `csv.escape.char`: Caracter de escape. Por defecto es el carácter nulo para que ningún caracter de los tweets sea escapado. Puede ocurrir que algunos caracteres escapen las dobles comillas que señalan las delimitaciones de los textos.
- `schema.generation.enabled`: Indica si se quiere generar un esquema de los datos recibidos.
- `key.schema`: Esquema en formato JSON (string) del identificador de cada fila del CSV.
- `value.schema`: Esquema en formato JSON (string) de los valores de cada fila del CSV.
- `topic`: Topic de escritura del conector.

```json
{
    "name": "CsvSpoolDir",
    "config": {
        "tasks.max": "1",
        "connector.class": "com.github.jcustenborder.kafka.connect.spooldir.SpoolDirCsvSourceConnector",
        "input.path": "/data/input",
        "input.file.pattern": "^tweets_.*\\.csv",
        "error.path": "/data/error",
        "finished.path": "/data/processed",
        "halt.on.error": "false",
        "topic": "stream-tweets",
        "csv.first.row.as.header": "true",
        "csv.escape.char": 0,
        "schema.generation.enabled": "true",
        "key.schema": "{\n    \"name\":\"stream.tweets.key.schema\",\n    \"type\":\"STRUCT\",\n    \"isOptional\":false,\n    \"fieldSchemas\":{\n       \"id\":{\n          \"type\":\"INT64\",\n          \"isOptional\":false\n       }\n    }\n }",
        "value.schema": "{\n   \"name\":\"stream.tweets.value.schema\",\n   \"type\":\"STRUCT\",\n   \"isOptional\":false,\n   \"fieldSchemas\":{\n      \"id\":{\n         \"type\":\"INT64\",\n         \"isOptional\":false\n      },\n      \"user\":{\n         \"type\":\"STRING\",\n         \"isOptional\":true\n      },\n      \"date\":{\n         \"type\":\"STRING\",\n         \"isOptional\":true\n      },\n      \"tweet\":{\n         \"type\":\"STRING\",\n         \"isOptional\":true\n      }\n   }\n}"
    }
}
```

## ElasticSearch

El fichero de configuración del conector Sink de ElasticSearch de Kafka Connect se llama `output-elasticsearch.json`. Se pueden consultar todos los parámetros de configuración en la [documentación oficial del conector](https://docs.confluent.io/kafka-connectors/elasticsearch/current/configuration_options.html). Los parámetros de configuración que podemos modificar son:

- `topics`: Topic de lectura del conector.
- `connection.url`: URL de conexión con Elasticsearch.
- `key.converter`: Conversor de la key de los mensajes.
- `value.converter`: Conversor de los valores de los mensajes. Por defecto Json para que Elasticsearch pueda generar mappings automáticamente.
- `value.converter.schemas.enable`: Indica que no se reciba el esquema del mensaje, para poder generar el mapping desde Elasticsearch.
- `schema.ignore`: Ignora el esquema con el objetivo de generar un mapping propio de Elasticsearch. `value.converter.schemas.enable` debe ser false, sino genera un error por conflicto pues estaría intentando utilizar un esquema y en el conversor se ha especificado que no se reciba el esquema de los mensajes.

```json
{
    "name": "ElasticSearchSink",
    "config": {
        "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
        "tasks.max": "1",
        "topics": "stream-sentiment",
        "connection.url": "http://elasticsearch:9200",
        "schema.ignore": true,
        "type.name": "_doc",
        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
        "value.converter": "org.apache.kafka.connect.json.JsonConverter",
        "value.converter.schemas.enable": false
    }
}
```

## Configuración de Kafka UI

La configuración de la interfaz gráfica de Kafka, Kafka UI, se encuentra en el fichero `kafka-ui-config.yaml`. Esta configuración es imprescindible para indicar cuáles son las conexiones que tiene que monitorizar a Kafka UI. Principalmente, se configuran los valores de conexión al resto de servicios del stack de Kafka.

```yaml
kafka:
  clusters:
    - name: pissed-off-people-on-twitter
      bootstrapServers: http://broker:29092
      kafkaConnect: 
        clusters:
          - name: connect
            address: http://kafka-connect:8083
      KSQLDBServer: http://ksqldb-server:8088
      schemaRegistry: http://schema-registry:8081
```
