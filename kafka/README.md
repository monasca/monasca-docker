monasca/kafka Dockerfile
========================

This image runs an instance of [Apache Kafka][1] optimized for Docker and
Kubernetes environments.

Sources: [kafka][2] &middot; [Dockerfile][3] &middot; [monasca-docker][4]

Tags
----

Images in this repository are tagged as follows:

 * `[kafka version]-[scala version]`, e.g. `0.9.0.1-2.11`
 * `latest`: the latest version recommended for use with other Monasca
   components. Currently, this is `0.9.0.1-2.11`
 * `master`: a development / testing build not necessarily intended for
   production use

Usage
-----

Kafka requires a running instance of Zookeeper. The [library zookeeper image][5]
is recommended:

    docker run --name zookeeper -d zookeeper:3.3

If Zookeeper is accessible at `zookeeper:2181`, no additional options need to be
specified:

    docker run --name kafka --link zookeeper monasca/kafka:latest

Kafka will be running on port `9092` by default. If JMX is enabled, that port
will be available as well (`7203` by default). These ports can be exposed as
necessary (`-p 9092:9092` or similar), but keep in mind that forwarding ports
will impact connectivity unless `KAFKA_ADVERTISED_HOST_NAME` is set correctly as
described below.

Configuration
-------------

Several parameters can be specified using environment variables:

| Variable                      | Default          | Description                           |
|-------------------------------|------------------|---------------------------------------|
| `ZOOKEEPER_CONNECTION_STRING` | `zookeeper:2181` | Comma-separated list of ZK hosts      |
| `ZOOKEEPER_WAIT`              | `true`  | If true, wait for zookeeper to become ready    |
| `ZOOKEEPER_WAIT_TIMEOUT`      | `3`     | Connection timeout for ZK wait loop            |
| `ZOOKEEPER_WAIT_DELAY`        | `10`    | Seconds to wait between connection attempts    |
| `ZOOKEEPER_WAIT_RETRIES`      | `20`    | Password for given user                        |
| `ZOOKEEPER_CHROOT`            | unset   | Optional ZK chroot / path prefix               |
| `KAFKA_HOSTNAME_FROM_IP`      | `true`  | If `true`, set advertised hostname to container IP  |
| `KAFKA_ADVERTISED_HOST_NAME`  | from IP | If set, use value as advertised hostname       |
| `KAFKA_BROKER_ID`             | `-1`    | Unique Kafka broker ID, `-1` for auto          |
| `KAFKA_LISTEN_PORT`           | `9092`  | Port for Kafka to listen on                    |
| `KAFKA_ADVERTISED_PORT`       | `$KAFKA_LISTEN_PORT` | Kafka port advertised to clients  |
| `KAFKA_CONTROLLED_SHUTDOWN_ENABLE` | `true` | If `true`, enable [controlled shutdown][6] |
| `KAFKA_JMX`                   | unset   | If `true`, expose JMX metrics over TCP         |
| `KAFKA_JMX_PORT`              | `7203`  | Port to expose JMX metrics                     |
| `KAFKA_JMX_OPTS`              | no SSL/auth, etc | Override default opts                 |
| `SERVER_LOG_LEVEL`            | `INFO`  | Log Level for server                           |
| `REQUEST_LOG_LEVEL`           | `WARN`  | Log Level for request logging                  |
| `CONTROLLER_LOG_LEVEL`        | `INFO`  | Log Level for controller                       |
| `LOG_CLEANER_LOG_LEVEL`       | `INFO`  | Log Level for log cleaner                      |
| `STATE_CHANGE_LOG_LEVEL`      | `INFO`  | Log Level for state changes                    |
| `AUTHORIZER_LOG_LEVEL`        | `WARN`  | Log Level for the authorizer                   |
| `GC_LOG_ENABLED`              | `False` | If True, JVM garbage collection log enabled    |
| `KAFKA_STACK_SIZE`            | `1024k` | JVM stack size                                 |
| `LOG_RETENTION_HOURS`         | `4`     | Number of hours to keep a log file             |
| `LOG_ROLL_MS`                 | `900000` | Number of ms before a new log segment is rolled out |
| `STAY_ALIVE_ON_FAILURE`       | `false` | If `true`, container stays alive for 2 hours after kafka exits |

### Log Files

Multiple Kafka log files are written to stdout for the container. They can be distinguished via
the logfile attribute in each message. For example:

```
kafka_1                 | [2017-06-15 06:32:09,572] INFO logfile=server.log Loading logs. (kafka.log.LogManager)
```

If `GC_LOG_ENABLED` is set to True, the JVM Garbage Collection log will be written within the
container at /kafka/logs/kafkaServer-gc.log. It can't be redirected to stdout.

[1]: http://kafka.apache.org/
[2]: https://github.com/hpcloud-mon/monasca-docker/blob/master/kafka/
[3]: https://github.com/hpcloud-mon/monasca-docker/blob/master/kafka/Dockerfile
[4]: https://github.com/hpcloud-mon/monasca-docker/
[5]: https://hub.docker.com/r/library/zookeeper/
[6]: https://kafka.apache.org/documentation/#basic_ops_restarting
