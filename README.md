![pissed-off-people-on-twitter](./doc/img/twitter-logo-transformed.png "pissed-off-people-on-twitter")

Based on: https://huggingface.co/blog/sentiment-analysis-python

# Documentación
- [Diseño](./doc/design.md)
- [Manual de operación](./doc/operacion.md)
- [Manual de usuario](./doc/manual_uso.md)

# ¿Cómo desplegar?

```bash
$ docker-compose --env-file=run.env up -d
```

# Architecture (c4 model diagram - System context)

Primer nivel de diagrama de arquitectura modelo c4 - System context, en el que se detalla el contexto del sistema con elementos externos y la interrelación de los módulos internos en alto nivel.

![arch-diagram](./doc/img/arch-diagram.system_context.drawio.png "arch-diagram")

# Architecture (c4 model diagram - Containers)

Diagrama de arquitectura modelo c4 - Level 2 - Containers, con mayor nivel de detalle. En este diagrama, además del contexto del sistema, se detallan todos los módulos que intervienen y conforman la aplicación.

![arch-diagram-containers](./doc/img/arch-diagram.containers.drawio.png "arch-diagram-containers")
