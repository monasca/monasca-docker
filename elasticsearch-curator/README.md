elasticsearch-curator
=====================

This image provide data retention possibilities for Elasticsearch.

Sources: [elasticsearch-curator][es-cur] &middot; [Dockerfile][es-cur-df] &middot; [monasca-docker][monasca-docker]

Tags
----

Images in this repository are tagged as follows:

 * `latest`: refers to the latest stable point release, e.g. `1.0.0`
 * `4.3.1-1.0.0`: a.k.a. `[elasticsearch-curator version]-[image version]`.
   In this case the image revision `1.0.0` has been built from a snapshot
   of Elasticsearch Curator `4.3.1`

Usage
-----

This image requires access to a running Elasticsearch instance.

If needed, connection parameters can be provided via environment variables as
described below.

Example of configuration for Docker Compose that will delete indices
that are older than 60 days:
```yaml
elasticsearch-curator:
  image: monasca/elasticsearch-curator:latest
  environment:
    CURATOR_DELETE_BY_AGE: 60
    LOGSTASH_FIELDS: "service=elasticsearch-curator"
  depends_on:
    - elasticsearch
```


Configuration
-------------

|           Variable            |       Default        |                        Description                        |
|-------------------------------|----------------------|-----------------------------------------------------------|
| `ELASTICSEARCH_URI`           | `elasticsearch:9200` | URI to connect to ES                                      |
| `CURATOR_LOG_LEVEL`           | `INFO`               | Curator log level                                         |
| `CURATOR_CRON`                | `0 0 * * *`          | Cron run time configuration                               |
| `CURATOR_EXCLUDED_INDEX_NAME` | ``                   | Index that will be excluded from deleting                 |
| `CURATOR_DELETE_BY_AGE`       | ``                   | Delete indices older than this number of days (e.g. `60`) |
| `CURATOR_DELETE_BY_SPACE`     | ``                   | Delete oldest indices over number of GB                   |

By default Elasticsearch Curator is running thanks to cron every day
at 12 a.m.. You could get more information how to set it to different time
at <http://corntab.com>.


Actions configuration
---------------------

You are able to configure Elasticsearch Curator to delete oldest data
by `age` and/or `space`. For example to delete indices older than 60 days
or bigger than 5 GB set both variables:

```
CURATOR_DELETE_BY_AGE: 60
CURATOR_DELETE_BY_SPACE: 5
```

`CURATOR_DELETE_BY_SPACE` could contain number smaller than `1`, like `0.05`.

You can exclude specific index from processing with `CURATOR_EXCLUDED_INDEX_NAME`:

`CURATOR_EXCLUDED_INDEX_NAME: .kibana`


[es-cur]: https://github.com/monasca/monasca-docker/blob/master/elasticsearch-curator/
[es-cur-df]: https://github.com/monasca/monasca-docker/blob/master/elasticsearch-curator/Dockerfile
[monasca-docker]: https://github.com/monasca/monasca-docker/
