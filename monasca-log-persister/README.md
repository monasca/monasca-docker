monasca-log-persister
---------------------

**monasca-log-persister** image contains [Logstash][1] configuration
to save logs inside **log-db** (i.e. [ElasticSearch][5])

Tags
----

**monasca-log-persister** uses simple [SemVer][2] tags as follows:

* `0.0.1` - `latest`

Configuration
-------------

| Variable                   | Default           | Description                         |
|----------------------------|-------------------|-------------------------------------|
| `ZOOKEEPER_URI`            | `zookeeper:2181`  | An URI to Zookeeper server          |
| `KAFKA_WAIT_FOR_TOPICS`    | `log-transformed` | Topics to wait on at startup        |
| `ELASTICSEARCH_HOST`       | `elasticsearch`   | Comma delimited ElasticSearch hosts |
| `ELASTICSEARCH_PORT`       | `9200`            | Port of ElasticSearch               |
| `ELASTICSEARCH_TIMEOUT`    | `60`              | How long to wait for ElasticSearch  |
| `ELASTICSEARCH_FLUSH_SIZE` | `600`             | See [flush_size][6]                 |
| `ELASTICSEARCH_IDLE_FLUSH_TIME` | `60`         | See [idle_flush_time][7]            |
| `ELASTICSEARCH_INDEX`      | `%{tenant}-%{index_date}` | See [index][8]              |
| `ELASTICSEARCH_DOC_TYPE`   | `logs`            | See [document_type][9]              |
| `ELASTICSEARCH_SNIFFING`   | `true`            | See [sniffing][10]                  |
| `ELASTICSEARCH_SNIFFING_DELAY` | `5`           | See [sniffing_delay][11]            |

Usage
-----

In order to run **monasca-log-persister**:

* [kafka][3] needs to be available
* [zookeeper][4] needs to be available
* [elasticsearch][5] needs to be available
* `log-transformed` topic needs to be created

After that, **monasca-log-persister** can be run with:
```docker run -l zookeeper -l kafka -l elasticsearch monasca/log-persister```

[1]: https://hub.docker.com/_/logstash/
[2]: http://semver.org/
[3]: https://github.comonasca/monasca-docker/kafka
[4]: https://hub.docker.com/_/zookeeper
[5]: https://hub.docker.com/_/elasticsearch
[6]: https://www.elastic.co/guide/en/logstash/2.4/plugins-outputs-elasticsearch.html#plugins-outputs-elasticsearch-flush_size
[7]: https://www.elastic.co/guide/en/logstash/2.4/plugins-outputs-elasticsearch.html#plugins-outputs-elasticsearch-idle_flush_time
[8]: https://www.elastic.co/guide/en/logstash/2.4/plugins-outputs-elasticsearch.html#plugins-outputs-elasticsearch-index
[9]: https://www.elastic.co/guide/en/logstash/2.4/plugins-outputs-elasticsearch.html#plugins-outputs-elasticsearch-document_type
[10]: https://www.elastic.co/guide/en/logstash/2.4/plugins-outputs-elasticsearch.html#plugins-outputs-elasticsearch-sniffing
[11]: https://www.elastic.co/guide/en/logstash/2.4/plugins-outputs-elasticsearch.html#plugins-outputs-elasticsearch-sniffing_delay
