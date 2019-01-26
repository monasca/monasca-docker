monasca-log-metrics
-------------------

**monasca-log-metrics** image contains [Logstash][1] configuration
to transform logs into metrics based on log's severity.

Tags
----

**monasca-log-metrics** uses simple [SemVer][2] tags as follows:

* `0.0.1` - `latest`

Configuration
-------------

| Variable                  |   Default        | Description                        |
|---------------------------|------------------|------------------------------------|
| `ZOOKEEPER_URI`           | `zookeeper:2181` | An URI to Zookeeper server         |
| `KAFKA_URI`               | `kafka:9092`     | The host and port for kafka        |
| `KAFKA_WAIT_FOR_TOPICS`   | `log-transformed,metrics` | Topics to wait on at startup |
| `KAFKA_WAIT_RETRIES`      | `24`             | # of kafka wait attempts           |
| `KAFKA_WAIT_DELAY`        | `5`              | # seconds to wait between attempts |
| `LOG_LEVEL`               | `warning,error,fatal` | List all log levels converted to metrics  |

Usage
-----

In order to run **monasca-log-metrics**:

* [kafka][3] needs to be available
* [zookeeper][4] needs to be available
* `log-transformed` and `metrics` topics needs to be created

After that, **monasca-log-metrics** can be run with:
```docker run -l zookeeper -l kafka monasca/log-metrics```

[1]: https://hub.docker.com/_/logstash/
[2]: http://semver.org/
[3]: https://github.com/monasca/monasca-docker/kafka
[4]: https://hub.docker.com/_/zookeeper
