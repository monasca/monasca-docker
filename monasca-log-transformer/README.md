monasca-log-transformer
-----------------------

**monasca-log-transformer** image contains [Logstash][1] configuration
to detect log's severity.

Tags
----

**monasca-log-transformer** uses simple [SemVer][2] tags as follows:

* `0.0.1` - `latest`

Configuration
-------------

| Variable                  |   Default        | Description                        |
|---------------------------|------------------|------------------------------------|
| `ZOOKEEPER_URI`           | `zookeeper:2181` | An URI to Zookeeper server         |
| `KAFKA_URI`               | `kafka:9092`     | The host and port for kafka        |
| `KAFKA_WAIT_FOR_TOPICS`   | `log-transformed,log` | Topics to wait on at startup |
| `KAFKA_WAIT_RETRIES`      | `24`             | # of kafka wait attempts           |
| `KAFKA_WAIT_DELAY`        | `5`              | # seconds to wait between attempts |

Usage
-----

In order to run **monasca-log-transformer**:

* [kafka][3] needs to be available
* [zookeeper][4] needs to be available
* `log-transformed` and `log` topics needs to be created

After that, **monasca-log-transformer** can be run with:
```docker run -l zookeeper -l kafka monasca/log-transformer```

[1]: https://hub.docker.com/_/logstash/
[2]: http://semver.org/
[3]: https://github.comonasca/monasca-docker/kafka
[4]: https://hub.docker.com/_/zookeeper
