# Arquitectura

![arch-diagram-containers](./img/arch-diagram.containers.drawio.png "arch-diagram-containers")

# Indice
- [Entrada de datos](#entrada)
    - [Ficheros](#Ficheros)
    - [Twitter API](#tw-api)
    - [REST Connect & Twitter API processer](#rest-connect)
- [Schema registry](#registry)
- [Salida](#Salida)
    - [KSQLDB & cli](#ksql)
    - [ElasticSearch & Kibana](#elastic)
- [Kafka UI](#kafka-ui)


# Entrada de datos<a name="entrada"></a>

El objetivo principal de la aplicación consiste en clasificar tweets en tiempo real, basándose en la opinión que transmiten, a medida que son generados en la aplicación de Twitter. La clasificación se realizará en tres categorías: positivo (POS), neutral (NEU) y negativo (NEG). Por consiguiente, se espera que la entrada de datos al sistema sea un flujo continuo de tweets, representando una corriente constante de información.

Se han implementado dos servicios de entrada: mediante **ficheros** en formato _.csv_ y a través de una **API Rest**. La API REST ha sido diseñada para emular las funcionalidades de la herramienta de desarrollo REST de Twitter. Esta decisión se ha tomado debido a que la herramienta de Twitter requiere un pago y proporciona un conjunto demasiado limitado de utilidades para los miembros gratuitos.

## Kafka Connect

Todas las entradas del sistema están construídas bajo un clúster de Kafka Connect. También el Sink Connector de ElasticSearch. Y se puede configurar cuáles de estos conectores se quieren activar o desactivar ([Manual de usuario](manual_uso.md)).

El contenedor del clúster de Kafka connect lanza un script para controlar que el clúster de Kafka se lance antes. Una vez se despliega el clúster de Kafka, se lanza la inicialización de los conectores configurados.

## Ficheros

El primer servicio de entrada ingesta información que proviene de ficheros en formato _.csv_. Para la ingesta de la información se ha integrado un conector de Kafka connect que simplifica la operación de lectura y transformación de los datos. Existen, al menos, dos conectores encargados de ingestar información a través de ficheros: [FileStream](https://docs.confluent.io/platform/current/connect/filestream_connector.html) y [Spool Dir](https://docs.confluent.io/kafka-connectors/spooldir/current/overview.html), pero según la documentación oficial de Confluent se recomienda utilizar el conector Spool Dir en entornos productivos.

[Spool dir recommendation](https://docs.confluent.io/platform/current/connect/filestream_connector.html)
> Confluent does not recommend the FileStream Connector for production use. If you want a production connector to read from files, use a Spool Dir connector.

En la configuración del conector se debe especificar el directorio de lectura de los ficheros, `input.path`; el patrón que sigue el nombre de los ficheros que contienen la información, `input.file.pattern`; directorio de ficheros procesados, `finished.path`, y directorio de ficheros erróneos, `error.path`. Además, se definen otras configuraciones relevantes al comportamiento del conector como la desactivación de parada del sistema ante errores, el carácter de escape que se utiliza en la información leída (se especifica a 0 porque es el carácter nulo. Muchos tweets contienen ':\' para representar estados de ánimo, lo cuál hace que se escape el carácter que delimita los tweets causando errores en la lectura de los ficheros). También se especifica el esquema AVRO con el que se convierten los mensajes al ser trasmitidos al topic.

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

La especificación del esquema que siguen los mensajes suprime la necesidad de ingestar mensajes para inducir o generar un nuevo esquema. Es importante, sin embargo, que los datos de los ficheros que se consumen sigan un patrón común. El patrón que se ha decidido es el siguiente:

```
id,date,user,tweet
1467810369,Mon Apr 06 22:19:45 PDT 2009,_TheSpecialOne_,"@switchfoot http://twitpic.com/2y1zl - Awww, that's a bummer.  You shoulda got David Carr of Third Day to do it. ;D"
```

## Twitter API<a name="tw-api"></a>

El kit de desarrollador de Twitter es de pago y la funcionalidad accesible de forma gratuita está limitada a la lectura de 1000 tweets. Por estas razones se ha desarrollado una API que emula la generación de tweets cada ciertos segundos. El funcionamiento es muy sencillo y su carácter es exclusivamente de desarrollo y pruebas.

Cada vez que se realiza una llamada al endpoint `GET /tweets` se leen aleatoriamente entre 1 y 10 tweets de un conjunto de datos (que debe ser especificado durante el arranque del servicio). La única configuración posible es la ruta de lectura del fichero de datos que contiene los tweets. Se puede especificar como variable de entorno `TWEETS_FILE_PATH` o con un fichero de configuración adicional en formato yaml. Se puede utilizar un fichero de configuración indicando la ruta del fichero con la variable de entorno `CONFIG_PATHS` ([Configuración](operacion.md#Configuración)).

Ejemplo de configuración:
```yaml
tweets:
  path: /data/tweets_processed.csv
```

La imagen del servicio está construída sobre Python 3.10 y utiliza FastAPI.

## REST Connect & Twitter API processer<a name="rest-connect"></a>

No existe un conector oficial para el consumo de endpoints de API REST de Kafka, sin embargo, sí existe un [plugin creado por Lenny Löfberg](https://github.com/llofberg/kafka-connect-rest/tree/master) con esta funcionalidad. Este conector lanza una petición contra un servicio REST, contra un endpoint concreto, separadas por un intervalo de tiempo especificado en su configuración, `rest.source.poll.interval.ms`. El repositorio del plugin se encuentra en un estado desactualizado, por lo que hay un problema en la configuración de maven que es necesario modificar. Concretamente hay que modificar la versión de confluent y la URL en las propiedades del `pom.xml`:

```xml
<confluent.version>5.2.1</confluent.version>
<confluent.maven.repo>https://packages.confluent.io/maven/</confluent.maven.repo>
```

Configuración del conector REST:

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

Dado que se trata de un plugin, es imprescindible instalarlo en la imagen para su posterior utilización. Por lo tanto, la imagen de Kafka Connect que se emplea se ha diseñado como una imagen multi-stage. En esta configuración, primero se construye el plugin y luego se lleva a cabo su configuración para habilitar su funcionalidad.

### Twitter API processer


# Schema registry<a name="registry"></a>

# Salida

## KSQLDB & cli<a name="ksql"></a>

## ElasticSearch & Kibana<a name="elastic"></a>

### Sink connect

# Kafka UI<a name="kafka-ui"></a>