kafka-init
==========

**kafka-init** is responsible for creating the topics.

Tags
----

Images in this repository are tagged as follows:

* `0.0.1` - standard [SemVer][1]
* `latest`: the latest version recommended to use with other Monasca
  components.


Usage
-----

**kafka-init** requires a running instance of [Kafka][2]. It can be launched using
command similar to this ```docker run -d -p 9092:9092 -l zookeeper monasca/kafka```.
**kafka-init** will wait for Kafka to become accessible.

Configuration
-------------

Several parameters can be specified using environment variables:

| Variable                      | Default          | Description                           |
|-------------------------------|------------------|---------------------------------------|
| `ZOOKEEPER_CONNECTION_STRING` | `zookeeper:2181` | Comma-separated list of ZK hosts      |
| `KAFKA_HOST`                  | `kafka:9092`     | One of the Kafka brokers              |
| `KAFKA_TIMEOUT`               | `60`      | How long to wait for Kafka to become available |
| `KAFKA_CREATE_TOPICS`         | `unset`   | Topics to create on startup, see below       |
| `KAFKA_TOPIC_CONFIG`          | `unset`   | Default config args for created topics       |
| `KAFKA_CREATE_TOPICS_SCRIPT`  | `/kafka/bin/kafka-topics.sh` | Path to script that creates topics |

Topic creation
--------------

This image will create topics automatically on first startup when
`KAFKA_CREATE_TOPICS` is set:

```
docker run \
    --name kafka-init \
    --link zookeeper \
    --link kafka \
    -e KAFKA_CREATE_TOPICS="topic1:64:1,topic2:16:1"
    monasca/kafka-init:latest
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

As an example, this is a valid `KAFKA_CREATE_TOPICS` string for [Monasca][3]
installations as used in the [docker-compose][4] environment:

    metrics:64:1,alarm-state-transitions:12:1,alarm-notifications:12:1,retry-notifications:3:1,events:12:1,60-seconds-notifications:3:1

If desired, default config parameters can be set using `KAFKA_TOPIC_CONFIG`.
These use `key=value,key2=value2` syntax and will be translated into
`--config key=value` arguments as described above. If a duplicate key is passed
in a specific topic string, it will override the value specified here.


[1]: http://semver.org/
[2]: https://github.com/monasca/monasca-docker/tree/master/kafka
[3]: https://hub.docker.com/r/monasca/api/
[4]: https://github.com/monasca/monasca-docker/
