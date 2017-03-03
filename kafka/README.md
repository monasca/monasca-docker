monasca/kafka Dockerfile
========================

This image runs an instance of [Apache Kafka][1] optimized for Docker and
Kubernetes environments.

Sources: [mysql-init][2] &middot; [Dockerfile][3] &middot; [monasca-docker][4]

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
| `KAFKA_CREATE_TOPICS`         | unset   | Topics to create on startup, see below         |
| `KAFKA_TOPIC_CONFIG`          | unset   | Default config args for created topics         |
| `KAFKA_DELETE_TOPIC_ENABLE`   | `false` | Enable topic deletion                          |
| `KAFKA_LISTEN_PORT`           | `9092`  | Port for Kafka to listen on                    |
| `KAFKA_ADVERTISED_PORT`       | `$KAFKA_LISTEN_PORT` | Kafka port advertised to clients  |
| `KAFKA_CONTROLLED_SHUTDOWN_ENABLE` | `true` | If `true`, enable [controlled shutdown][6] |
| `KAFKA_JMX`                   | unset   | If `true`, expose JMX metrics over TCP         |
| `KAFKA_JMX_PORT`              | `7203`  | Port to expose JMX metrics                     |
| `KAFKA_JMX_OPTS`              | no SSL/auth, etc | Override default opts                 |

### Topic creation

This image will create topics automatically on first startup when
`KAFKA_CREATE_TOPICS` is set:

```
docker run \
    --name kafka \
    --link zookeeper \
    -e KAFKA_CREATE_TOPICS="topic1:64:1,topic2:16:1"
    monasca/kafka:latest
```

The variable should be set to a comma-separated list of topic strings. These
each look like so:

```
[topic name]:partitions=[partitions]:replicas=[replicas]:[key]=[val]:[key]=[val]
```

In the above, `partitions` and `replicas` are required, and tokens surrounded by
`[brackets]` should be replaced with the desired value. All other properties
will be translated to `--config key=val` when running `kafka-topics.sh`.
Example:

```
my_topic_name:partitions=3:replicas=1:segment.ms=900000
```

Partitions and replicas also support an index-based shorthand, so the following
works as well:

```
[topic name]:[partitions]:[replicas]
```

As an example, this is a valid `KAFKA_CREATE_TOPICS` string for [Monasca][8]
installations as used in the [docker-compose][4] environment:

    metrics:64:1,alarm-state-transitions:12:1,alarm-notifications:12:1,retry-notifications:3:1,events:12:1,60-seconds-notifications:3:1

If desired, default config parameters can be set using `KAFKA_TOPIC_CONFIG`.
These use `key=value,key2=value2` syntax and will be translated into
`--config key=value` arguments as described above. If a duplicate key is passed
in a specific topic string, it will override the value specified here.

[1]: http://kafka.apache.org/
[2]: https://github.com/hpcloud-mon/monasca-docker/blob/master/kafka/
[3]: https://github.com/hpcloud-mon/monasca-docker/blob/master/kafka/Dockerfile
[4]: https://github.com/hpcloud-mon/monasca-docker/
[5]: https://hub.docker.com/r/library/zookeeper/
[6]: https://kafka.apache.org/documentation/#basic_ops_restarting
[7]: https://github.com/wurstmeister/kafka-docker
[8]: https://hub.docker.com/r/monasca/api/
