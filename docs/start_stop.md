# Advanced start, stop and status

## Starting

### All services

To spin up the entire monaca-docker (including both **log** and **metric**
pipelines) one must execute:

```sh
$ docker-compose -f log-pipeline.yml -f docker-compose.yml up
```

from the root of the [monasca-docker][1] repository.

Invidual pipelines can still be launched. See below for more details

#### Metric pipeline

For **metric** pipeline it suffices to just execute

```sh
$ docker-compose up
```

or

```sh
$ docker-compose -f docker-compose.yml up
```

There is a 3rd approach which requires passing all (some) of the members of
**metric** pipeline as arguments after ```up```. For example:

```sh
$ docker-compose up kafka zookeeper monasca-notification
```

It will result in launching only **kafka**, **zookeeper** and **monasca-notification**.

#### Log pipeline

The **log** pipeline is a bit more complicated. As it is an addition to the
**metric** pipeline, some of the services are
shared between each and thus defined in [docker-compose.yml](../docker-compose.yml) without a duplicate
in **log-pipeline.yml**. That affects the way you could launch *just* the **log** pipeline. See the
examples below to get a grip:

* both pipelines ```docker-compose -f log-pipeline.yml -f docker-compose.yml up```
* just **log** pipeline ```docker-compose -f log-pipeline.yml -f docker-compose.yml up {{
  log_pipeline_members }}``` where ```log_pipeline_members``` resolves to all the services defined in
  [log-pipeline.yml](../log-pipeline.yml) file + some of the services that are
  shared between i.e **kafka**, **zookeeper**, **keystone**, **mysql**. Obviously all the *-init*
  containers corresponding to aforementioned services should be included in launch as well.

### Invidual services

Launching individual services has been described above to some extent. In greater detail, launching an
individual service is as easy as specifying what service(s) you wish to launch as an argument to the
```docker-compose up``` command. For example, to launch **monasca-log-transformer** you execute
something like ```docker-compose -f log-pipeline up log-transformer```. The tricky point is to know
the "dependencies" of single service. These "dependencies" need to be available, either externally or
launched together with the desired service.

## Stopping

Stopping the services it similar to starting them. The difference is that instead of doing
```docker-compose up``` you do ```docker-compose stop```. With this command you can:

* stop everything ```docker-compose -f log-pipeline.yml -f docker-compose.yml stop```
* stop service(s) ```docker-compose -f log-pipeline.yml -f docker-compose.yml stop {{ services }}```

An important thing to mention is that ```stop``` does not result in removing the containers from the
system. In order to stop and execute a bit of cleaning replace ```stop``` with ```down```.

## Getting status

To know if the the service is up and running, you can execute ```docker-compose ps```. That command is
similar to plain ```docker ps```. However it allows to use the easier to remember *service name* instead of
auto-generated labels docker assigns to containers. For example:

```sh
$ docker-compose ps kafka
        Name             Command    State    Ports
----------------------------------------------------
monascadocker_kafka_1   /start.sh   Up      9092/tcp
```

[1]: [https://github.com/monasca/monasca-docker]
