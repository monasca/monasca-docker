monasca-thresh Dockerfile
===============================

This image has a containerized version of the Monasca Threshold Engine. For
more information on the Monasca project, see [the wiki][1].

Sources: [monasca-thresh][2] &middot; [monasca-docker][3] &middot; [Dockerfile][4]

Tags
----

Images in this repository are tagged as follows:

 * `latest`: refers to the latest stable point release, e.g. `1.7.0`
 * `1.0.0`, `1.0`, `1`: standard semver tags based on git tags in the
   [official repository][2].
 * `newton`, `ocata`, etc: named versions following OpenStack release names
   built from the tip of `stable/RELEASENAME` branches in the repository
 * `master`, `master-DATESTAMP`: unstable testing builds from the master branch,
   these may have features or enhancements not available in stable releases, but
   are not production-ready.

Note that features in this Dockerfile, particularly relating to running in
Docker and Kubernetes environments, require code that has not yet been made
available in a tagged release. Until this changes, only `master` images may be
available and `latest` may point to `master` images.

Usage
-----

The Threshold engine requires configured instances of MySQL, Kafka,
Zookeeper, and optionally Storm [monasca-api][5]. In environments resembling the official
[docker-compose][3] or [Kubernetes][6] environments, this image requires little
to no configuration and can be minimally run like so:

    docker run monasca/thresh:latest

Configuration
-------------

| Variable                      | Default        | Description                              |
|-------------------------------|----------------|------------------------------------------|
| `MYSQL_DB_HOST`               | `mysql`        | MySQL hostname                           |
| `MYSQL_DB_PORT`               | `3306`         | MySQL port                               |
| `MYSQL_DB_USERNAME`           | `thresh`       | MySQL username                           |
| `MYSQL_DB_PASSWORD`           | `password`     | MySQL password                           |
| `MYSQL_DB_DATABASE`           | `mon`          | MySQL database name                      |
| `MYSQL_WAIT_RETRIES`          | `24`           | # of tries to verify MySQL availability  |
| `MYSQL_WAIT_DELAY`            | `5`            | # seconds between retry attempts         |
| `KAFKA_URI`                   | `kafka:9092`   | If `true`, disable remote root login     |
| `KAFKA_WAIT_FOR_TOPICS`       | `alarm-state-transitions,metrics,events`    | Comma-separated list of topic names to check |
| `KAFKA_WAIT_RETRIES`          | `24`           | # of tries to verify Kafka availability  |
| `KAFKA_WAIT_DELAY`            | `5`            | # seconds between retry attempts         |
| `ZOOKEEPER_URL`               | `zookeeper:2181` | Zookeeper URL                          |
| `NO_STORM_CLUSTER`            | unset          | If `true`, run without Storm daemons     |
| `STORM_WAIT_RETRIES`          | `24`           | # of tries to verify Storm availability  |
| `STORM_WAIT_DELAY`            | `5`            | # seconds between retry attempts         |
| `WORKER_MAX_MB`          | unset          | If set and `NO_STORM_CLUSTER` is `true`, use as MaxRam Size for JVM |
| `METRIC_SPOUT_THREADS`        | `2`            | Metric Spout threads        |
| `METRIC_SPOUT_TASKS`          | `2`            | Metric Spout tasks          |
| `EVENT_SPOUT_THREADS`         | `2`            | Event Spout Threads         |
| `EVENT_SPOUT_TASKS`           | `2`            | Event Spout Tasks           |
| `EVENT_BOLT_THREADS`          | `2`            | Event Bolt Threads          |
| `EVENT_BOLT_TASKS`            | `2`            | Event Bolt Tasks            |
| `FILTERING_BOLT_THREADS`      | `2`            | Filtering Bolt Threads      |
| `FILTERING_BOLT_TASKS`        | `2`            | Filtering Bolt Tasks        |
| `ALARM_CREATION_BOLT_THREADS` | `2`            | Alarm Creation Bolt Threads |
| `ALARM_CREATION_BOLT_TASKS`   | `2`            | Alarm Creation Bolt Tasks   |
| `AGGREGATION_BOLT_THREADS`    | `2`            | Aggregation Bolt Threads    |
| `AGGREGATION_BOLT_TASKS`      | `2`            | Aggregation Bolt Tasks      |
| `THRESHOLDING_BOLT_THREADS`   | `2`            | Thresholding Bolt Threads   |
| `THRESHOLDING_BOLT_TASKS`     | `2`            | Thresholding Bolt Tasks     |
| `THRESH_STACK_SIZE`           | `1024k`        | JVM stack size              |

Running with and without Storm
------------------------------

The Threshold Engine can be run in two different modes, with Storm Daemons or without Storm Daemons.
If run with the Storm Daemons, multiple Storm Supervisor containers can be used with more than one worker process
in each. With no Storm Daemons, only a single Threshold Engine container can be run with a single worker process.

The default docker-compose.yml file is configured to run without Storm. To change docker-compose.yml to run
with Storm, delete the `thresh` service entry and replace it with the below:

```
  storm-nimbus:
    image: monasca/storm:1.0.3
    command: storm nimbus
    environment:
      STORM_LOCAL_HOSTNAME: "storm-nimbus"
      WORKER_LOGS_TO_STDOUT: "true"
    depends_on:
      - zookeeper
      - kafka

  storm-supervisor:
    image: monasca/storm:1.0.3
    command: storm supervisor
    depends_on:
      - storm-nimbus
      - zookeeper
      - kafka

  thresh-init:
    image: monasca/thresh:master
    environment:
      STORM_WAIT_RETRIES: 50
    depends_on:
      - zookeeper
      - storm-nimbus
      - storm-supervisor
```

[1]: https://wiki.openstack.org/wiki/Monasca
[2]: https://github.com/openstack/monasca-thresh/
[3]: https://github.com/hpcloud-mon/monasca-docker/
[4]: https://github.com/hpcloud-mon/monasca-docker/blob/master/monasca-thresh/Dockerfile
[5]: https://github.com/hpcloud-mon/monasca-docker/blob/master/storm/Dockerfile
[6]: https://github.com/hpcloud-mon/monasca-docker/blob/master/k8s/
[7]: https://v2.developer.pagerduty.com/docs/events-api
