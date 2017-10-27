monasca/storm Dockerfile
========================

This image runs an instance of [Apache Storm][1] optimized for Docker and
Kubernetes environments.

Sources: [monasca/storm][2] &middot; [Dockerfile][3] &middot; [monasca-docker][4]


Tags
----

Images in this repository are tagged as follows:

 * `1.0.3`: storm version
 * `latest`: the latest version recommended for use with other Monasca
   components. Currently, this is `1.0.3`
 * `master`: a development / testing build not necessarily intended for
   production use

Usage
-----

Storm requires several components. First a nimbus instance should be started:

    docker run --name storm-nimbus monasca/storm:1.0.3 storm nimbus

Then one or more supervisor instances:

    docker run \
      --name storm-supervisor \
      --link storm-nimbus \
      monasca/storm:1.0.3 storm supervisor

The cluster then requires a topology. To use [monasca-thresh][6]:

    docker run --rm=true --link storm-nimbus monasca/thresh:master

The submission takes around a minute to complete, after which the container is
no longer needed. Storm will automatically transfer the topology to new workers
that join, restart, etc, and as such the topology only needs to be submitted
once unless the cluster is completely reset.

Configuration
-------------

Several parameters can be specified using environment variables:

| Variable                 | Default        | Description                           |
|--------------------------|----------------|---------------------------------------|
| `ZOOKEEPER_SERVERS`      | `zookeeper`    | Comma-separated list of ZK hostnames  |
| `ZOOKEEPER_PORT`         | `2181`         | Port to use for hostnames             |
| `ZOOKEEPER_WAIT`         | `true`         | If `true`, wait for ZK before startup |
| `SUPERVISOR_SLOTS_PORTS` | `6701,6702`    | List of supervisor ports, 1 per process |
| `NIMBUS_SEEDS`           | `storm-nimbus` | Comma-separated list of Nimbus hosts  |
| `STORM_LOCAL_HOSTNAME`   |                | If set, use as storm hostname, if not set, use container IP |
| `LOG_LEVEL`              | `warn`         | log4j2 console logging level          |
| `WORKER_LOGS_TO_STDOUT`  | `false`        | if `true`, workers log to container stdout |

Note that the configuration template also supports a number of less common
environment variables. See the [`storm.yaml.j2`][5] template for a full list.

### Memory

Note that all Storm JVM processes are configured to scale their max heap size
based on a configured container limit (using Docker's `--memory` flag or
similar). This behavior can be tuned as follows:

| Variable             | Default | Description                                              |
|----------------------|---------|----------------------------------------------------------|
| `JVM_MAX_RATIO` | `0.75`  | The max % of allocatable memory to pass to `-XX:MaxRAM`       |
| `JVM_MAX_MB`    | unset   | Value to use for allocatable memory, autodetect if unset |
| `MAX_OVERRIDE_MB`   | unset   | Ignore scaling, always return `-XX:MaxRAM$MAX_OVERRIDE_MB` |
| `SUPERVISOR_MAX_MB` | `256` | MaxRam of JVM in MiB for supervisor |
| `WORKER_MAX_MB`     | `784` | MaxRam of JVM in MiB for workers    |
| `NIMBUS_MAX_MB`     | `256` | MaxRam of JVM in MiB for nimbus          |
| `UI_MAX_MB`         | `768` | MaxRam of JVM in MiB for UI              |
| `SUPERVISOR_STACK_SIZE` | `1024k` | JVM stack size    |
| `WORKER_STACK_SIZE`     | `1024k` | JVM stack size    |
| `NIMBUS_STACK_SIZE`     | `1024k` | JVM stack size    |
| `UI_STACK_SIZE`         | `1024k` | JVM stack size    |

Memory scaling is done based off of an automatically determined "effective"
memory limit. The ultimate limit is either the true system memory limit or, if
set, a limited value set via Docker's `--memory` flag (whichever value is
smallest). This value is then scaled by `JVM_MAX_RATIO` to ensure some
memory is left for other use.

The final max ram size for each component is then the smallest of:
 * The component-specific memory request, e.g. `WORKER_MAX_MB`
 * The scaled allocatable memory (as described above)
 * If set, `JVM_MAX_MB`

### monasca-thresh

Configuration for [monasca-thresh][6] is included by default and supports a
number of additional configuration options:

| Variable                      | Default      | Description                   |
|-------------------------------|--------------|-------------------------------|
| `METRIC_SPOUT_THREADS`        | `2`          | Metric Spout threads          |
| `METRIC_SPOUT_TASKS`          | `2`          | Metric Spout tasks            |
| `KAFKA_URI`                   | `kafka:9092` | Kafka host                    |
| `MYSQL_DB_HOST`               | `mysql`      | MySQL host                    |
| `MYSQL_DB_PORT`               | `3306`       | MySQL port                    |
| `MYSQL_DB_DATABASE`           | `mon`        | Monasca database name         |
| `MYSQL_DB_USERNAME`           | `thresh`     | MySQL user                    |
| `MYSQL_DB_PASSWORD`           | `password`   | MySQL password                |
| `EVENT_SPOUT_THREADS`         | `2`          | Event Spout Threads           |
| `EVENT_SPOUT_TASKS`           | `2`          | Event Spout Tasks             |
| `EVENT_BOLT_THREADS`          | `2`          | Event Bolt Threads            |
| `EVENT_BOLT_TASKS`            | `2`          | Event Bolt Tasks              |
| `FILTERING_BOLT_THREADS`      | `2`          | Filtering Bolt Threads        |
| `FILTERING_BOLT_TASKS`        | `2`          | Filtering Bolt Tasks          |
| `ALARM_CREATION_BOLT_THREADS` | `2`          | Alarm Creation Bolt Threads   |
| `ALARM_CREATION_BOLT_TASKS`   | `2`          | Alarm Creation Bolt Tasks     |
| `AGGREGATION_BOLT_THREADS`    | `2`          | Aggregation Bolt Threads      |
| `AGGREGATION_BOLT_TASKS`      | `2`          | Aggregation Bolt Tasks        |
| `THRESHOLDING_BOLT_THREADS`   | `2`          | Thresholding Bolt Threads     |
| `THRESHOLDING_BOLT_TASKS`     | `2`          | Thresholding Bolt Tasks       |
| `USE_SSL_ENABLED`             | `true`       | Use SSL validation with MySql |

Note that monasca-thresh configs can be removed by overwriting or removing
`/templates/thresh-config.yml.j2`.

[1]: http://storm.apache.org/
[2]: https://github.com/hpcloud-mon/monasca-docker/blob/master/storm/
[3]: https://github.com/hpcloud-mon/monasca-docker/blob/master/storm/Dockerfile
[4]: https://github.com/hpcloud-mon/monasca-docker/
[5]: https://github.com/hpcloud-mon/monasca-docker/blob/master/storm/templates/storm.yaml.j2
[6]: https://github.com/openstack/monasca-thresh
