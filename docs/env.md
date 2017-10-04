# Version control with .env

**monasca-docker** leverages the [environmental variable handling][2] of
[docker-compose][1]. The latest release, a.k.a. versions of the images that
are used for *master* branch is controlled with the help of [.env](../.env)
file. Basically, the file contains all the images' versions and resembles the
following code snippet:

```sh
INFLUXDB_VERSION=1.3.2-alpine
INFLUXDB_INIT_VERSION=latest
MYSQL_VERSION=5.5
MYSQL_INIT_VERSION=1.5.1
MEMCACHED_VERSION=1.5.0-alpine
CADVISOR_VERSION=v0.26.1
ZOOKEEPER_VERSION=3.4

MON_SIDECAR_VERSION=1.0.0
MON_KEYSTONE_VERSION=1.1.1
MON_KAFKA_VERSION=0.9.0.1-2.11-1.0.2
MON_ALARMS_VERSION=1.1.0
MON_GRAFANA_VERSION=4.0.0-1.1.1
MON_GRAFANA_INIT_VERSION=1.1.0

MON_API_VERSION=master
MON_PERSISTER_VERSION=master
MON_THRESH_VERSION=latest
MON_NOTIFICATION_VERSION=master
MON_AGENT_FORWARDER_VERSION=master
MON_AGENT_COLLECTOR_VERSION=master
```

This file is automatically picked by [docker-compose][1], hence there are no
```export``` instructions.

## Overriding

In order to override certain images versions, for example to create OpenStack
Ocata based deployment, you may want to create a file, similar to this one:

```sh
export INFLUXDB_VERSION=1.1.0-alpine
export MON_API_VERSION=ocata
export MON_PERSISTER_VERSION=ocata
export MON_THRESH_VERSION=ocata
export MON_NOTIFICATION_VERSION=ocata
export MON_AGENT_FORWARDER_VERSION=ocata
export MON_AGENT_COLLECTOR_VERSION=ocata
```

That file, called ```.ocata.env```, differs from [.env](../.env), as it
contains ```export``` instructions. That is the mandatory approach, as sourced
variables take precedence over aforementioned environmental file.

    Alternative approach, that achieves the same result, is to override values
    of certain variables directly in ```.env``` file.

[1]: https://docs.docker.com/compose/
[2]: https://docs.docker.com/compose/environment-variables/
