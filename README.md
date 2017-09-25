Dockerfiles for Monasca
=======================

[![Build Status](https://travis-ci.org/monasca/monasca-docker.svg?branch=master)](https://travis-ci.org/monasca/monasca-docker)

This repository contains resources for building and deploying a full Monasca
stack in Docker and Kubernetes environments.

Requirements
------------

 * docker, version >= 1.13 recommended
 * docker-compose >= 1.9.0
 * at least 4 GiB of RAM
 * 2 CPUs (cores) or more recommended

Quick Start
-----------

To quickly get a Monasca environment running, you can use [docker-compose][1]:

    docker-compose up

Assuming all goes well, the following services should be exposed on your host
machine:

 * keystone on ports 5000 and 35357
   * see [`preload.yml`][2] for full account info
 * monasca-api on port 8070
 * grafana on port 3000
   * log in with `mini-mon` and `password` (or any valid keystone account)

If needed, `docker-compose rm` can be used to completely clean the environment
between runs.

Advanced start, stop and status
-------------------------------

## Starting 

### All services

To spin up entire monaca-docker (including both **log** and **metric** pipelines) one must execute 
```docker-compose -f log-pipeline.yml -f docker-compose.yml up``` from the root of 
the (monasca-docker)[https://github.com/monasca/monasca-docker] repository. 

Invidual pipelines can still be launched. See below for more details

#### Metric

For **metric** pipeline it suffices to just execute ```docker-compose up``` 
or ```docker-compose -f docker-compose.yml up```. There is 3rd approach which requires passing all (some) of the members of 
**metric** pipeline as arguments after ```up```. For example: ```docker-compose up kafka zookeeper monasca-notification```.
The last command will result in launching only **kafka**, **zookeeper** and **monasca-notification**. It might come in handy
if the deployment is distributed.

#### Logs

The **log** pipeline is a bit more complicated. As it is an addition to the **metric** pipeline, some of the services are 
shared between each and thus defined in **docker-compose.yml** without a duplicate in **log-pipeline.yml**. That effects the way
you could launch *just* the **log** pipeline. See the examples below to get a grip:

* both pipelines ```docker-compose -f log-pipeline.yml -f docker-compose.yml up```
* just **log** pipeline ```docker-compose -f log-pipeline.yml -f docker-compose.yml up {{ log_pipeline_members }}``` where
```log_pipeline_members``` resolves to all the services defined in **log-pipeline.yml** file + some of the services that are 
shared between i.e **kafka**, **zookeeper**, **keystone**, **mysql**. Obviously all the *-init* containers corresponding to 
aformentioned services should be included in launch as well.

### Invidual services

Launching individual services has been described above to some extent. In greater detail, launching an invidual service is as 
easy as specyfying what service(s) you wish to launch as an argument to the ```docker-compose up``` command. For example, to
launch monasca-log-transformer you exeute something like ```docker-compose -f log-pipeline up log-transformer```. The tricky
point is to known the "dependencies" of single service. These "dependencies" need to be available, either externally or 
launched together with the desired service.

## Stopping

Everything stays the same, as for the launching. The difference is that insted of doing ```docker-compose up``` you do 
```docker-compose stop```. With this command you can:

* stop everything ```docker-compose -f log-pipeline.yml -f docker-compose.yml stop```
* stop service(s) ```docker-compose -f log-pipeline.yml -f docker-compose.yml stop {{ services }}```

An important thing to mention is that ```stop``` does not result in removing the containers from the system. In order to stop
and execute a bit of cleaning replace ```stop``` with ```down```. 

## Getting status

To know if the the service is up and running, you can execute ```docker-compose ps```. That command is similar to plain 
```docker ps```. However it allows to use easier to remember *service name* instead of auto-generated labels docker assigns 
to containers. For example:

```sh
09:13 $ docker-compose ps kafka
        Name             Command    State    Ports   
----------------------------------------------------
monascadocker_kafka_1   /start.sh   Up      9092/tcp 
```

Repository Layout
-----------------

 * `monasca-api-python/`: Dockerfile for monasca-api (python version)
 * `monasca-persister-python/`: Dockerfile for monasca-persister (python
   version)
 * `monasca-notification/`: Dockerfile for the notification engine
 * `monasca-agent/`: Dockerfile for Monasca Agent

There are also several run-once init containers used to bootstrap a new
Monasca installation:
 * `grafana-init/`: pre-loads Grafana with a Monasca datasource and several
   default dashboard
 * `influxdb-init/`: creates influxdb users and databases
 * `monasca-thresh/`: job to submit the monasca-thresh Storm topology
 * `mysql-init/`: initializes MySQL users, databases, and schemas

A number of custom dependency containers are also here:

 * `grafana/`: Dockerfile for Grafana with Keystone auth and Monasca plugins
 * `keystone/`: Dockerfile for dev keystone
 * `kafka/`: Dockerfile for k8s-compatible Kafka
 * `storm/`: Dockerfile for Storm container

Version control
---------------

**monasca-docker** leverages the [environmental variable handling][3] of
[docker-compose][1]. The latest release, a.k.a. versions of the images that
are used for *master* branch is controlled with the help of [.env](./.env) file.
In overall the file contains all the images' versions and resembles the following
code snippet:

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

This file is automatically picked by [docker-compose][1], hence there are no ```export```
instructions.

In order to override certain images versions, for example to create OpenStack Ocata based deployment,
you may want to create a file, similar to this one:

```sh

export INFLUXDB_VERSION=1.1.0-alpine
export MON_API_VERSION=ocata
export MON_PERSISTER_VERSION=ocata
export MON_THRESH_VERSION=ocata
export MON_NOTIFICATION_VERSION=ocata
export MON_AGENT_FORWARDER_VERSION=ocata
export MON_AGENT_COLLECTOR_VERSION=ocata

```

That file, called ```.ocata.env```, differs from [.env](./.env), as it contains ```export```
instructions. That is mandatory approach, as sourced variables takes precedence over
aforementioned environmental file.

    Alternative approach, that achieves the same result, is to override values
    of certain variables directly in ```.env``` file.

Using external OpenStack Keystone
---------------------------------

By default `monasca-docker` is using Keystone stored in separate container.
But if you want to use external Keystone you need to overwrite some
environment variables in specific containers.

Remove `keystone` image initialization and all references to this
image from `depends_on` from other images from `docker-compose.yml` and
`log-pipeline.yml` files.

Example configuration taking into account usage of Keystone aliases
instead of ports when overwriting environment variables:

#### `docker-compose.yml`

In `agent-forwarder` and `agent-collector`:
```yaml
environment:
  OS_AUTH_URL: http://192.168.10.6/identity/v3
  OS_USERNAME: monasca-agent
  OS_PASSWORD: password
  OS_PROJECT_NAME: mini-mon
```

In `alarms`:
```yaml
environment:
  OS_AUTH_URL: http://192.168.10.6/identity/v3
  OS_USERNAME: mini-mon
  OS_PASSWORD: password
  OS_PROJECT_NAME: mini-mon
```

In `monasca`:
```yaml
environment:
  KEYSTONE_IDENTITY_URI: http://192.168.10.6/identity
  KEYSTONE_AUTH_URI: http://192.168.10.6/identity
  KEYSTONE_ADMIN_USER: admin
  KEYSTONE_ADMIN_PASSWORD: secretadmin
```

In `grafana`:
```yaml
environment:
  GF_AUTH_KEYSTONE_AUTH_URL: http://192.168.10.6/identity
```

#### `log-pipeline.yml`

In `kibana`:
```yaml
environment:
  KEYSTONE_URI: 192.168.10.6/identity
```

In `log-api`:
```yaml
environment:
  KEYSTONE_AUTH_URI: http://192.168.10.6/identity
  KEYSTONE_IDENTITY_URI: http://192.168.10.6/identity
  KEYSTONE_ADMIN_USER: admin
  KEYSTONE_ADMIN_PASSWORD: secretadmin
```

Synchronizing containers time with host time
--------------------------------------------

If you want to synchronize containers time with host time they are running on,
you need to add to every service following volumes:

```yaml
volumes:
  - "/etc/timezone:/etc/timezone:ro"
  - "/etc/localtime:/etc/localtime:ro"
```

[1]: https://docs.docker.com/compose/
[2]: https://github.com/hpcloud-mon/monasca-docker/blob/master/keystone/preload.yml
[3]: https://docs.docker.com/compose/environment-variables/
