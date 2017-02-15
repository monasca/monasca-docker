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
| `KAFKA_AUTO_CREATE_TOPICS`    | `true`  | Enable automatic topic creation                |
| `KAFKA_DELETE_TOPIC_ENABLE`   | `false` | Enable topic deletion                          |
| `KAFKA_LISTEN_PORT`           | `9092`  | Port for Kafka to listen on                    |
| `KAFKA_ADVERTISED_PORT`       | `$KAFKA_LISTEN_PORT` | Kafka port advertised to clients  |
| `KAFKA_CONTROLLED_SHUTDOWN_ENABLE` | `true` | If `true`, enable [controlled shutdown][6] |
| `KAFKA_JMX`                   | unset   | If `true`, expose JMX metrics over TCP         |
| `KAFKA_JMX_PORT`              | `7203`  | Port to expose JMX metrics                     |
| `KAFKA_JMX_OPTS`              | no SSL/auth, etc | Override default opts                 |


JMX
---

Remote JMX access can be a bit of a pain to set up. The start script for this
container tries to make it as painless as possible, but it's important to
understand that if you want to connect a client like VisualVM from outside other
Docker containers (e.g. directly from your host OS in development), then you'll
need to configure RMI to be addressed *as the Docker host IP or hostname*. If
you have set `KAFKA_ADVERTISED_HOST_NAME`, that value will be used and is
probably what you want. If not (you're only using other containers to talk to
Kafka brokers) or you need to override it for some reason, then you can instead
set `JAVA_RMI_SERVER_HOSTNAME`.

For example in practice, if your Docker host is VirtualBox run by Docker
Machine, a `run` command like this should allow you to connect VisualVM from
your host OS to `$(docker-machine ip docker-vm):7203`:

    $ docker run -d --name kafka -p 7203:7203 \
        --link zookeeper:zookeeper \
        --env JAVA_RMI_SERVER_HOSTNAME=$(docker-machine ip docker-vm) \
        ches/kafka

Note that it is fussy about port as well---it may not work if the same port
number is not used within the container and on the host (any advice for
workarounds is welcome).

Finally, please note that by default remote JMX has authentication and SSL
turned off (these settings are taken from Kafka's own default start scripts). If
you expose the JMX hostname/port from the Docker host in a production
environment, you should make make certain that access is locked down
appropriately with firewall rules or similar. A more advisable setup in a Docker
setting would be to run a metrics collector in another container, and link it to
the Kafka container(s).

If you need finer-grained configuration, you can totally control the relevant
Java system properties by setting `KAFKA_JMX_OPTS` yourself---see `start.sh`.

[1]: http://kafka.apache.org/
[2]: https://github.com/hpcloud-mon/monasca-docker/blob/master/kafka/
[3]: https://github.com/hpcloud-mon/monasca-docker/blob/master/kafka/Dockerfile
[4]: https://github.com/hpcloud-mon/monasca-docker/
[5]: https://hub.docker.com/r/library/zookeeper/
[6]: https://kafka.apache.org/documentation/#basic_ops_restarting
[7]: https://github.com/wurstmeister/kafka-docker

[Docker]: http://www.docker.io
[on the Docker registry]: https://registry.hub.docker.com/u/ches/kafka/
[relateiq/kafka]: https://github.com/relateiq/docker-kafka
